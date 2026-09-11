# Cross-Vendor Validation — Intel Energy Measurement (RAPL, bare-metal)

This document records how workflow traces and per-task energy were obtained on
the Intel validation machine for the cross-vendor experiments (thesis §7.1).
It is intended to make the Intel measurements reproducible.

# Machine

| Property | Value |
|---|---|
| Processor | Intel Core i5-12400 |
| Cores | 6 |
| RAM | 32 GB |
| Approx. package power | ~44 W |
| OS | Arch Linux (bare-metal) |
| Energy interface | RAPL via Linux powercap sysfs |

This machine is **not** in the training data. It was profiled solely to test
cross-vendor generalisation of the server-trained model.

# Software stack

- Nextflow: 23.10.1 (running under WSL2)
- nf-core pipelines: atacseq - 2.1.2, chipseq - 2.0.0
- Java: 17.0.10


1. Verify RAPL is accessible

bash
ls /sys/class/powercap/
cat /sys/class/powercap/intel-rapl:0/energy_uj   # should print a number

If you get a cumulative microjoule counter, RAPL works. (You may need sudo to read it.)

2. Set up a RAPL logger — a script that reads the counter every second with a timestamp, mirroring how Augur samples:

bash
# rapl_log.sh
while true; do
  echo "$(date +%s%3N),$(cat /sys/class/powercap/intel-rapl:0/energy_uj)"
  sleep 1
done > rapl_energy.csv

This logs epoch_ms,energy_uj once per second — the same cumulative-counter format you already know how to process. (Add DRAM if intel-rapl:0:0 / dram subdomain exists, to match your Augur package+DRAM setup.)

3. Clean previous runs

bash
rm -rf work .nextflow*
df -h .    # confirm disk space

4. Start the RAPL logger FIRST (must outlast the workflow, like uProf did):

bash
sudo bash rapl_log.sh &
RAPL_PID=$!

5. Run the workflow with tracing (same command/config as your laptop):

bash
NXF_VER=23.10.1 nextflow run nf-core/<workflow> -r <version> \
  -profile test,docker --outdir atacseq_out \
  -with-trace atacseq_trace.txt -c trace.config

Then repeat for chipseq (after another rm -rf work .nextflow*).

6. Stop the logger after the workflow finishes

bash
kill $RAPL_PID