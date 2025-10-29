#!/bin/bash

echo "Testing concurrent client requests"
echo "===================================="
echo ""

echo "Starting 3 clients simultaneously..."
echo ""

./client.py 1 &
./client.py 3 &
./client.py 99 &

wait

echo ""
echo "All clients finished"

