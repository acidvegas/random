#!/usr/bin/env python
# DDoSmon - developed by acidvegas in python (https://git.acid.vegas/ddosmon)
import socket

try:
	import dpkt
	from dpkt.compat import compat_ord
except ImportError:
	raise Exception('missing required \'dpkt\' library (pip install dpkt)')

try:
	import pcapy
except ImportError:
	raise Exception('missing required \'pcapy\' library (pip install pcapy)')

def inet_to_str(inet):
	try:
		return socket.inet_ntop(socket.AF_INET, inet)
	except ValueError:
		return socket.inet_ntop(socket.AF_INET6, inet)

def mac_addr(address):
	return ':'.join('%02x' % compat_ord(b) for b in address)

def handle_packet(header, data):
	eth = dpkt.ethernet.Ethernet(data)
	if isinstance(eth.data, dpkt.ip.IP) or isinstance(eth.data, dpkt.ip6.IP6):
		ip  = eth.data
		do_not_fragment = bool(ip.off & dpkt.ip.IP_DF)
		more_fragments  = bool(ip.off & dpkt.ip.IP_MF)
		fragment_offset = ip.off & dpkt.ip.IP_OFFMASK
		print('Protocol       : ', ip.get_proto(ip.p).__name__)
		print('Ethernet Frame : ', mac_addr(eth.src), mac_addr(eth.dst), eth.type)
		print('Connection     : %s:%s -> %s:%s   (len=%d ttl=%d DF=%d MF=%d offset=%d)' % (inet_to_str(ip.src), ip.data.sport, inet_to_str(ip.dst), ip.data.dport, ip.len, ip.ttl, do_not_fragment, more_fragments, fragment_offset))
		if isinstance(ip.data, dpkt.icmp.ICMP):
			icmp = ip.data
			print('ICMP: type:%d code:%d checksum:%d data: %s\n' % (icmp.type, icmp.code, icmp.sum, repr(icmp.data)))
		elif isinstance(ip.data, dpkt.tcp.TCP):
			tcp = ip.data
			try:
				request = dpkt.http.Request(tcp.data)
			except (dpkt.dpkt.NeedData, dpkt.dpkt.UnpackError):
				pass
			else:
				print('HTTP request: %s\n' % repr(request))
				if not tcp.data.endswith(b'\r\n'):
					print('\nHEADER TRUNCATED! Reassemble TCP segments!\n')

if __name__ == '__main__':
	pcap = pcapy.open_live('eth0', 65536, 0, 100)
	pcap.loop(-1, handle_packet)
