#!/bin/bash

DEFAULT_SERVER=0
DISABLE_IPV6=1

function disable_ipv6 {
	sysctl -w net.ipv6.conf.all.disable_ipv6=0
	sysctl -w net.ipv6.conf.default.disable_ipv6=0
	sysctl -w net.ipv6.conf.lo.disable_ipv6=0
}

function generate_config {
	if [ -f /etc/openvpn/client/mullvad/mullvad.conf ]; then
		sed '14s/.*/remote ${1}.mullvad.net ${2}/' /etc/openvpn/client/mullvad/mullvad.conf > /etc/openvpn/client/mullvad/mullvad.conf
	else
		echo "auth-user-pass auth
ca ca.crt
cipher AES-256-CBC
client
comp-lzo
crl-verify crl.pem
dev tun
nobind
persist-key
persist-tun
ping 10
ping-restart 60
proto udp
remote ${1}.mullvad.net ${2}
remote-cert-tls server
resolv-retry infinite
tls-cipher TLS-DHE-RSA-WITH-AES-256-GCM-SHA384:TLS-DHE-RSA-WITH-AES-256-CBC-SHA
tun-ipv6
verb 3" > /etc/openvpn/client/mullvad/mullvad.conf
	fi
}

function menu_auth {
	ACCOUNT_NUMBER=$(dialog --backtitle "Mullvad VPN Helper" --title "Login" --inputbox "Account Number:" 8 50 2>&1 >/dev/tty)
	clear
	echo -e "$ACCOUNT_NUMBER\nm" > /etc/openvpn/client/mullvad/auth
	chmod 600 /etc/openvpn/client/mullvad/auth
	chown root:root /etc/openvpn/client/mullvad/auth
}

function menu_server {
	if [ $DEFAULT_SERVER -eq 0 ]; then
		OPTIONS=(1 "Random"
			2  "Austria        (AT)"
			3  "Australia      (AU)"
			4  "Belgium        (BE)"
			5  "Bulgaria       (BG)"
			6  "Canada         (CA)"
			7  "Canada         (CA) - Toronto"
			8  "Canada         (CA) - Vancouver"
			9  "Czech Republic (CZ)"
			10 "Denmark	       (DK)"
			11 "Germany	       (DE)"
			12 "Germany	       (DE) - Berlin"
			13 "Germany	       (DE) - Frankfurt"
			14 "Finland	       (FI)"
			15 "France	       (FR)"
			16 "Hong Kong      (HK)"
			17 "Hungary	       (HU)"
			18 "Israel         (IL)"
			19 "Italy          (IT)"
			20 "Japan          (JP)"
			21 "Moldova	       (MD)"
			22 "Netherlands    (NL)"
			23 "Norway	       (NO)"
			24 "Poland 	       (PL)"
			25 "Portugual	   (PT)"
			26 "Romania	       (RO)"
			27 "Singapore	   (SG)"
			28 "Spain 	       (ES)"
			29 "Sweden	       (SE)"
			30 "Sweden	       (SE) - Helsingborg"
			31 "Sweden	       (SE) - Malmö"
			32 "Sweden	       (SE) - Stockholm"
			33 "Switzerland	   (CH)"
			34 "United Kingdom (GB)"
			35 "United Kingdom (GB) - London"
			36 "United Kingdom (GB) - Manchester"
			37 "United States  (US)"
			38 "United States  (US) - Arizona"
			39 "United States  (US) - California"
			40 "United States  (US) - Florida"
			41 "United States  (US) - Georgia"
			42 "United States  (US) - Illinois"
			43 "United States  (US) - Nevada"
			44 "United States  (US) - New Jersey"
			45 "United States  (US) - New York"
			46 "United States  (US) - Texas"
			47 "United States  (US) - Utah"
			48 "United States  (US) - Washington"
			49 "United States  (US) - Washington DC")
		CHOICE=$(dialog --clear --backtitle "Mullvad VPN Helper" --title "Connection" --menu "Select a regional server below:" 20 60 20 "${OPTIONS[@]}" 2>&1 >/dev/tty)
		clear
		if [ $CHOICE -eq 1 ]; then
			CHOICE=$(shuf -i 2-38 -n 1)
		fi
	elif [ $DEFAULT_SERVER == 1 ]; then
		CHOICE=$(shuf -i 2-38 -n 1)
	else
		CHOICE=$DEFAULT_SERVER
	fi
	case $CHOICE in
		2)  generate_config "at"     "1302";;
		3)  generate_config "au"     "1302";;
		4)  generate_config "be"     "1196";;
		5)  generate_config "bg"     "1195";;
		6)  generate_config "ca"     "1301";;
		7)  generate_config "ca-bc"  "1196";;
		8)  generate_config "ca-on"  "1196";;
		9)  generate_config "cz"     "1302";;
		10) generate_config "dk"     "1197";;
		11) generate_config "de"     "1195";;
		12) generate_config "de-ber" "1197";;
		13) generate_config "de-fra" "1301";;
		14) generate_config "fi"     "1302";;
		15) generate_config "fr"     "1301";;
		16) generate_config "hk"     "1195";;
		17) generate_config "hu"     "1194";;
		18) generate_config "il"     "1197";;
		19) generate_config "it"     "1196";;
		20) generate_config "jp"     "1197";;
		21) generate_config "md"     "1301";;
		22) generate_config "nl"     "1195";;
		23) generate_config "no"     "1194";;
		24) generate_config "pl"     "1301";;
		25) generate_config "pt"     "1301";;
		26) generate_config "ro"     "1197";;
		27) generate_config "sg"     "1302";;
		28) generate_config "es"     "1194";;
		29) generate_config "se"     "1195";;
		30) generate_config "se-hel" "1197";;
		31) generate_config "se-mma" "1194";;
		32) generate_config "se-sto" "1197";;
		33) generate_config "ch"     "1195";;
		34) generate_config "gb"     "1197";;
		35) generate_config "gb-lon" "1194";;
		36) generate_config "gb-mnc" "1302";;
		37) generate_config "us"     "1196";;
		38) generate_config "us-az"  "1194";;
		39) generate_config "us-ca"  "1194";;
		40) generate_config "us-fl"  "1195";;
		41) generate_config "us-ga"  "1196";;
		42) generate_config "us-il"  "1196";;
		43) generate_config "us-nv"  "1302";;
		44) generate_config "us-nj"  "1301";;
		45) generate_config "us-ny"  "1195";;
		46) generate_config "us-tx"  "1195";;
		47) generate_config "us-ut"  "1196";;
		48) generate_config "us-wa"  "1197";;
		49) generate_config "us-dc"  "1302";;
	esac
}

if [ $EUID -ne 0 ]; then
	echo "[!] - This script requires sudo privledges!"
	exit 1
fi
if [ ! -f /etc/openvpn/client/mullvad/auth ]; then
	menu_auth
fi
if [ $DISABLE_IPV6 -eq 1 ]; then
	disable_ipv6
fi
rm /etc/openvpn/client/mullvad/mullvad.conf
menu_server
openvpn --cd /etc/openvpn/client/mullvad --config mullvad.conf
