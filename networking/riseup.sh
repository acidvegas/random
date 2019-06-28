#!/bin/bash

DEFAULT_PORT=0
DEFAULT_PROTOCOL=0
DISABLE_IPV6=1
ENABLE_KILLSWITCH=0

function disable_ipv6 {
	if [ ! -f /etc/sysctl.d/99-vpn-disable-ipv6.conf ]; then
		echo "net.ipv6.conf.all.disable_ipv6=1" > /etc/sysctl.d/99-vpn-disable-ipv6.conf
		echo "net.ipv6.conf.default.disable_ipv6=1" >> /etc/sysctl.d/99-vpn-disable-ipv6.conf
		echo "net.ipv6.conf.lo.disable_ipv6=1" >> /etc/sysctl.d/99-vpn-disable-ipv6.conf
		sysctl -w net.ipv6.conf.all.disable_ipv6=1
		sysctl -w net.ipv6.conf.default.disable_ipv6=1
		sysctl -w net.ipv6.conf.lo.disable_ipv6=1
	fi
}

function generate_config {
	if [ $DEFAULT_PORT == 0 ]; then
		CHOICE=$(dialog --clear --backtitle "RiseUp VPN Helper" --title "Connection" --menu "Select a connection port:" 20 60 20 1 "1194 (Recommended)" 2 "80" 3 "443" 2>&1 >/dev/tty)
		clear
	else
		CHOICE=$DEFAULT_PORT
	fi
	case $CHOICE in
		1) PROTO="1194";;
		2) PROTO="80";;
		3) PROTO="443";;
	esac
	if [ $DEFAULT_PROTOCOL == 0 ]; then
		CHOICE=$(dialog --clear --backtitle "RiseUp VPN Helper" --title "Connection" --menu "Select a connection protocol:" 20 60 20 1 "UDP (Recommended)" 2 "TCP" 2>&1 >/dev/tty)
		clear
	else
		CHOICE=$DEFAULT_PROTOCOL
	fi
	case $CHOICE in
		1) PROTO="udp";;
		2) PROTO="tcp";;
	esac
	echo "auth SHA256
auth-user-pass auth
ca ca.pem
cipher AES-256-CBC
client
comp-lzo
dev tun0
down /etc/openvpn/scripts/update-systemd-resolved
down-pre
group vpn
iproute /usr/local/sbin/unpriv-ip
mute 3
nobind
persist-key
persist-tun
proto $PROTO
remote vpn.riseup.net $PORT
remote-cert-tls server
reneg-sec 0
resolv-retry infinite
script-security 2
setenv PATH /usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
tls-client
tls-version-min 1.2
up /etc/openvpn/scripts/update-systemd-resolved
user vpn
verb 4" > /etc/openvpn/client/riseup/riseup.conf
}

function killswitch {
	if [ -f /etc/iptables/vpn-rules.v4 ]; then
		iptables-restore < /etc/iptables/vpn-rules.v4
	else
		iptables -F
		iptables -X
		iptables -Z
		iptables -t filter -F
		iptables -t filter -X
		iptables -t mangle -F
		iptables -t mangle -X
		iptables -t nat -F
		iptables -t nat -X
		iptables -t raw -F
		iptables -t raw -X
		iptables -t security -F
		iptables -t security -X
		iptables -P OUTPUT  DROP
		iptables -P INPUT   DROP
		iptables -P FORWARD DROP
		iptables -A INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
		iptables -A INPUT -i lo -j ACCEPT
		iptables -A INPUT -i tun+ -j ACCEPT
		iptables -A OUTPUT -o lo -j ACCEPT
		iptables -A OUTPUT -d 172.27.0.1 -j ACCEPT
		iptables -A OUTPUT -p -m --dport -j ACCEPT
		iptables -A OUTPUT -o tun+ -j ACCEPT
		iptables -A INPUT -s 192.168.1.0/24 -j ACCEPT
		iptables -A OUTPUT -d 192.168.1.0/24 -j ACCEPT
		iptables -A OUTPUT -j REJECT --reject-with icmp-net-unreachable
		iptables-save > /etc/iptables/vpn-rules.v4
	fi
	if [ $DISABLE_IPV6 -eq 1 ]; then
		if [ -f /etc/iptables/vpn-rules.v6 ]; then
			ip6tables-restore < /etc/iptables/vpn-rules.v6
		else
			ip6tables -F
			ip6tables -X
			ip6tables -Z
			ip6tables -t filter -F
			ip6tables -t filter -X
			ip6tables -t mangle -F
			ip6tables -t mangle -X
			ip6tables -t nat -F
			ip6tables -t nat -X
			ip6tables -t raw -F
			ip6tables -t raw -X
			ip6tables -t security -F
			ip6tables -t security -X
			ip6tables -P OUTPUT  DROP
			ip6tables -P INPUT   DROP
			ip6tables -P FORWARD DROP
			ip6tables-save > /etc/iptables/vpn-rules.v6
		fi
	fi

}

function menu_auth {
	USERNAME=$(dialog --backtitle "RiseUp VPN Helper" --title "Login" --inputbox "Username:" 8 50 2>&1 >/dev/tty)
	PASSWORD=$(dialog --backtitle "RiseUp VPN Helper" --title "Login" --clear --passwordbox "Password" 8 50 2>&1 >/dev/tty)
	clear
	echo -e "$USERNAME\n$PASSWORD" > /etc/openvpn/client/riseup/auth
	chmod 600 /etc/openvpn/client/riseup/auth
	chown root:root /etc/openvpn/client/riseup/auth
}

function secure_dns {
	if [ ! -f /etc/openvpn/scripts/update-systemd-resolved ]; then
		mkdir -p /etc/openvpn/scripts
		wget -O /etc/openvpn/scripts/update-systemd-resolved https://raw.githubusercontent.com/jonathanio/update-systemd-resolved/master/update-systemd-resolved
		chmod 750 /etc/openvpn/scripts/update-systemd-resolved
	fi
	if [ -f /etc/nsswitch.conf ]; then
		if ! grep -q "hosts: files resolve myhostname" /etc/nsswitch.conf; then
			sed 's/hosts:.*/hosts: files resolve myhostname/' /etc/nsswitch.conf > /etc/nsswitch.conf
		fi
	else
		echo "[!] - Failed to locate /etc/nsswitch.conf file!"
		exit 1
	fi
	if ! $(/usr/bin/systemctl -q is-active systemd-resolved.service); then
		systemctl start systemd-resolved
	fi
	if ! $(/usr/bin/systemctl -q is-enabled systemd-resolved.service); then
		systemctl enable systemd-resolved
	fi
}

function setup {
	pacman -S dialog openvpn screen sudo
	mkdir -p /var/lib/openvpn
	if ! id vpn >/dev/null 2>&1; then
		useradd -r -d /var/lib/openvpn -s /usr/bin/nologin vpn
	fi
	if [ ! $(getent group vpn) ]; then
		groupadd vpn
	fi
	if ! getent group vpn | grep &>/dev/null "\bvpn\b"; then
		gpasswd -a vpn vpn
	fi
	chown vpn:vpn /var/lib/openvpn
	if [ -f /etc/sudoers ]; then
		if ! grep -q "vpn ALL=(ALL) NOPASSWD: /sbin/ip" /etc/sudoers; then
			echo -e "\nvpn ALL=(ALL) NOPASSWD: /sbin/ip" >> /etc/sudoers
		fi
		if ! grep -q "Defaults:vpn !requiretty" /etc/sudoers; then
			echo -e "\nDefaults:vpn !requiretty" >> /etc/sudoers
		fi
	else
		echo "[!] - Failed to locate /etc/sudoers file!"
		exit 1
	fi
	if [ ! -f /usr/local/sbin/unpriv-ip ]; then
		echo "#!/bin/sh" > /usr/local/sbin/unpriv-ip
		echo "sudo /sbin/ip \$*" >> /usr/local/sbin/unpriv-ip
		chmod 755 /usr/local/sbin/unpriv-ip
	fi
	if [ ! -f /etc/openvpn/openvpn-startup ]; then
		echo "#!/bin/sh" > /etc/openvpn/openvpn-startup
		echo "openvpn --rmtun --dev tun0" >> /etc/openvpn/openvpn-startup
		echo "openvpn --mktun --dev tun0 --dev-type tun --user vpn --group vpn" >> /etc/openvpn/openvpn-startup
		chmod 755 /etc/openvpn/openvpn-startup
	fi
	if [ -d /etc/openvpn/client/riseup ]; then
		rm -r /etc/openvpn/client/riseup
	fi
	mkdir /etc/openvpn/client/riseup
	wget -O /etc/openvpn/client/riseup/ca.pem https://riseup.net/security/network-security/riseup-ca/RiseupCA.pem
	menu_auth
}

if [ $EUID -ne 0 ]; then
	echo "[!] - This script requires sudo privledges!"
	exit 1
fi
if [ ! -d /etc/openvpn/client/riseup ]; then
	setup
	generate_config
fi
secure_dns
if [ $DISABLE_IPV6 -eq 1 ]; then
	disable_ipv6
fi
openvpn --cd /etc/openvpn/client/riseup --config riseup.conf
if [ $ENABLE_KILLSWITCH -eq 1 ]; then
	killswitch
fi
