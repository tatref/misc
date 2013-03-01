#!/usr/bin/env python
#
# Tool to slow specific IP on call of duty
# Using Linux's traffic shaping and tshark
#
# Execute as root (lancher.sh is simpler)
# Tested on backtrack 5, ubuntu
# 
# Require:
#  tshark
#  
#

import time
import curses
import optparse
import os
import re
import signal
import subprocess
import sys
import traceback

# Sending ~20 pkts / second
MIN_PACKETS = 70
DELAY = 1000				# ms
MY_IP = "192.168.0.1"

"""
ctrl-c handler
Clean qdisc and exit
"""
def interrupt_handler(signal, frame):
	print("Cleaning qdisc and exiting !")
	init()

	# clean curses
	curses.echo()
	curses.nocbreak()
	curses.endwin()
	traceback.print_exc()

	# exit
	sys.exit(0)

"""
execute cmd
display = True/False to print output
"""
def run_cmd(c, display):
	s = subprocess.Popen(c.split(), stdout=subprocess.PIPE, stderr = subprocess.PIPE)
	v = s.wait()

	if display == True:
		output = "".join(s.stdout.readlines())
		print(output)

	if v != 0:
		# An error occurred
		print(c + "".join(map(str, s.stderr.readlines())))
		print(c + "".join(map(str, s.stdout.readlines())))

"""
init traffic shapping, and reset iptables
"""
def init():
	init_qdisc(DELAY)

	# delete all rules
	run_cmd("iptables -F", False)

	# delete all chains
	run_cmd("iptables -X", False)
	

"""
init traffic shapping
"""
def init_qdisc(delay):
	commands = ["tc qdisc del dev eth0 parent 1:3",
    "tc qdisc del dev eth0 root",
	"tc qdisc add dev eth0 root handle 1: prio",
	"tc qdisc add dev eth0 parent 1:3 handle 30: netem delay " + str(delay) + "ms"]

	for c in commands:
		run_cmd(c, False)

"""
return a list of conversations, each conversation beeinga dict of: ip1, ip2, outcoming packets, incoming packets
"""
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

"""
low-level function to slow ip
"""
def slow(ip):
	c = "tc filter add dev eth0 protocol ip parent 1:0 prio 3 u32 match ip dst " + ip + " flowid 1:3"
	
	run_cmd(c, False)

"""
low-level function to kick ip
"""
def kick(ip):
	cmd = "iptables -I INPUT -i eth0 -s " + ip + " -j DROP"
	run_cmd(cmd)
	cmd = "iptables -I OUTPUT -d " + ip + " -j DROP"
	run_cmd(cmd)

def print_conv(conv):
	print(conv)


"""
old terminal version
"""
def batch():
	init()

	print("Sniffing...")
	conv = sniff()

	if conv == None or len(conv) == 0:
		print("No packets :-(")
	elif len(conv) == 1:
		host = conv[0]["ip1"] if conv[0]["ip1"] != MY_IP else conv[0]["ip2"]
		print("Not host :-(\nHost is " + host)
		run_cmd("./geolocate_ip.sh " + host, True)
	else:
		print("Got host !\n")
		clients = []
		for line in conv:
			client_ip = line["ip1"] if line["ip1"] != MY_IP else line["ip2"]
			pattern = re.compile("[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*")
			if not pattern.match(client_ip):
				print("Warning : not an IP: " + client_ip)
				continue
			frames = line["in_frames"] + line["out_frames"]
			clients.append(client_ip)
		print(str(len(clients)) + " clients :\n" + "\n".join(clients))

		raw_input("Press enter to start slowing")
		
		while True:
			for ip in clients:
				init()
				slow(ip)
				print("Slowing " + ip)

				do_kick = raw_input("kick? ")
				if do_kick == "y":
					kick(ip)
				raw_input("")
			print("\nEnd of clients !")

"""
Internal variables used by curses
"""
class Model(object):
	def __init__(self):
		self.host = None
		self.delay = 1000
		self.clients = []
		# require :
		# -host / not host
		# -list of clients
		# -delay
		# -kick / slow multiple IP
		pass

	def refresh_clients(self):
		init()

		self.host = None
		self.clients = []

		conv = sniff()

		if conv == None or len(conv) == 0:
			self.host = None
		elif len(conv) == 1:
			host = conv[0]["ip1"] if conv[0]["ip1"] != MY_IP else conv[0]["ip2"]
			self.host = host
			#run_cmd("./geolocate_ip.sh " + host, True)
		else:
			self.host = "self"
			clients = []
			for line in conv:
				client_ip = line["ip1"] if line["ip1"] != MY_IP else line["ip2"]
				pattern = re.compile("[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*")
				if not pattern.match(client_ip):
					print("Warning : not an IP: " + client_ip)
					continue
				frames = line["in_frames"] + line["out_frames"]
				self.clients.append(client_ip)

	def set_delay(delay):
		self.delay = delay

	def slow(ip):
		init()
		model.slow(ip)

	def kick(ip):
		init()
		kick(ip)


"""
Main curses display
"""
def main_curses(screen, model):
	slowed_client = None
	selected_client = 0
	clients_y_offset = 1

	running = True
	while running:
		screen.clear()

		# draw UI here
		###############
		screen.addstr(0, 0, "Host is " + str(model.host))

		for i in range(len(model.clients)):
			screen.addstr(clients_y_offset + i, 1, "[ ] " + model.clients[i])
			if slowed_client == i:
				screen.addstr(clients_y_offset + i, 2, "x")

		# set cursor pos
		if len(model.clients) > 0:
			screen.move(selected_client + clients_y_offset, 2)


		# end of draw UI
		screen.refresh()

		c = screen.getch()

		if c == ord('q'):
			# quit
			running = False
		if c == ord('r'):
			# refresh
			screen.addstr(0, 30, "Refreshing list of clients...")
			screen.refresh()

			# re-init UI
			slowed_client = None
			selected_client = 0

			# refresh model
			model.refresh_clients()
		if c == curses.KEY_UP:
			if selected_client > 0:
				selected_client -= 1
		if c == curses.KEY_DOWN:
			if selected_client < len(model.clients) - 1:
				selected_client += 1
		if c == ord(' '):
			if model.host == "self":
				slowed_client = selected_client
				model.slow(model.clients[selected_client])
		if c == ord('k'):
			if model.host == "self":
				kicked_client = selected_client
				model.kick(model.clients[selected_client])

		# end of getch()
	# end of main loop

if __name__ == '__main__':
	# ctrl-c handler
	signal.signal(signal.SIGINT, interrupt_handler)

	# curses
	#screen = curses.initscr()
	#curses.noecho()		# dont echo input keys
	#curses.cbreak()		# don't wait for 'enter' to read keys
	#screen.keypad(1)	# interpret special keys (UP, DOWN...)

	## model
	#model = Model()

	try:
		# old terminal script
		batch()
	except:
		pass
		#main_curses(screen, model)
	#except:
	#	curses.echo()
	#	curses.nocbreak()
	#	curses.endwin()
	#	traceback.print_exc()
	#finally:
	#	curses.echo()
	#	curses.nocbreak()
	#	curses.endwin()

