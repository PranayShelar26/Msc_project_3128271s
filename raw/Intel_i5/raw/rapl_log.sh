#!/bin/bash
# Logs package energy (microjoules) with millisecond epoch timestamp, once per second
while true; do
  echo "$(date +%s%3N),$(cat /sys/class/powercap/intel-rapl:0/energy_uj)"
  sleep 1
done
