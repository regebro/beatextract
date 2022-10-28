import argparse


def extract(filename):
    last = 0
    distances = []
    with open(filename) as file:
        for line in file.readlines():
            fields = line.split()
            if "Timing" not in fields:
                continue
            timestamp = int(fields[0], base=16)
            if last == 0:
                last = timestamp
                continue
            delta = timestamp - last
            distances.append(delta)
            print(delta)
            last = timestamp

    dmin = min(distances)
    dmax = max(distances)
    avg = sum(distances) // len(distances)
    print(f"Minimum: {dmin}  Maximum: {dmax} Average: {avg} Delta: {dmax-dmin}")


def main():
    parser = argparse.ArgumentParser(
        description="Extract MIDI clock timings from MIDIOX logs"
    )
    parser.add_argument("filename", type=str, help="The file to be analyzed")
    args = parser.parse_args()

    extract(args.filename)


if __name__ == "__main__":
    main()
