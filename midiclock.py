import mido
import time

mido.set_backend("mido.backends.pygame")
msg = mido.Message("clock")
out = mido.open_output('MIDIFACE 16x16 MIDI 1', autoreset=True)

start = time.time_ns()
count = 0

while True:
    out.send(msg)
    count += 1
    # 120bpm = 120*24 ticks per minute = 48 ticks per second =
    # 1E9/48 ns/tick 
    n = int(count*5E8//24)
#    print(count)
    tick_ns = start + n
    sc = 0
    while True:
        time.sleep(0.000001)  # Sleep one microsecond
        if time.time_ns() >= tick_ns:
            break
        sc += 1
    
    
    
