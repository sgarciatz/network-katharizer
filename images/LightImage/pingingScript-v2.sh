#!/bin/bash

dstIP=$1
# Frequecy depends on the heat value 
freq=$(echo "scale=2; 1 / $2" | bc)

# Perform the ping and extract the latency
ping_result=$(ping -i $freq -w 60 "$dstIP" | grep "min/avg/max" )

# Use the variable as needed
random_number=$((60 + RANDOM % 120))

sleep $random_number
echo $ping_result > /shared/$3

