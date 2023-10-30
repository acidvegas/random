## 1. Set up the GRE Tunnel
###### Source
```shell
ip tunnel add gre1 mode gre remote [VPS2_PUBLIC_IP] local [VPS1_PUBLIC_IP] ttl 255
ip link set gre1 up
ip addr add [LOCAL_TUNNEL_IP1]/32 dev gre1
```

###### Destination
```shell
ip tunnel add gre1 mode gre remote [VPS1_PUBLIC_IP] local [VPS2_PUBLIC_IP] ttl 255
ip link set gre1 up
ip addr add [LOCAL_TUNNEL_IP2]/32 dev gre1
```

## 2. Set up IPsec
This is for securing the GRE tunnel. StrongSwan is a popular tool for IPsec.
1. `nano /etc/ipsec.conf` *(Both servers)*
```
conn gre-tunnel
    left=[VPS1_PUBLIC_IP]
    leftsubnet=[VPS1_LOCAL_NETWORK]
    right=[VPS2_PUBLIC_IP]
    rightsubnet=[VPS2_LOCAL_NETWORK]
    authby=secret
    keyexchange=ikev2
    ikelifetime=1h
    keylife=20m
    keyingtries=3
    auto=start
    esp=aes128-sha1-modp1024!
    ike=aes128-sha1-modp1024!
```

2. `nano /etc/ipsec.secrets`
```
[VPS1_PUBLIC_IP] [VPS2_PUBLIC_IP] : PSK "YourStrongSecretKey"
```

3. `systemctl restart strongswan`

## 3. Forward Traffic
###### Source
```shell
iptables -t nat -A POSTROUTING -o gre1 -j MASQUERADE
iptables -A FORWARD -i gre1 -j ACCEPT
```

###### Destination
```shell
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
iptables -A FORWARD -i gre1 -j ACCEPT
```

###### Both servers
`echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf` *(Permanent)*

or..

`echo 1 > /proc/sys/net/ipv4/ip_forward` *(Temporary)*

and then run `sysctl -p`
