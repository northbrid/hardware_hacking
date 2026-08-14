#!/bin/bash
set -euo pipefail

# --- Configuration (edit these) ---

# Physical Ethernet interface
PARENT_IF="${PARENT_IF:-eth0}"

# Subnet base (first three octets)
SUBNET_BASE="${SUBNET_BASE:-172.16.0}"

# First and last host octet to simulate (inclusive)
IP_START="${IP_START:-151}"
IP_END="${IP_END:-250}"

# macvlan mode: bridge works well on a flat LAN/switch
MACVLAN_MODE="${MACVLAN_MODE:-bridge}"

# Prefix for virtual interface names
IF_PREFIX="${IF_PREFIX:-simdev}"

# salt for generating MAC addresses
MAC_SALT="${MAC_SALT:-STEMsisters}"

# --- Helpers ---
die() {
    echo "ERROR: $*" >&2
    exit 1
}

require_root() {
    [[ "${EUID:-$(id -u)}" -eq 0 ]] || die "Run as root (sudo)."
}

require_ip() {
    command -v ip >/dev/null 2>&1 || die "'ip' command not found. Install iproute2."
}

validate_config() {
    [[ "$IP_START" -ge 1 && "$IP_START" -le 254 ]] || die "IP_START must be 1-254"
    [[ "$IP_END" -ge 1 && "$IP_END" -le 254 ]] || die "IP_END must be 1-254"
    [[ "$IP_START" -le "$IP_END" ]] || die "IP_START must be <= IP_END"

    ip link show "$PARENT_IF" >/dev/null 2>&1 \
        || die "Parent interface '$PARENT_IF' not found"
}

# Generate a locally-administered unicast MAC from host octet
# Format: 02:00:00:00:00:XX  (up to 254 devices with unique last octet)
mac_for_host_old() {
    local host="$1"
    printf "02:00:00:00:00:%02x" "$host"
}

# Generates a randomly-looking but deterministic MAC address for IP
# So my students can't easily distinguish the generated ones from the outlier
mac_for_host() {
    local host="$1"
    local ip="$(ip_for_host "$host")"
    local input="${MAC_SALT}:${ip}:${host}"

    local hash
    hash=$(printf '%s' "$input" | md5sum | awk '{print $1}')

    printf "%02x:%02x:%02x:%02x:%02x:%02x" \
	$(( (0x${hash:0:2}  & 0xfc) | 0x02 )) \
	$((  0x${hash:2:2} )) \
	$((  0x${hash:4:2} )) \
	$((  0x${hash:6:2} )) \
	$((  0x${hash:8:2} )) \
	$((  0x${hash:10:2} ))
}

iface_for_host() {
    local host="$1"
    echo "${IF_PREFIX}${host}"
}

ip_for_host() {
    local host="$1"
    echo "${SUBNET_BASE}.${host}"
}

write_proc_sys() {
    local key="$1"
    local value="$2"
    local path="/proc/sys/${key//./\/}"

    if [[ -w "$path" ]]; then
        echo "$value" > "$path"
    else
        echo "WARNING: cannot write $path" >&2
    fi
}

tune_sysctl() {
    write_proc_sys net.ipv4.conf.all.rp_filter 0
    write_proc_sys "net.ipv4.conf.${PARENT_IF}.rp_filter" 0
    write_proc_sys "net.ipv4.conf.${PARENT_IF}.proxy_arp" 0
    write_proc_sys "net.ipv4.conf.${PARENT_IF}.arp_ignore" 1
    write_proc_sys "net.ipv4.conf.${PARENT_IF}.arp_announce" 2
}

create_device() {
    local host="$1"
    local iface mac ip

    iface="$(iface_for_host "$host")"
    mac="$(mac_for_host "$host")"
    ip="$(ip_for_host "$host")"
    
    ip link add link "$PARENT_IF" name "$iface" type macvlan mode "$MACVLAN_MODE"
    ip link set "$iface" address "$mac"
    ip addr add "${ip}/32" dev "$iface"
    ip link set "$iface" up

    write_proc_sys "net.ipv4.conf.${iface}.proxy_arp" 0
    write_proc_sys "net.ipv4.conf.${iface}.arp_ignore" 1
    write_proc_sys "net.ipv4.conf.${iface}.arp_announce" 2

    echo "- created $iface  mac=$mac  ip=$ip"
}

require_root
require_ip
validate_config
tune_sysctl

echo "Creating simulated devices on $PARENT_IF ($IP_START..$IP_END)..."

for host in $(seq "$IP_START" "$IP_END"); do
    create_device "$host"
done
