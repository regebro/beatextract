import argparse
import math
import statistics
import struct
import sys
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
        raise RuntimeError(f"Sorry, this script does not support a sample width of {width}")

    sample_values = []
    for i in range(sound.getnframes()):
        frame = sound.readframes(1)[:width]
        sample = struct.unpack(samp_struct, samp_prefix + frame)[0] // samp_divisor
        sample_values.append(sample)

    return sample_values


def find_sound(value_gen, threshold, resolution):
    while True:
        try:
            while True:
                pos, value = next(value_gen)
                #print(pos, value)
                if abs(value) >= threshold:
                    break
        except StopIteration:
            raise StopIteration(pos)
            
        while True:
            # This could be sound, find silence:
            spos = find_silence(value_gen, threshold, resolution)
            if spos - pos > 10:
                # OK, that's a sound
                return pos
        
        
def find_silence(value_gen, threshold, resolution):
    while True:
        try:           
            while True:
                # Find a section below the threshold
                pos, value = next(value_gen)
                #print(pos, value)
                if abs(value) < threshold:
                    break
        except StopIteration:
            raise StopIteration(pos)
        
        try:
            # Make sure it's long enough to count as silence:
            while True:
                spos, value = next(value_gen)
                #print(pos, value)
                if abs(value) >= threshold:
                    # That wasn't long enough to be silence, so we continue looking
                    break
    
                if spos - pos > resolution:
                    # Yes, this is silence
                    return pos
        except StopIteration:
            raise StopIteration(spos)
        

def chunk(values, size):
    num = math.ceil(len(values) / size)

    i = 0
    while i < num:
        j = i + 1
        yield values[size * i : size * (j)]
        i = j


def absmax(values):
    """Returns the maximum value, ignoring signs"""
    # Not sure if this is faster, or if abs() on each value is faster
    return max(max(values), -min(values))


def analyze_levels(values, resolution):
    # Average out blocks
    blocks = [absmax(each) for each in chunk(values, resolution)]
    # This assumes most of the audio is silence. In practice it seems
    # a good value for noise floor is twice the median.
    noisefloor = math.floor(statistics.median(blocks) * 2)
    # Peak level
    peak = max(blocks)
    return noisefloor, peak


def extract(sound, threshold, resolution, beats):
    print("Loading...")
    try:
        values = load(sound)
    except RuntimeError as e:
        print(e.args[0])
        
    print(f"Found {8*sound.getsampwidth()} bit sound file with {len(values)} samples")

    if threshold == 0:
        # Analyze file for audio levels. Put the threshold somewhere in the
        # middle, because that's going to be the fastest changing point, and
        # gives the most accurate results.
        threshold = sum(analyze_levels(values, resolution))/2
        print(f"Using {threshold} for trigger threshold")

    value_gen = iter(enumerate(values))

    # Skip silence
    print("Looking...")
    sound_starts = []
    try:
        while True:
            pos = find_sound(value_gen, threshold, resolution)
            sound_starts.append(pos)
            print(".", end="")
    
            # Now look for silence
            find_silence(value_gen, threshold, resolution)
            # And then for a new sound
            continue
    except StopIteration as e:
        # Check that we did iterate to the end
        assert e.args[0] == sound.getnframes() - 1
    
    if len(sound_starts) < 2:
        print(
            f"No sounds found with threshold {threshold} and min {resolution} samples of silence."
        )
        sys.exit(1)
               
    prev = sound_starts[0]
    distances = []
    for pos in sound_starts[1:]:
        d = pos - prev
        distances.append(d)
        prev = pos

    if beats > 1:
        if len(distances) < 2 * beats:
            print(
                f"Did not find enough sounds to group them into groups of {beats}."
            )
        distances = [sum(chunk) for chunk in zip(*[iter(distances)]*beats)]

    return distances


def print_stats(sound, distances):
    print("Done! Found with the following distances")
    [print(x) for x in distances]


    dmin = min(distances)
    dmax = max(distances)
    avg = sum(distances) // len(distances)
    print(f"Minimum: {dmin}  Maximum: {dmax} Average: {avg} Delta: {dmax-dmin}")
    stddev = statistics.pstdev(distances)
    milliseconds = (stddev * 1000) / sound.getframerate()
    print(f"The standard deviation is {milliseconds} ms")

    # Split into x groups
    numgroups = 11
    gwidth = 2 * (max([dmax, dmin]) - avg) / numgroups
    groups = [int((x - dmin) // gwidth) for x in distances]
    maxcount = max(groups.count(i) for i in range(numgroups))
    scale = max(maxcount/80, 1)
    
    print()
    print("Distribution:")
    for i in range(numgroups):
        print("#" * int(groups.count(i) / scale))

    return


def main():
    parser = argparse.ArgumentParser(description="Extract timings from soundfiles")
    parser.add_argument("filename", type=str, help="The file to be analyzed")
    parser.add_argument(
        "-t",
        "--threshold",
        type=int,
        default=0,
        help="The noise floor threshold (the value that counts as a sound)",
    )
    parser.add_argument(
        "-r",
        "--resolution",
        type=int,
        default=0,
        help="The length of silence before the end of the sound (in samples)",
    )
    parser.add_argument(
        "-b",
        "--beats",
        type=int,
        default=1,
        help="The amount of ticks that counts as one beat",
    )

    args = parser.parse_args()

    sound = wave.open(args.filename, "rb")

    if sound.getnchannels() != 1:
        print("This script only supports mono sounds, in stereofiles on channel 1 is used")

    resolution = args.resolution
    if resolution == 0:
        # Default to using a resolution that is larger than the wavelenghth of
        # a 20 Hz wave, so that really low bassnotes doesn't confuse the analysis
        resolution = math.floor(sound.getframerate() / 20)
        print(f"Using {resolution} samples for silence detection")

    distances = extract(sound, args.threshold, resolution, args.beats)
    print_stats(sound, distances)


def debugproc():
    import csv
    parser = argparse.ArgumentParser(description="WTF is going on, really?")
    parser.add_argument("filename", type=str, help="The file to be analyzed")
    args = parser.parse_args()

    with open("soundextract.csv", "wt", newline='') as outfile:
        csvwriter = csv.writer(outfile, delimiter='\t')
        resolution = math.floor(48000 / 20)
        
        thresholds = [350, 400, 424, 450, 500, 1000, 10000, 100000, 1000000]
        
        csvwriter.writerow(thresholds)
        
        results = []
        for threshold in thresholds:
            sound = wave.open(args.filename, "rb")
            distances = extract(sound, threshold, resolution)
            results.append(distances)
        
        import itertools
        res = itertools.zip_longest(*results)
        csvwriter.writerows(res)
    

if __name__ == "__main__":
    main()
    #debugproc()
