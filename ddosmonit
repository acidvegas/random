#!/bin/sh
interface=eth0
dumpdir=/tmp/
email="admin@domain.tld"
subject="DDoS Notification: `hostname`"
sender="admin@domain.tld"
while /bin/true; do
	pkt_old=`grep $interface: /proc/net/dev | cut -d : -f2 | awk '{ print $2 }'`
	sleep 1
	pkt_new=`grep $interface: /proc/net/dev | cut -d : -f2 | awk '{ print $2 }'`
	pkt=$(( $pkt_new-$pkt_old ))
	echo -ne "\r$pkt packets/s\033[0K"
	if [ $pkt -gt 5000 ]; then
		filename=$dumpdir/dump.`date +"%Y%m%d-%H%M%S"`.cap
		tcpdump -n -s0 -c 2000 > $filename
		echo "`date` Packets dumped, sleeping now."
		sleep 1
		data=`cat $filename`
		sendmail -F $sender -it <<END_MESSAGE
		To: $email
		Subject: $subject
		`cat $filename`
		END_MESSAGE
		echo "sendmail complete"
		sleep 300
	fi
done