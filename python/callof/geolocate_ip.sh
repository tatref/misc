#!/bin/bash

if [ $# -ne 1 ]
then
	echo "Usage : $(basename $0) <ip>"
	exit 1
fi

url="http://www.geoiptool.com/en/?IP=$1"
user_agent='Mozilla/6.0 (Windows NT 6.2; WOW64; rv:16.0.1) Gecko/20121011 Firefox/16.0.1'


lynx -useragent="$user_agent" -dump $url | sed -n '/Host Name/,/Postal code/p' 2> /dev/null
