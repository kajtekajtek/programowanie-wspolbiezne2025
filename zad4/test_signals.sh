#!/bin/bash

echo "Testing signal handling"
echo "======================="
echo ""

if [ -z "$1" ]; then
    echo "Usage: $0 <server_pid>"
    echo "Example: $0 12345"
    exit 1
fi

SERVER_PID=$1

echo "Server PID: $SERVER_PID"
echo ""

echo "Test 1: Sending SIGHUP (should be ignored)"
kill -SIGHUP $SERVER_PID
sleep 1
echo "SIGHUP sent"
echo ""

echo "Test 2: Sending SIGTERM (should be ignored)"
kill -SIGTERM $SERVER_PID
sleep 1
echo "SIGTERM sent"
echo ""

echo "Test 3: Sending SIGUSR1 (should terminate server)"
kill -SIGUSR1 $SERVER_PID
sleep 1
echo "SIGUSR1 sent"
echo ""

echo "Signal tests completed"

