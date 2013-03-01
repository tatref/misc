#!/bin/bash
#
# Wrapper script for callof.py script
# Configure Windows to use the Linux box as gateway
#


#########################
# Variables
#########################

ETH=eth0
PLAYER=192.168.0.1

#########################
# Main
#########################

# check that we are root
if [ $(id -u) -ne 0 ]
then
	echo "re-run as root"
	exit 1
fi

gateway=$(ip route | grep -o -P '(?<=default via )[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+')


# spoof gateway and player
echo 1 > /proc/sys/net/ipv4/ip_forward

sysctl net.ipv4.conf.eth0.send_redirects=0 > /dev/null
sysctl net.ipv4.conf.all.send_redirects=0 > /dev/null

#pkill -0 arpspoof
#if [ $? -eq 1 ]
#then
#	arpspoof -i $ETH -t $PLAYER $gateway &> /dev/null &
#	arpspoof -i $ETH -t $gateway $PLAYER &> /dev/null &
#fi

# main script
./callof.py

