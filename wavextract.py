import argparse
import struct
import wave


def load(sound):
    width = sound.getsampwidth()
    if width == 2:
        samp_struct = "<h"
        samp_prefix = b""
        samp_divisor = 1
    elif width == 3:
        # struct doesn't have a 3 byte wide data type, so we add a LSB of 0
        # unpack it as 4 bytes and then divide with 256
        samp_struct = "<i"
        samp_prefix = b"\00"
        samp_divisor = 256
    else:
        print(f"Sorry, this script does not support a sample width of {width}")
        return

    sample_values = []
    for i in range(sound.getnframes()):
        frame = sound.readframes(1)
        sample = struct.unpack(samp_struct, samp_prefix+frame)[0]//samp_divisor
        sample_values.append(sample)

    return sample_values


def find_sound(value_gen, threshold):
    pos = 0
    while abs(value := next(value_gen)) < threshold:
        pos += 1
    return pos


def find_silence(value_gen, threshold, silence):
    pos = 0
    while True:
        # Find a section below the threshold
        while abs(value := next(value_gen)) >= threshold:
            pos += 1
            continue
        # Check how long that section is
        l = find_sound(value_gen, threshold)
        pos += l
        if l > silence:
            # We found silence
            return pos

        # That wasn't long enough to be silence, so we continue
        continue


def extract(filename, threshold, silence):
    sound = wave.open(filename, "rb")

    if sound.getnchannels() != 1:
        print(f"Sorry, this script only supports mono sounds")
        return

    print("Loading...")
    values = load(sound)
    print(f"Found {8*sound.getsampwidth()} bit sound file with {len(values)} samples")

    value_gen = iter(values)
    pos = 0
    # Skip silence
    print("Looking...")
    pos += find_sound(value_gen, threshold)

    print(f"Skipping {pos} samples of silence.")
    print("Found sound", end="")
    sound_starts = []
    try:

        while True:
            sound_starts.append(pos)
            print(".", end="")

            # Now look for silence
            pos += find_silence(value_gen, threshold, silence)
            # And then for a new sound
            pos += find_sound(value_gen, threshold)

    except StopIteration:
        print()

    print("Done! Found with the following distances")
    prev = sound_starts[0]
    distances = []
    for pos in sound_starts[1:-1]:
        d = pos-prev
        distances.append(d)
        print(d)
        prev = pos
        
    if not distances:
        print(f"No sounds found with threshold {threshold} and min {silence} samples of silence.")
        return
    
    dmin = min(distances)
    dmax = max(distances)
    avg = sum(distances)//len(distances)
    print(f"Minimum: {dmin}  Maximum: {dmax} Average: {avg} Delta: {dmax-dmin}")
    return


def main():
    parser = argparse.ArgumentParser(description='Extract timings from soundfiles')
    parser.add_argument("filename", type=str, help="The file to be analyzed")
    parser.add_argument("-t", "--threshold", type=int, default=300,
                        help='The value that counts as not silence')
    parser.add_argument("-s", "--silence", type=int, default=300,
                        help='The length of silence before the end of the sound (in frames)')

    args = parser.parse_args()

    extract(args.filename, args.threshold, args.silence)

if __name__ == "__main__":
    main()

