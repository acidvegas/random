location ~ /.well-known/acme-challenge/ {
    allow all;
    root /var/www/html; # This should point to the webroot of your site
}

sudo nano /etc/systemd/system/certbot-renewal.service
[Unit]
Description=Certbot Renewal

[Service]
Type=oneshot
ExecStart=/usr/bin/certbot renew --webroot -w /var/www/html --quiet

sudo nano /etc/systemd/system/certbot-renewal.timer
[Unit]
Description=Run certbot renewal daily

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target


sudo systemctl enable certbot-renewal.timer
sudo systemctl start certbot-renewal.timer
