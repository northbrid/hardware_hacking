#!/usr/bin/env python3
"""
Wrapper for whsniff (https://github.com/homewsn/whsniff) on Zigbee 2.4 GHz channels 11–26.

Why this exists: whsniff writes a valid pcap *stream* to stdout, but on some errors it also
prints lines like "ERROR: LIBUSB_ERROR_..." to stdout (see whsniff.c), which would corrupt a
redirection. This script only forwards complete pcap records to the file and logs errors
separately. On whsniff restart, the duplicate 24-byte pcap file header is skipped so one capture
stays a single valid pcap with consecutive packets (modulo a single truncated record on crash; we
only commit complete records).

PCAP note: a savefile has a one-time global header (24 bytes) then a sequence of
(16-byte record header + `incl_len` bytes of packet). If a process dies after writing a partial
record, that file is truncated after the last *complete* record; an incomplete last record is
not written.

Usage:
  Find activity: wait for the first frame on each channel (or timeout), one pcap per channel;
  repeats 11–26 forever (Ctrl+C to stop), appending new frames to the same pcap per channel:
    ./whsniff_zigbee.py -o recording-1 -d 45000
  Creates recording-1-11.pcap … (prefix from -o, default is whsniff_rec). Stdout: line 1 = channel
  IDs, line 2 = per-round live counts with “>” under the active channel.

  Capture on one channel, restart on whsniff exit, append valid pcap only:
    ./whsniff_zigbee.py -c 15 -o cap.pcap

  Path to whsniff (default: WHSNIFF env, else "whsniff" on PATH):
    WHSNIFF=/path/to/whsniff ./whsniff_zigbee.py -c 18

  See also:
    ./whsniff_zigbee.py -c 18 --diagnostic
    ./whsniff_zigbee.py -c 18 --diagnostic --diagnostic-seconds 30

  Notes (whsniff.c): Before capture, some messages go to stderr; during capture, libusb errors
  are printf'd to *stdout* after the pcap file header, so a raw ">" redirect can corrupt a pcap.
  This tool strips those ERROR lines and only writes full pcap records. A pcap is a global header
  plus whole records (16-byte header + incl_len); whsniff emits complete records per packet, so
  you will not get a half-record from the sniffer in normal operation—only a truncated file if
  the wrapper wrote a partial record, which this script avoids.
"""

from __future__ import annotations

import argparse
import os
import select
import struct
import subprocess
import sys
import time
from dataclasses import dataclass, field
from typing import BinaryIO, Callable, Optional, Tuple

# Native-order magic from whsniff (see whsniff.c pcap_hdr)
PCAP_MAGIC_LE = 0xA1B2C3D4
PCAP_MAGIC_BE = 0xD4C3B2A1
PCAP_FILE_HDR_SIZE = 24
PCAP_REC_HDR_SIZE = 16


def pcap_le_global_header_802_15_4() -> bytes:
    """Empty capture file header, same as whsniff (snaplen 128, DLT 195 = IEEE 802.15.4)."""
    return struct.pack(
        "<IHHiIII",
        0xA1B2C3D4,
        2,
        4,
        0,
        0,
        128,
        195,
    )


@dataclass
class PcapState:
    """Buffer incoming bytes and emit pcap file header + full records (callback per record)."""

    buf: bytearray = field(default_factory=bytearray)
    seen_file_header: bool = False
    # After first file header, apply skip_header to subsequent invocations of the child (restart).
    want_skip_global_header: bool = False
    # If True, do not log when skipping a repeated 24B header (avoids spamming the scan-mode TTY UI).
    quiet_skip_header: bool = False

    def _take(self, n: int) -> bytes:
        if len(self.buf) < n:
            return b""
        out = bytes(self.buf[:n])
        del self.buf[:n]
        return out

    def _consume_error_lines(self, log: Callable[[str], None]) -> None:
        # whsniff prints e.g. "ERROR: LIBUSB_ERROR_IO.\n" to *stdout* after capture starts
        while self.buf.startswith(b"ERROR:"):
            nl = self.buf.find(b"\n", 0)
            if nl < 0:
                return
            line = self.buf[: nl + 1].decode("ascii", errors="replace").rstrip()
            del self.buf[: nl + 1]
            log(line)

    def feed(
        self,
        data: bytes,
        on_file_header: Optional[Callable[[bytes], None]],
        on_record: Callable[[bytes, bytes], None],
        log: Callable[[str], None],
    ) -> None:
        self.buf.extend(data)
        while self.buf:
            self._consume_error_lines(log)
            if not self.buf:
                break
            if self.want_skip_global_header:
                if len(self.buf) < PCAP_FILE_HDR_SIZE:
                    return
                magic = struct.unpack_from("<I", self.buf, 0)[0]
                if magic in (PCAP_MAGIC_LE, PCAP_MAGIC_BE):
                    self._take(PCAP_FILE_HDR_SIZE)
                    self.want_skip_global_header = False
                    # Stream is now aligned on packet records (same as after first global header).
                    self.seen_file_header = True
                    if not self.quiet_skip_header:
                        log("Skipping duplicate pcap global header (whsniff restart).")
                else:
                    if self.buf.startswith(b"ERROR:"):
                        continue
                    del self.buf[0]
                continue

            if not self.seen_file_header:
                self._consume_error_lines(log)
                if not self.buf:
                    break
                if len(self.buf) < PCAP_FILE_HDR_SIZE:
                    return
                magic = struct.unpack_from("<I", self.buf, 0)[0]
                if magic in (PCAP_MAGIC_LE, PCAP_MAGIC_BE):
                    hdr = self._take(PCAP_FILE_HDR_SIZE)
                    self.seen_file_header = True
                    if on_file_header:
                        on_file_header(hdr)
                else:
                    del self.buf[0]
                continue

            if len(self.buf) < PCAP_REC_HDR_SIZE:
                return
            if self.buf.startswith(b"ERROR:"):
                continue
            _ts, _tus, incl_len, orig_len = struct.unpack_from(
                "<IIII", self.buf, 0
            )
            if (
                incl_len == 0
                or orig_len == 0
                or incl_len > 2048
                or orig_len > 2048
            ):
                del self.buf[0]
                log("Dropping 1 byte to resync pcap (implausible record length).")
                continue
            need = PCAP_REC_HDR_SIZE + incl_len
            if len(self.buf) < need:
                return
            rec_hdr = self._take(PCAP_REC_HDR_SIZE)
            pkt = self._take(incl_len)
            on_record(rec_hdr, pkt)

    def reset_for_new_stream(self) -> None:
        """Call when a new whsniff process starts: next global header can be skipped."""
        self.buf.clear()
        if self.seen_file_header:
            self.want_skip_global_header = True


def _default_which() -> str:
    return os.environ.get("WHSNIFF", "whsniff")


def _read_which_stdout_stderr(
    cmd: list[str], duration: float, log: Callable[[str], None]
) -> None:
    """Run whsniff until it fails, logging stderr and a note about stdout (for diagnostics)."""
    t0 = time.monotonic()
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    err_chunks: list[bytes] = []
    out_len = 0

    def drain_stderr() -> None:
        if proc.stderr and proc.stderr.readable():
            try:
                data = os.read(proc.stderr.fileno(), 65536)
                if data:
                    err_chunks.append(data)
            except (BlockingIOError, OSError):
                pass

    while True:
        elapsed = time.monotonic() - t0
        if duration > 0 and elapsed >= duration:
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
            break
        rlist: list = []
        if proc.stdout:
            rlist.append(proc.stdout)
        if proc.stderr:
            rlist.append(proc.stderr)
        r, _, _ = select.select(rlist, [], [], 0.2)
        for fd in r:
            if proc.stdout and fd is proc.stdout:
                b = os.read(proc.stdout.fileno(), 65536) if proc.stdout else b""
                if b:
                    out_len += len(b)
            if proc.stderr and fd is proc.stderr:
                b = os.read(proc.stderr.fileno(), 65536)
                if b:
                    err_chunks.append(b)
        if proc.poll() is not None:
            # Drain rest
            if proc.stdout:
                b = proc.stdout.read()
                if b:
                    out_len += len(b)
            if proc.stderr:
                b = proc.stderr.read()
                if b:
                    err_chunks.append(b)
            break
    err = b"".join(err_chunks).decode("utf-8", errors="replace")
    log("--- whsniff diagnostic run (stdout=binary pcap+errors, size=%d bytes) ---" % out_len)
    if err.strip():
        log("--- stderr (device open etc.) ---\n" + err.rstrip() + "\n")
    else:
        log("--- (no stderr) ---")


def _format_scan_table(
    chans: list[int],
    counts: dict[int, int],
    current: Optional[int],
    round_n: int,
) -> Tuple[str, str]:
    """
    Line 1: # | ch… | Σ   (fixed widths so ANSI line-2 updates stay aligned)
    Line 2: round id and counts are zero-padded; active channel: >0… | Σ total
    """
    w_rnd = 3
    w_ch = 4
    w_sum = 3
    pad = 1
    sep = " " * pad

    def zfit(n: int, width: int) -> str:
        """Up to `width` digit characters, right-aligned with leading zeros (truncates on overflow)."""
        s = str(n)
        if len(s) > width:
            s = s[-width:]
        return s.rjust(width, "0")

    def fmt_head(s: str, w: int) -> str:
        if len(s) > w:
            s = s[:w]
        return s.center(w)

    def fmt_round_id(n: int) -> str:
        return zfit(n, w_rnd)

    def fmt_channel_count(ch: int, n: int) -> str:
        n = int(n)
        is_active = ch == current
        d = w_ch - 1
        num = zfit(n, d)
        return (">" if is_active else " ") + num

    h0 = fmt_head("#", w_rnd)
    h_mid = [fmt_head(f"{c}", w_ch) for c in chans]
    h_end = fmt_head("Σ", w_sum)
    line1 = sep.join([h0] + h_mid + [h_end])

    total = int(sum(int(counts.get(c, 0)) for c in chans))
    st = zfit(total, w_sum)
    c0 = fmt_round_id(round_n)
    cells2 = [fmt_channel_count(c, counts.get(c, 0) or 0) for c in chans]
    line2 = sep.join([c0] + cells2 + [st])
    return line1, line2


def _file_write(f: BinaryIO, data: bytes) -> None:
    f.write(data)
    f.flush()


def _run_scan_wait_first(
    whsniff: str,
    output_prefix: str,
    per_channel_timeout_ms: float,
    first_channel: int,
    last_channel: int,
    log: Callable[[str], None],
) -> None:
    if first_channel < 11 or last_channel > 26 or first_channel > last_channel:
        print("Channel range must be 11..26 and low<=high", file=sys.stderr)
        sys.exit(2)
    per_channel_wait_sec = max(0.0, per_channel_timeout_ms) / 1000.0
    chans = list(range(first_channel, last_channel + 1))
    counts: dict[int, int] = {c: 0 for c in chans}
    current_ch: Optional[int] = None
    round_n = 0
    # Set True only right before refresh after a new packet; controls \n vs \r for the data row.
    data_row_end_newline = [False]
    header_printed = [False]

    def refresh_status() -> None:
        l1, l2 = _format_scan_table(
            chans, counts, current_ch, round_n
        )
        if not header_printed[0]:
            print(l1, file=sys.stdout)
            header_printed[0] = True
        use_nl = data_row_end_newline[0]
        data_row_end_newline[0] = False
        print(l2, end="\n" if use_nl else "\r", flush=True)

    log(
        f"Each channel: up to {per_channel_timeout_ms:.0f} ms for the first frame; cycles "
        f"{first_channel}–{last_channel} forever (Ctrl+C). Appends to "
        f'"{output_prefix}-<ch>.pcap. Header once on stdout, then data row only (\\r / \\n); logs on stderr.'
    )
    try:
        while True:
            round_n += 1
            current_ch = None
            refresh_status()
            for ch in chans:
                current_ch = ch
                refresh_status()
                pcap_path = f"{output_prefix}-{ch}.pcap"
                channel_deadline = time.monotonic() + per_channel_wait_sec
                got_packet = [False]
                existing = (
                    os.path.exists(pcap_path) and os.path.getsize(pcap_path) > 0
                )
                pcap_f: BinaryIO = open(pcap_path, "ab", buffering=0)
                pcap_f_has_header = existing
                st = PcapState(quiet_skip_header=True)
                if pcap_f_has_header:
                    st.want_skip_global_header = True

                def on_file_header(hdr: bytes) -> None:
                    nonlocal pcap_f_has_header
                    if pcap_f_has_header:
                        return
                    _file_write(pcap_f, hdr)
                    pcap_f_has_header = True

                def on_record(rec_hdr: bytes, pkt: bytes) -> None:
                    if got_packet[0]:
                        return
                    _file_write(pcap_f, rec_hdr + pkt)
                    got_packet[0] = True
                    counts[ch] = int(counts.get(ch, 0)) + 1
                    data_row_end_newline[0] = True
                    refresh_status()

                def drain_err(proc: subprocess.Popen) -> None:
                    if not proc.stderr:
                        return
                    if not select.select([proc.stderr], [], [], 0.0)[0]:
                        return
                    data = os.read(proc.stderr.fileno(), 8192)
                    if not data:
                        return
                    for line in data.decode("utf-8", errors="replace").splitlines():
                        if line.strip():
                            log("[whsniff stderr] " + line)

                def stop_proc(p: subprocess.Popen) -> None:
                    if p.poll() is not None:
                        return
                    p.terminate()
                    try:
                        p.wait(timeout=2.0)
                    except subprocess.TimeoutExpired:
                        p.kill()
                        try:
                            p.wait(timeout=1.0)
                        except (subprocess.TimeoutExpired, OSError):
                            pass

                try:
                    while (not got_packet[0]) and time.monotonic() < channel_deadline:
                        if pcap_f_has_header:
                            st = PcapState(quiet_skip_header=True)
                            st.want_skip_global_header = True
                        else:
                            st = PcapState(quiet_skip_header=True)
                        cmd = [whsniff, "-c", str(ch)]
                        proc = subprocess.Popen(
                            cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                        )
                        if proc.stdout is None or proc.stderr is None:
                            time.sleep(0.3)
                            continue
                        while (
                            proc.poll() is None
                            and (not got_packet[0])
                            and time.monotonic() < channel_deadline
                        ):
                            tleft = channel_deadline - time.monotonic()
                            if tleft <= 0:
                                break
                            w = min(0.25, tleft)
                            r, _, _ = select.select(
                                [proc.stdout, proc.stderr], [], [], w
                            )
                            for s in r:
                                if s is proc.stdout and proc.stdout:
                                    b = os.read(proc.stdout.fileno(), 65536)
                                    if b:
                                        st.feed(
                                            b, on_file_header, on_record, log
                                        )
                                elif proc.stderr and s is proc.stderr:
                                    drain_err(proc)
                        # If whsniff is still running, never call read() to EOF: it would block
                        # forever. Stop the process first, then drain.
                        stop_proc(proc)
                        if proc.stdout:
                            rest = proc.stdout.read() or b""
                            if rest:
                                st.feed(rest, on_file_header, on_record, log)
                        if proc.stderr:
                            rest2 = proc.stderr.read() or b""
                            if rest2:
                                for line in rest2.decode(
                                    "utf-8", errors="replace"
                                ).splitlines():
                                    if line.strip():
                                        log("[whsniff stderr] " + line)
                finally:
                    if (not pcap_f_has_header) and (not got_packet[0]):
                        _file_write(pcap_f, pcap_le_global_header_802_15_4())
                    pcap_f.close()

    except KeyboardInterrupt:
        log("Stopped by user (Ctrl+C).")
    current_ch = None
    data_row_end_newline[0] = True
    refresh_status()
    print(file=sys.stdout)



def _run_capture(
    whsniff: str,
    channel: int,
    pcap_path: str,
    log: Callable[[str], None],
) -> None:
    if channel < 11 or channel > 26:
        print("Channel must be 11–26", file=sys.stderr)
        sys.exit(2)

    pcap_f = open(pcap_path, "ab", buffering=0)
    pcap_f_has_header = os.path.getsize(pcap_path) > 0
    n_packets = 0
    total_cap_bytes = 0  # sum of incl_len
    st = PcapState()
    if pcap_f_has_header:
        # Next whsniff process will re-emit 24B global header; we skip that and append records only.
        st.want_skip_global_header = True

    def on_file_header(hdr: bytes) -> None:
        nonlocal pcap_f_has_header
        if pcap_f_has_header:
            return
        _file_write(pcap_f, hdr)
        pcap_f_has_header = True
        log("Wrote pcap global header.")

    def on_record(rec_hdr: bytes, pkt: bytes) -> None:
        nonlocal n_packets, total_cap_bytes, pcap_f_has_header
        incl = struct.unpack_from("<IIII", rec_hdr, 0)[2]
        _file_write(pcap_f, rec_hdr + pkt)
        n_packets += 1
        total_cap_bytes += incl
        # One line per packet, updated totals
        print(
            f"packet {n_packets}: size={incl} bytes, total={total_cap_bytes} bytes (all packets so far)"
        )
        sys.stdout.flush()

    log(f"Capturing to {pcap_path!r} on channel {channel} (Ctrl+C to stop).")
    log("Restarts the sniffer on exit; pcap only receives complete records, errors go to this log only.")

    try:
        while True:
            cmd = [whsniff, "-c", str(channel)]
            st.reset_for_new_stream()
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            if proc.stdout is None:
                raise RuntimeError("failed to open whsniff stdout")
            if proc.stderr is None:
                raise RuntimeError("failed to open whsniff stderr")

            def log_err(data: str) -> None:
                for line in data.splitlines():
                    if line.strip():
                        log("[whsniff stderr] " + line)

            def feed_err() -> None:
                if select.select([proc.stderr], [], [], 0.0)[0]:
                    b = os.read(proc.stderr.fileno(), 8192)
                    if b:
                        log_err(b.decode("utf-8", errors="replace"))

            while proc.poll() is None:
                r, _, _ = select.select([proc.stdout, proc.stderr], [], [], 0.25)
                for s in r:
                    if s is proc.stdout:
                        b = os.read(proc.stdout.fileno(), 65536)
                        if b:
                            st.feed(
                                b,
                                on_file_header,
                                on_record,
                                log,
                            )
                    if s is proc.stderr:
                        feed_err()
            # proc ended: drain
            b = (proc.stdout.read() or b"") if proc.stdout else b""
            if b:
                st.feed(b, on_file_header, on_record, log)
            if proc.stderr:
                rest = proc.stderr.read() or b""
                if rest:
                    log_err(rest.decode("utf-8", errors="replace"))
            code = proc.returncode or 0
            log(
                f"whsniff exited (code {code}). Restarting in 0.3s (same pcap) …"
            )
            time.sleep(0.3)
    except KeyboardInterrupt:
        log("Stopped by user.")
    finally:
        pcap_f.close()


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Zigbee channel scan and robust whsniff→pcap capture (filters stdout errors).",
    )
    ap.add_argument(
        "--whsniff",
        default=_default_which(),
        help="Path to whsniff binary (default: $WHSNIFF or 'whsniff')",
    )
    ap.add_argument(
        "-c",
        "--channel",
        type=int,
        default=None,
        metavar="N",
        help="If set, listen on this Zigbee channel (11–26) and save pcap; if omitted, scan 11–26.",
    )
    ap.add_argument(
        "-d",
        "--duration",
        type=float,
        default=60_000.0,
        metavar="MS",
        help="Scan mode: max milliseconds to wait for the *first* frame on each channel (default: 60000 = 60 s)",
    )
    ap.add_argument(
        "-o",
        "--output",
        default=None,
        help='Without -c: output filename *prefix* (e.g. "recording-1" → recording-1-11.pcap, …). '
        "With -c: pcap file path (default: whsniff_capture.pcap).",
    )
    ap.add_argument(
        "--first",
        type=int,
        default=11,
        help="First channel in scan mode (default: 11)",
    )
    ap.add_argument(
        "--last",
        type=int,
        default=26,
        help="Last channel in scan mode (default: 26)",
    )
    ap.add_argument(
        "--diagnostic",
        action="store_true",
        help="Run whsniff until it fails; print stderr and stdout byte count (no pcap).",
    )
    ap.add_argument(
        "--diagnostic-seconds",
        type=float,
        default=0.0,
        help="Optional max seconds for --diagnostic (0 = no limit)",
    )

    args = ap.parse_args()
    wh = args.whsniff

    def log(msg: str) -> None:
        print(msg, file=sys.stderr)
        sys.stderr.flush()

    if args.diagnostic:
        if args.channel is None:
            print("Use -c for diagnostic run (need a channel).", file=sys.stderr)
            sys.exit(2)
        cmd = [wh, "-c", str(args.channel)]
        log("Running: " + " ".join(cmd))
        _read_which_stdout_stderr(
            cmd, args.diagnostic_seconds, log
        )
        return

    if args.channel is not None:
        out = args.output or "whsniff_capture.pcap"
        _run_capture(wh, args.channel, out, log)
    else:
        prefix = args.output or "whsniff_rec"
        _run_scan_wait_first(wh, prefix, args.duration, args.first, args.last, log)


if __name__ == "__main__":
    main()
