#!/bin/bash

MASTER_IP_ADDRESS=$1

echo "wait for control plane ready(timeout = 300 s)"
result=1

for _ in {1..60}
do
    nc -zv -w 1 "$MASTER_IP_ADDRESS" 6443
    result=$?

    if [ $result -ne 0 ]; then
      echo "master node not ready yet, wait for 5 second to do check again"
      sleep 5
    else
      break
    fi
done

exit $result
