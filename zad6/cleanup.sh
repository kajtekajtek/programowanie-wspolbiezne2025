#!/bin/bash

# Cleanup script for IPC resources used by the Three Card Monte game

echo "Cleaning up IPC resources for current user..."
echo

# Remove semaphores
echo "Removing semaphores..."
ipcs -s | grep $(whoami) | awk '{print $2}' | while read id; do
    if [ -n "$id" ]; then
        ipcrm -s $id 2>/dev/null && echo "  Removed semaphore $id"
    fi
done

# Remove shared memory segments
echo "Removing shared memory segments..."
ipcs -m | grep $(whoami) | awk '{print $2}' | while read id; do
    if [ -n "$id" ]; then
        ipcrm -m $id 2>/dev/null && echo "  Removed shared memory $id"
    fi
done

echo
echo "Cleanup complete!"
echo
echo "Current IPC resources:"
echo "Semaphores:"
ipcs -s
echo
echo "Shared Memory:"
ipcs -m

