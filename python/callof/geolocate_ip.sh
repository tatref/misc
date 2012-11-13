#!/bin/bash

if [ $# -ne 1 ]
then
	echo "Usage : $(basename $0) <ip>"
	exit 1
fi

url="http://www.geoiptool.com/en/?IP=$1"

lynx -dump $url | sed -n '/Host Name/,/Postal code/p'
