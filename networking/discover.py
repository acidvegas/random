#!/usr/bin/env python
import subprocess

def portscan(ip):
	ports = list()
	try:
		cmd = subprocess.check_output('nmap -F ' + ip, shell=True).decode()
		output = cmd.split('SERVICE')[1].split('MAC')[0].split('\n')
		for item in output:
			port = item.split('/')[0]
			if port and 'filtered' not in item:
				ports.append(port)
		return ports
	except:
		return None

def scanhosts(subnet):
	data = list()
	matrix = {'ip':list(),'host':list(),'ports':list()}
	cmd = subprocess.check_output(f'nmap -sP {subnet}/24', shell=True).decode()
	output = cmd.split('Nmap scan report for ')[1:-1]
	for item in output:
		ip    = item.split('\n')[0]
		ports = portscan(ip)
		ports = ', '.join(ports) if ports else 'N/A'
		mac   = item.split('MAC Address: ')[1].split()[0]
		host  = item.split(mac)[1].replace('(','').replace(')','')[1:-1]
		matrix['ip'].append(ip)
		matrix['host'].append(host)
		matrix['ports'].append(ports)
		data.append({'ip':ip,'mac':mac,'host':host,'ports':ports})
	for item in matrix:
		matrix[item] = len(max(matrix[item], key=len))
	print('\033[30m\033[47m{0}   {1}   {2}   {3} \033[0m'.format('IP Address'.ljust(matrix['ip']), 'MAC Address      ', 'Hostname'.ljust(matrix['host']), 'Ports'.ljust(matrix['ports'])))
	for item in data:
		print('{0} | {1} | {2} | {3}'.format(item['ip'].ljust(matrix['ip']), item['mac'], item['host'].ljust(matrix['host']), item['ports']))

scanhosts('10.0.0.0')