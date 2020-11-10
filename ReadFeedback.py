#!/usr/bin/env python3

"""
Parses the feedback logfiles created by a BBB Instance and make them humanly readable.
To enable feedback logs: https://docs.bigbluebutton.org/2.2/customize.html#collect-feedback-from-the-users
"""

__author__ = "Lukas Mahler"
__version__ = "0.1.0"
__date__ = "10.11.2020"
__email__ = "m@hler.eu"
__status__ = "Development"


import os
import glob
import gzip
import shutil
import argparse


def parsefeedback(logspath, log2file=False, parsezip=False, silent=False):
    myrating = 0
    numratings = 0

    if not silent:
        print("[x] Started parsing feedback logs\n")

    # Find all rotated logfiles
    logs = glob.glob(logspath + "html5-client.log*")
    writefile = logspath + "html5-client-readable.log"

    if log2file:
        openmode = 'w'
    else:
        openmode = 'a'

    with open(writefile, openmode) as writefile:

        txt = "Rating: | Author:                   | Comment:\n"
        if log2file:
            writefile.write(txt + "=" * 140)
        if not silent:
            print(txt + "=" * 140)

        if log2file:
            writefile.write(txt + "=" * 140)

        for log in logs:
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

                    # Read out the commenters name
                    if "fullname" in line:
                        start = line.index("fullname")
                        name = "".join(line[start + 1:start + 3])

                    # Split comment on 100 characters
                    if "comment" in line:
                        start = line.index("comment") + 1
                        end = line.index("userRole")
                        comment = "".join(line[start:end])

                        c = ""
                        for i in range(len(comment)):
                            if (i + 1) % 100 == 0:
                                c += "\n" + " " * 36 + "| "
                            c += comment[i]

                    # Read out the given rating
                    if "rating" in line:
                        start = line.index("rating")
                        rating = "".join(line[start + 1:start + 2])

                        myrating = myrating + int(rating)
                        numratings += 1

                    # Only print & write out lines with a comment
                    if "comment" in line:
                        txt = "{0} Stars | {1:25s} | {2}\n".format(rating, name, c)
                        if log2file:
                            writefile.write(txt)
                        if not silent:
                            print(txt, end="")

            # Delete unzipped files
            if unzipped:
                os.remove(log)

        # No ratings were given yet
        try:
            redurating = round(myrating / numratings, 2)
        except ZeroDivisionError:
            redurating = 0

        txt = "\nTotal Rating: {0} on {1} Votes".format(redurating, numratings)
        if log2file:
            writefile.write("=" * 140 + txt)

        if not silent:
            print("=" * 140 + txt)
            print("\n[x] Finished parsing feedback logs")

            if log2file:
                print("[x] Wrote to file: {0}".format(writefile.name))


if __name__ == "__main__":

    # Parse cmd parameter
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', default='/var/log/nginx/',
                        help='Provide the full path to the directory containing the feedback logs')
    parser.add_argument('-s', '--silent', action='store_true',
                        help="If True the script won't have any output")
    parser.add_argument('-tf', '--tofile', action='store_true',
                        help='If True write the output to `html5-client-readable.log`')
    parser.add_argument('-pz', '--parsezip', action='store_true',
                        help='If True unzip .gz logs and parse them aswell')
    args = parser.parse_args()

    # Execute feedback parsing
    parsefeedback(args.path, log2file=args.tofile, parsezip=args.parsezip, silent=args.silent)
