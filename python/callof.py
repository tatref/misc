#!/usr/bin/env python
#
# Tool to slow specific IP on call of duty
# Using Linux's traffic shaping and tshark
#

import optparse, os, re, subprocess, signal, sys

# Sending ~20 pkts / second
MIN_PACKETS = 70
DELAY = 300				# ms
MY_IP = "192.168.0.1"

"""ctrl-c handler
Clean qdisc and exit
"""
def interrupt_handler(signal, frame):
	print("Cleaning qdisc and exiting !")
	init()
	sys.exit(0)

def init():
	init_qdisc(DELAY)
	#arpspoof()
	

def init_qdisc(delay):
	commands = ["tc qdisc del dev eth0 parent 1:3",
    "tc qdisc del dev eth0 root",
	"tc qdisc add dev eth0 root handle 1: prio",
	"tc qdisc add dev eth0 parent 1:3 handle 30: netem delay " + str(delay) + "ms"]

	for c in commands:
		s = subprocess.Popen(c.split(), stdout=subprocess.PIPE, stderr = subprocess.PIPE)
		v = s.wait()
		if v != 0:
			# An error occurred
			print(c + "".join(map(str, s.stderr.readlines())))
			print(c + "".join(map(str, s.stdout.readlines())))

def sniff():
	tshark_cmd = "tshark -n -q -a duration:5 -z conv,udp not arp and udp and ip and port 3074"
	tshark = subprocess.Popen(tshark_cmd.split(), stdout=subprocess.PIPE, stderr = subprocess.PIPE)
	tshark.wait()
	
	tshark_out = tshark.stdout.readlines()

	conv = []
	pattern = re.compile("[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*")
	for line in tshark_out:
		line = line.decode("utf-8")
		if pattern.match(line):
			# IP1:PORT <-> IP2:PORT InFrames InSize OutFrames OutSize Frames Size
			split = line.split()
			ip1 = split[0].split(":")[0]
			ip2 = split[2].split(":")[0]
			in_frames = int(split[3])
			out_frames = int(split[5])

			conv.append({"ip1" : ip1, "ip2" : ip2, "in_frames" : in_frames, "out_frames" : out_frames})
	conv = list(filter(lambda d : True if (d["out_frames"] + d["in_frames"] > MIN_PACKETS) else False, conv))

	return conv

def slow(ip):
	# delay in ms
	init_qdisc(DELAY)
	
	pattern = re.compile("[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*")
	if not pattern.match(ip):
		raise ValueError
	
	commands = ["tc filter add dev eth0 protocol ip parent 1:0 prio 3 u32 match ip dst " + ip + " flowid 1:3"]
	
	for c in commands:
		s = subprocess.Popen(c.split(), stdout=subprocess.PIPE, stderr = subprocess.PIPE)
		v = s.wait()
		if v != 0:
			# Error occurred
			print(c + "".join(map(str, s.stderr.readlines())))
			print(c + "".join(map(str, s.stdout.readlines())))

def print_conv(conv):
	print(conv)

def batch():
	init()

	print("Sniffing...")
	conv = sniff()

	if conv == None or len(conv) == 0:
		print("No packets :-(")
	elif len(conv) == 1:
		host = conv[0]["ip1"] if conv[0]["ip1"] != MY_IP else conv[0]["ip2"]
		print("Not host :-(\nHost is " + host)
	else:
		print("Got host !\n")
		clients = []
		for line in conv:
			client_ip = line["ip1"] if line["ip1"] != MY_IP else line["ip2"]
			frames = line["in_frames"] + line["out_frames"]
			clients.append(client_ip)
		print(str(len(clients)) + " clients :\n" + "\n".join(clients))

		raw_input("Press enter to start slowing")
		
		while True:
			for ip in clients:
				init_qdisc(DELAY)
				slow(ip)
				print("Slowing " + ip)
				raw_input("")
			print("\nEnd of clients !")

if __name__ == '__main__':
	signal.signal(signal.SIGINT, interrupt_handler)
	init()
	batch()
