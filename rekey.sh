#!/bin/sh
recycle_gpg_key() {
	gpg --expert --full-gen-key
	local KEYID="CHANGEME" # todo: automatically parse this from gpg output
	gpg --export --armor $KEYID > $KEYID.pub.asc
	gpg --export-secret-keys --armor $KEYID > $KEYID.priv.asc
	gpg --export-secret-subkeys --armor $KEYID > $KEYID.sub_priv.asc
	gpg --delete-secret-key $KEYID
	gpg --import $KEYID.sub_priv.asc
}

recycle_irc_key() {
	local NICK="CHANGEME"
	openssl req -x509 -new -newkey rsa:4096 -sha256 -days 3650 -nodes -out $NICK.pem -keyout $NICK.pem
	chmod 400 $NICK.pem
}

recycle_ssh_key() {
	if [ ! -d $HOME/.ssh ]; then
		mkdir $HOME/.ssh
	else
		[ -f $HOME/.ssh/key     ] && mv $HOME/.ssh/key $HOME/.ssh/key.back
		[ -f $HOME/.ssh/key.pub ] && rm $HOME/.ssh/key.pub
	fi
	read -p "Password: " $PASSWORD
	ssh-keygen -t ed25519 -a 100 -C "" -P "$PASSWORD" -f $HOME/.ssh/key -q
}

setup_authorized_keys() {
	if [ ! -d /etc/ssh/authorized_keys ]; then
		mkdir /etc/ssh/authorized_keys
	else
		for f in /home/*/.ssh/authorized_keys; do
			local USERNAME=$(echo $f | cut -d/ -f 3)
			if [ ! -f /etc/ssh/authorized_keys/$USERNAME ]; then
				cat $f > /etc/ssh/authorized_keys/$USERNAME && rm $f
			fi
		done
	fi
}