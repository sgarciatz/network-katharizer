#!/bin/bash

dstIP=$1
# Frequecy depends on the heat value 
freq=$(echo "scale=2; 1 / $2" | bc)
#Create a csv of RTTs with header
echo "RTT" >> /shared/$3 
ping -i $freq -w 60 $dstIP | while read line; do
    [[ "$line" =~ ^PING ]] && continue
    [[ ! "$line" =~ "bytes from" ]] && continue
    rtt=${line##*time=}
    rtt=${rtt%% *}
    echo "$rtt" >> /shared/$3 
done
