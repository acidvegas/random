#ROOT CHECK

ACCOUNT_NUMBER=CHANGEME
PRIVATE_KEY= CHANGEME # wg genkey

function get_servers() {
	ADDRESS="$(curl -sSL https://api.mullvad.net/wg/ -d account="$ACCOUNT_NUMBER" --data-urlencode pubkey="$(wg pubkey <<< "$PRIVATE_KEY")")"
	RESPONSE="$(curl -LsS https://api.mullvad.net/public/relays/wireguard/v1/)"
	FIELDS="$(jq -r 'foreach .countries[] as $country (.; .; foreach $country.cities[] as $city (.; .; foreach $city.relays[] as $relay (.; .; $country.name, $city.name, $relay.hostname,$relay.public_key, $relay.ipv4_addr_in)))' <<< "$RESPONSE")"
	while read -r COUNTRY && read -r CITY && read -r HOSTNAME && read -r PUBKEY && read -r IPADDR; do
		{
			echo "#COUNTRY @ $CITY"
			echo "[Interface]"
			echo "PrivateKey = $PRIVATE_KEY"
			echo "Address = $ADDRESS"
			echo "DNS = 193.138.218.74"
			echo -e "\n[Peer]"
			echo "PublicKey = $PUBKEY"
			echo "Endpoint = $IPADDR:51820"
			echo "AllowedIPs = 0.0.0.0/0, ::/0"
		} > /etc/mullvad-${HOSTNAME%-wireguard}.conf
	done <<< "$FIELDS"
}

function select_server() {
	for file in /etc/wireguard/*; do
	    echo $(basename "$file" | cut -d "-" -f2  )
	done
}