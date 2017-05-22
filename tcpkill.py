#!/usr/bin/env python
#
# tcpkill using scapy
#
# Usage: sudo /path/to/python tcpkill <ip> <dport> <sport>
#

from scapy.all import *


ip = sys.argv[1]
dport = int(sys.argv[2])
sport = int(sys.argv[3])


print('Waiting for TCP packet...')

# we wait for 1 packet to arrive on the interface to know the seq number
f = 'host ' + ip + ' and tcp and dst port ' + str(dport) + ' and src port ' + str(sport)
p = sniff(filter=f, count=1)[0]


# grab seq number
seq = p.getlayer('TCP').seq

# send RST
send(IP(dst=ip)/TCP(dport=dport,sport=sport, seq=seq, flags='R'))
