#!/usr/bin/env python3

"""
Parses the feedback logfiles created by a BBB Instance and makes them humanly readable.
To enable feedback logs: https://docs.bigbluebutton.org/admin/customize.html#collect-feedback-from-the-users
"""

__author__ = "Lukas Mahler"
__version__ = "0.3.1"
__date__ = "26.09.2022"
__email__ = "m@hler.eu"
__status__ = "Development"

import csv
import gzip
import shutil
import textwrap
from pathlib import Path
from datetime import datetime
from typing import Tuple, Dict, List
from argparse import ArgumentParser, Namespace


def parsefeedback(args: Namespace) -> Tuple[List[Dict], Dict]:

    logspath = args.path
    parsezip = args.parsezip
    silent = args.silent

    data = []
    myrating = 0
    numratings = 0

    if not silent:
        print("[x] Started parsing feedback logs\n")

    # Find all (rotated) logfiles
    logs = list(logspath.glob("html5-client.log*"))

    # No html5-client.log found
    if len(logs) == 0:
        raise FileNotFoundError("[x] No logfiles found")

    for index, log in enumerate(logs):

        if not silent:
            print(f"[{index+1}/{len(logs)}] parsed")

        unzipped = False
        if log.suffix == ".gz":
            if parsezip:
                with gzip.open(log, 'rb') as zipin:
                    with open(log.with_suffix(''), 'wb') as zipout:
                        shutil.copyfileobj(zipin, zipout)
                        log = Path(zipout.name)
                        unzipped = True
            else:
                continue

        with open(log, 'r') as readfile:
            for line in readfile:
                # Get good UTF-8 encoding
                line = bytes(line, encoding='latin1').decode('unicode_escape')

                # Skip empty lines
                try:
                    line = line.split(r" [")[2][:-2]
                except IndexError:
                    continue

                # String formatting
                line = line.replace(r"\n", " ")
                line = line.replace("}", "")
                line = line.replace("{", "")
                line = line.replace(",", ":")
                line = line.replace('"', '')
                line = line.split(":")

                # Read the timestamp
                if "time" in line:
                    start = line.index("time")
                    time = "".join(line[start + 1:start + 3])
                    timestamp = datetime.strptime(time, "%Y-%m-%dT%H%M").strftime("%d.%m.%y %H:%M")

                # Read the given rating
                if "rating" in line:
                    start = line.index("rating")
                    rating = "".join(line[start + 1:start + 2])

                    myrating = myrating + int(rating)
                    numratings += 1

                # Read the commenters name
                if "fullname" in line:
                    start = line.index("fullname")
                    name = ",".join(line[start + 1:start + 3])
                    name = bytes(name, encoding='latin1').decode('UTF-8')
                    if "confname" in name:
                        # Non registered accounts will have "confname" in their name.
                        # Replace these with (temp)
                        name = name.replace(",confname", " (temp)")

                # Split comment every 100 characters
                if "comment" in line:
                    start = line.index("comment") + 1
                    end = line.index("userRole")
                    raw_comment = "".join(line[start:end])
                    raw_comment = bytes(raw_comment, encoding='latin1').decode('UTF-8')

                    comment = f"\n{'':15s}│ {'':8s}│ {'':30s}│ ".join(textwrap.wrap(raw_comment, 100))

                # Add good comments to dict
                if "comment" in line:
                    data.append({
                        'timestamp': timestamp,
                        'rating': rating + " Stars",
                        'name': name,
                        'comment': comment,
                        'raw_comment': raw_comment
                    })

        # Delete unzipped files
        if unzipped:
            log.unlink()

    # Sort data by timestamp
    sorted_data = sorted(data, key=lambda k: datetime.strptime(k['timestamp'], "%d.%m.%y %H:%M"))

    # Calculate rating_data
    if numratings == 0:
        median = 0
    else:
        median = round(myrating/numratings, 2)
    rating_data = {'num': numratings, 'median': median}

    if not silent:
        print("\n[x] Finished parsing feedback logs")

    return sorted_data, rating_data


def print_parsed(data: List[Dict], rating: Dict) -> None:
    print(f"\n{'Timestamp:':15s}│ {'Rating:':8s}│ {'Author:':30s}│ Comment:")
    print(f"{15*'─'}┼{9*'─'}┼{31*'─'}┼{102*'─'}")
    lastline = len(data)-1
    for index, entry in enumerate(data):
        print(f"{entry['timestamp']:15}│ {entry['rating']:8}│ {entry['name']:30s}│ {entry['comment']}")
        if index != lastline:
            print(f"{15 * '─'}┼{9 * '─'}┼{31 * '─'}┼{102 * '─'}")
        else:
            print(f"{15 * '─'}┴{9 * '─'}┴{31 * '─'}┴{102 * '─'}\n")
    print(f"Median rating: {rating['median']} with {rating['num']} Votes\n")


def write_parsed(args: Namespace, data: List[Dict], rating: Dict) -> None:
    logspath = args.path
    silent = args.silent

    writefile = logspath / "html5-client-readable.log"
    with open(writefile, 'w', encoding='UTF-8') as f:
        f.write(f"{'Timestamp:':15s}│ {'Rating:':8s}│ {'Author':30s}│ Comment:\n")
        f.write(f"{15*'─'}┼{9*'─'}┼{31*'─'}┼{102*'─'}\n")
        lastline = len(data) - 1
        for index, entry in enumerate(data):
            f.write(f"{entry['timestamp']:15}│ {entry['rating']:8}│ {entry['name']:30s}│ {entry['comment']}\n")
            if index != lastline:
                f.write(f"{15 * '─'}┼{9 * '─'}┼{31 * '─'}┼{102 * '─'}\n")
            else:
                f.write(f"{15 * '─'}┴{9 * '─'}┴{31 * '─'}┴{102 * '─'}\n")
        f.write(f"Median rating: {rating['median']} with {rating['num']} Votes")

    if not silent:
        print(f"→ Wrote to file: {writefile.name}")


def write_csv(args: Namespace, data: List[Dict]) -> None:
    logspath = args.path
    silent = args.silent

    writefile = logspath / "BBB-Feedback.csv"
    with open(writefile, 'w', encoding='UTF-8', newline='') as f:
        write = csv.writer(f)
        for entry in data:
            write.writerow([entry['timestamp'], entry['rating'], entry['name'], entry['raw_comment']])

    if not silent:
        print(f"→ Wrote to file: {writefile.name}")


# ======================================================================================================================

def main():

    # Parse cmd parameter
    parser = ArgumentParser()
    parser.add_argument('-p', '--path', default='/var/log/nginx/', type=Path,
                        help='Provide the full path to the directory containing the feedback logs')
    parser.add_argument('-s', '--silent', action='store_true',
                        help="If True the script won't have any output")
    parser.add_argument('-tf', '--tofile', action='store_true',
                        help='If True parse the output to `html5-client-readable.log`')
    parser.add_argument('-csv', action='store_true',
                        help='If True parse the output into `feedback.csv`')
    parser.add_argument('-pz', '--parsezip', action='store_true',
                        help='If True unzip .gz logs and parse them aswell')
    args = parser.parse_args()

    silent = args.silent

    # Execute feedback parsing
    data, rating = parsefeedback(args)
    if not silent:
        print_parsed(data, rating)
    if args.tofile:
        write_parsed(args, data, rating)
    if args.csv:
        write_csv(args, data)


if __name__ == "__main__":
    main()
