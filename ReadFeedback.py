#!/usr/bin/env python3

"""
Parses the feedback logfiles created by a BBB Instance and makes them humanly readable.
To enable feedback logs: https://docs.bigbluebutton.org/2.2/customize.html#collect-feedback-from-the-users
"""

__author__ = "Lukas Mahler"
__version__ = "0.2.2"
__date__ = "12.02.2020"
__email__ = "m@hler.eu"
__status__ = "Development"

import os
import csv
import glob
import gzip
import shutil
import argparse
from datetime import datetime


def parsefeedback(args):

    logspath = args.path
    parsezip = args.parsezip
    silent = args.silent

    data = []
    count = 1
    myrating = 0
    numratings = 0

    if not silent:
        print("[x] Started parsing feedback logs\n")

    # Find all rotated logfiles
    logs = glob.glob(logspath + "html5-client.log*")

    # No html5-client.log found
    if len(logs) == 0:
        raise FileNotFoundError("[x] No logfiles found")

    for log in logs:

        if not silent:
            print("({0}/{1}) parsed".format(count, len(logs)))

        unzipped = False
        if log.endswith(".gz"):
            if parsezip:
                with gzip.open(log, 'rb') as zipin:
                    with open(log[:-3], 'wb') as zipout:
                        shutil.copyfileobj(zipin, zipout)
                        log = zipout.name
                        unzipped = True
            else:
                continue

        with open(log, 'r') as readfile:
            for line in readfile:
                # Get good UTF-8 encoding
                line = bytes(line, encoding='latin1').decode('unicode_escape')
                line = bytes(line, encoding='latin1').decode('UTF-8')

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
                    name = "".join(line[start + 1:start + 3])
                    if "confname" in name:
                        # Not registered accounts will have "confname" in their name.
                        # Replace these with (temp)
                        name = name.replace("confname", " (temp)")

                # Split comment every 60 characters
                if "comment" in line:
                    start = line.index("comment") + 1
                    end = line.index("userRole")
                    c = "".join(line[start:end])

                    comment = ""
                    for i in range(len(c)):
                        if (i + 1) % 100 == 0:
                            comment += "\n" + " " * (60 - 3) + "| "
                        comment += c[i]

                # Add good comments to dict
                if "comment" in line:
                    data.append({
                        'timestamp': timestamp,
                        'rating': rating + " Stars",
                        'name': name,
                        'comment': comment,
                        'fullcmt': c
                    })

        # Delete unzipped files
        if unzipped:
            os.remove(log)

        count += 1

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


def print_parsed(data, rating):
    print("\n{0:15s}| {1:8s}| {2:30s}| Comment:".format("Timestamp:", "Rating:", "Author:"))
    print("=" * 160)
    for entry in data:
        print("{0:15}| {1:8}| {2:30s}| {3}".format(
            entry['timestamp'], entry['rating'], entry['name'], entry['comment']
        ))
    print("=" * 160)
    print("Median rating: {0} with {1} Votes".format(rating['median'], rating['num']))


def write_parsed(args, data, rating):
    logspath = args.path
    silent = args.silent

    writefile = logspath + "html5-client-readable.log"
    with open(writefile, 'w') as f:
        f.write("{0:15s}| {1:8s}| {2:30s}| Comment:\n".format("Timestamp:", "Rating:", "Author:"))
        f.write(("=" * 160) + "\n")
        for entry in data:
            f.write("{0:15}| {1:8}| {2:30s}| {3}\n".format(
                entry['timestamp'], entry['rating'], entry['name'], entry['comment']
            ))
        f.write(("=" * 160) + "\n")
        f.write("Median rating: {0} with {1} Votes".format(rating['median'], rating['num']))

    if not silent:
        print("\n-> Wrote to file: {0}".format(os.path.basename(writefile)))


def write_csv(args, data):
    logspath = args.path
    silent = args.silent

    writefile = logspath + "BBB-Feedback.csv"
    with open(writefile, 'w', newline='') as f:
        write = csv.writer(f)
        for entry in data:
            write.writerow([entry['timestamp'], entry['rating'], entry['name'], entry['fullcmt']])

    if not silent:
        print("\n-> Wrote to file: {0}".format(os.path.basename(writefile)))


# ======================================================================================================================

def main():
    # Parse cmd parameter
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', default='/var/log/nginx/',
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
