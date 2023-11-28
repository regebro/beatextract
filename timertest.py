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
    print(f"Minimum: {dmin} ns  Maximum: {dmax} ns Average: {avg} ns Delta: {dmax-dmin} ns")
    stddev = statistics.pstdev(deltas)
    print(f"The standard deviation is {stddev} ns")

    # Split into x groups
    numgroups = 11
    gwidth = 2 * (max([dmax, dmin]) - avg) / numgroups
    if gwidth == 0:
        gwidth = 1
    groups = [int((x - dmin) // gwidth) for x in deltas]
    maxcount = max(groups.count(i) for i in range(numgroups))
    scale = max(maxcount/80, 1)
    
    print()
    print("Distribution:")
    for i in range(numgroups):
        print("#" * int(groups.count(i) / scale))

    return


def timertest():

    print("Minimal sleep x 100000")
    print("======================")
    times = []
    for i in range(100000):
        time.sleep(0)  # Sleep as little as possible
        times.append(time.time_ns())
    print_stats(times)

    print("1 microsecond sleep x 1000")
    print("===========================")
    times = []
    for i in range(1000):
        time.sleep(0.000001)
        times.append(time.time_ns())
    print_stats(times)
    

    print("1 millisecond sleep x 1000")
    print("==========================")
    times = []
    for i in range(1000):
        time.sleep(0.001)
        times.append(time.time_ns())
    print_stats(times)

if __name__ == "__main__":
    timertest()
    
