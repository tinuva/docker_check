#!/usr/bin/env python3
import sys
import os
import docker

__author__ = 'El Acheche Anis'
__license__ = 'GPL'
__version__ = '0.1'

'''
Requires Python 3

'''


def get_mem_pct(ct, stats):
    mem = stats[ct]['memory_stats']
    usage = mem['usage']
    limit = mem['limit']
    return round(usage*100/limit, 2)


def get_cpu_pct(ct):
    # cpu=client.containers.get(ct).stats(stream=False)['precpu_stats']
    # usage=cpu['system_cpu_usage']
    # ToDo:
    # Use API instead of docker stats
    # (new_dock_usage - old_dock_usage)/(new_sys_cpu_use-old_cpu_usage)*100
    # with spreding that on CPU CORE numbers
    # should find way to keep old & current values:OS STATS LOGS or a tmp file
    usage = str(os.popen("docker stats --no-stream=true "+ct).read()).split()
    usage_pct = usage[usage.index(ct)+1]
    return float(usage_pct[:-1])


def get_net_io(ct, stats):
    net =  stats[ct]['networks']
    net_in = net['eth0']['rx_bytes']
    net_out = net['eth0']['tx_bytes']
    return [net_in, net_out]


def get_disk_io(ct, stats):
    disk = stats[ct]['blkio_stats']['io_service_bytes_recursive']
    disk_in = disk[0]['value']
    disk_out = disk[1]['value']
    return disk_in, disk_out


def main():
    ls = client.containers.list()
    ct = []

    for i in ls:
        ct.append(str(i).replace('<', '').replace('>', '').split()[1])

    summary = ''
    stats = {}
    metrics = [0, 0]
    ct_stats = {}
    for i in ct:
        ct_stats[i] = client.containers.get(i).stats(stream=False)
        mem_pct = get_mem_pct(i, ct_stats)
        cpu_pct = get_cpu_pct(i)
        net_in = get_net_io(i, ct_stats)[0]
        net_out = get_net_io(i, ct_stats)[1]
        disk_in = get_disk_io(i, ct_stats)[0]
        disk_out = get_disk_io(i, ct_stats)[1]
        stats[i+'_mem_pct'] = mem_pct
        stats[i+'_cpu_pct'] = cpu_pct
        summary += '{}_mem_pct={}% {}_cpu_pct={}% {}_net_in={} {}_net_out={} '\
                   '{}_disk_in={} {}_disk_out={} '.format(
                    i, mem_pct, i, cpu_pct, i, net_in, i, net_out, i, disk_in,
                    i, disk_out)

    for s in stats:
        if stats[s] >= metrics[1]:
            metrics[0] = s
            metrics[1] = stats[s]

    if metrics[1] < 50:
            print("OK | {}".format(summary))
            sys.exit(0)
    elif 50 <= metrics[1] <= 80:
            print("WARNING: Some containers need your attention: {} have {}% '\
                    | {}".format(metrics[0], metrics[1], summary))
            sys.exit(1)
    elif metrics[1] > 80:
            print("CRITICAL: Some containers need your attention: {} have {}%'\
                    ' | {}".format(metrics[0], metrics[1], summary))
            sys.exit(2)
    else:
            print("UKNOWN | {}".format(summary))
            sys.exit(3)

if __name__ == '__main__':
    client = docker.from_env(version="1.21")
    # try except the version based on docker version | grep "server api"
    main()
