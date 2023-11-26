import mido
import time
import sys

mido.set_backend("mido.backends.pygame")
msg = mido.Message("clock")

# My test ports
if sys.platform == "linux":
    port = 'Midi Through Port-0'
else:
    port = 'DIN 1'
out = mido.open_output(port, autoreset=True)

start = time.time_ns()
count = 0

while True:
    out.send(msg)
    count += 1
    # 120bpm = 120*24 ticks per minute = 48 ticks per second =
    # 1E9/48 ns/tick 
    n = int(count*5E8//24)
    tick_ns = start + n
    sc = 0
    pmax = 0
    pmin = 1E20
    pt = 0
    while True:
        time.sleep(0)  # Sleep as little as possible
        pold = pt
        pt = time.time_ns()
        if pold != 0:
            pdiff = pt - pold
            pmin = min(pdiff, pmin)
            pmax = max(pdiff, pmax)
        p = pt - tick_ns
        if p > 0:
            print(sc, p, pmin, pmax)
            break
        sc += 1
    
    
    
