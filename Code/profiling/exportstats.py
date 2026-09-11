import sys
import numpy as np


def get_lines(filename):
    with open(f'../raw/AMD_Ryzen7/{filename}', 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines


# no. of cores
def read_props(filename):
    raw = get_lines(filename)
    threads = int(raw[1].split(':')[1])
    cores_per_socket = int(raw[2].split(':')[1])
    sockets = int(raw[3].split(':')[1])
    return threads * cores_per_socket * sockets


# measured in instructions per second (read documentation) MIPS
def read_7z_run(filename):
    raw = get_lines(filename)
    return f'{raw[-1].split()[2]}'


# measured in events per second
def read_sysbench_run(filename):
    raw = get_lines(filename)
    ents_per_sec = raw[8].split(':')[1].strip()
    return f'{ents_per_sec}' 


# measured in MiB/s
def read_fio_run(filename):
    raw = get_lines(filename)

    for line in raw:
        if "READ: bw=" in line or "WRITE: bw=" in line:
            data_line = line
            break

    return data_line.split(',')[0].split(' ')[1].split('=')[1][:-5]


def convert_J_to_kWh(val):
    return val / 3600000


def read_benchmark_trace(filename):
    raw = get_lines(filename)

    # compute the difference --> 16 is start, 17 complete, memory is 13, 21 cpu%, 22 %mem, 26 peak_vmem, 31 read_bytes, 32 write_bytes
    first_record = raw[1].split(',')
    earliest_start = first_record[16]
    latest_complete = first_record[17]
    for line in raw[2:]:
        parts = line.split(',')
        if parts[16] < earliest_start:
            earliest_start = parts[16]
        if parts[17] > latest_complete:
            latest_complete = parts[17]

    makespan = (float(latest_complete) - float(earliest_start)) / 1000  # convert to seconds

    return makespan


def get_mean_and_std(arr):
    return np.mean(arr), np.std(arr)


def average_wf_benchmark():
    time_1 = read_benchmark_trace('wf-benchmark-1.csv', )

    return get_mean_and_std([time_1])


def write_profile(data, memory):
    cores,io_read,io_write,bench = data
    filename = '../laptop_data/raw/stats.csv'
    with open(filename, 'w') as f:
        f.write('ram,cores,io_read,io_write,sysbench,bench_time\n')
        f.write(f'{memory},{cores},{io_read},{io_write},{bench}\n')
    print(f'[ExportStats] profile created with {memory}GB in {filename}')


if __name__ == '__main__':
    args = sys.argv[1:]
    memory =args[0].strip()
    props = read_props('props.txt')
    fio_read = read_fio_run('fio_read.txt' )
    fio_write = read_fio_run('fio_write.txt')
    sysbench = read_sysbench_run('sysbench.txt' )

    write_profile((props, fio_read, fio_write, sysbench),memory)