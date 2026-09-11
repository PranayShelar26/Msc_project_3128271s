# Cross-Vendor Validation — AMD Energy Measurement (uProf, WSL2)

This document records how workflow traces and per-task energy were obtained on
the two AMD validation machines for the cross-vendor experiments (thesis §7.1).
It is intended to make the AMD measurements reproducible.

## Machines

| Property | Ryzen 7 | Ryzen 5 |
|---|---|---|
| Processor | AMD Ryzen 7 4800H | AMD Ryzen 5 7535U |
| Cores | 8 | 8 |
| RAM | 8 GB | 16 GB |
| Approx. package power | ~28 W | ~23 W |
| OS |  Windows + WSL2 distro/version | Windows + WSL2 distro/version |
| Energy interface | AMD uProf | AMD uProf |

## Software stack

- Nextflow: 23.10.1 (running under WSL2)
- nf-core pipelines: atacseq - 2.1.2, chipseq - 2.0.0
- Java: 17.0.10
- AMD uProf: 5.3.521.0 (running on the Windows host)

# Step 1 — Set up WSL2 environment
bash
# In WSL2 terminal
sudo apt update
sudo apt install openjdk-17-jdk   # Java 17 for Nextflow
java -version                      # confirm 17

# Nextflow
curl -s https://get.nextflow.io | bash
sudo mv nextflow /usr/local/bin/
nextflow -version

# Confirm Docker works (Docker Desktop must be running on Windows with WSL2 integration on)
docker ps
# Step 2 — Confirm RAPL is NOT available (why you use uProf)
bash
ls /sys/class/powercap/   # will be empty under WSL2 — confirms RAPL unavailable

This is why you measure on the Windows host with uProf instead.

Step 3 — Prepare the trace config (in WSL2)
bash
cat > trace.config << 'EOF'
trace {
    enabled = true
    raw = true
    fields = 'task_id,hostname,process,name,status,exit,cpus,time,memory,submit,start,complete,duration,realtime,%cpu,%mem,rss,peak_rss,rchar,wchar'
    sep = ','
}
EOF
# Step 4 — Set up uProf logging (on Windows host)

uProf runs on Windows, not in WSL2, because it measures the physical CPU's package power.

Option A — uProf CLI (AMDuProfCLI):
Open a Windows Command Prompt / PowerShell (as admin) and use the timed collection:

AMDuProfCLI.exe timechart --event power --interval 1000 --duration <seconds> -o C:\path\to\output
--event power — collects power/energy
--interval 1000 — sample every 1000ms (1 second, matching your pipeline)
--duration — how long to log (set longer than the workflow will take)
Output goes to a CSV

The key: uProf logs package power (watts) over time with timestamps.

# Step 5 — Run the workflow (coordinated timing)

The critical part is timing coordination — uProf (Windows) and the workflow (WSL2) run separately, so:

Start uProf logging first (on Windows) — note the start time.
Immediately run the workflow (in WSL2):

bash

# Check disk space first
df -h

# Clean previous runs (or you get cached tasks with no energy)
rm -rf work .nextflow*

# Run
NXF_VER=23.10.1 nextflow run nf-core/<workflow> -r <version> \
  -profile test,docker \
  --outdir chipseq_out \
  -with-trace chipseq_trace.txt \
  -c trace.config
Stop uProf logging after the workflow finishes (it must outlast the workflow).