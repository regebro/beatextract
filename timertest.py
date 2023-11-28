#!/usr/bin/env python3
import time
import statistics

def print_stats(times):
    t0 = times.pop(0)
    deltas = []
    for t in times:
        deltas.append(t - t0)
        t0 = t
        
    dmin = min(deltas)
    dmax = max(deltas)
    avg = sum(deltas) // len(deltas)
    print(f"Minimum: {dmin}  Maximum: {dmax} Average: {avg} Delta: {dmax-dmin}")
    stddev = statistics.pstdev(deltas)
    print(f"The standard deviation is {stddev} ns")

    # Split into x groups
    numgroups = 11
    gwidth = 2 * (max([dmax, dmin]) - avg) / numgroups
    groups = [int((x - dmin) // gwidth) for x in deltas]
    maxcount = max(groups.count(i) for i in range(numgroups))
    scale = max(maxcount/80, 1)
    
    print()
    print("Distribution:")
    for i in range(numgroups):
        print("#" * int(groups.count(i) / scale))

    return


def timertest():

    print("Minimal sleep")
    print("=============")
    times = []
    for i in range(10000):
        time.sleep(0)  # Sleep as little as possible
        times.append(time.time_ns())
    print_stats(times)

    print("1 microsecond sleep")
    print("===================")
    times = []
    for i in range(10000):
        time.sleep(0.000001)  # Sleep as little as possible
        times.append(time.time_ns())
    print_stats(times)
    

    print("1 millisecond sleep")
    print("===================")
    times = []
    for i in range(10000):
        time.sleep(0.001)  # Sleep as little as possible
        times.append(time.time_ns())
    print_stats(times)

if __name__ == "__main__":
    timertest()
    
