#!/usr/bin/env python2.6
# encoding: utf-8
#
# Copyright (c) 2013 Aerys. All rights reserved.
# Created by Warren Seine on Apr 05, 2013.

import getopt
import sys
import os
import shutil
import subprocess
import tempfile

VERBOSE = 0
MAX_QUALITY = "18"
FORMAT = "jpg"


def error(text, code=0):
    if VERBOSE >= 1:
        sys.stderr.write("%s: %s\n" % (os.path.basename(sys.argv[0]), text))
    if code:
        sys.exit(code)


def download(video, directory):
    return subprocess.call([
        sys.executable,
        "./youtube-dl",
        video,
        "-v" if VERBOSE >= 1 else "-q",
        "--max-quality", MAX_QUALITY,
        "-o", os.path.join(directory, "%(id)s.%(ext)s")
    ])


def thumbnailize(video, offset, duration, size, framerate, format, source, destination):
    try:
        os.makedirs(destination)
    except:
        pass

    return subprocess.call([
        "ffmpeg",
        "-loglevel", "info" if VERBOSE >= 1 else "panic",
        "-ss", offset,
        "-i", os.path.join(source, video + ".mp4"),
        "-t", duration,
        "-r", framerate,
        "-vf", "scale=-1:" + size.split("x")[1],
        "-vf", "crop=" + size.replace("x", ":"),
        os.path.join(destination, "%08d." + format)
    ])


def convert(video, destination, offset, duration, framerate, size):
    source = tempfile.mkdtemp(suffix=video)

    if download(video, source) != 0:
        return False

    if thumbnailize(video, offset, duration, size, framerate, FORMAT, source, destination) != 0:
        return False

    shutil.rmtree(source)

    if VERBOSE >= 1:
        print("YouTube video %s successfully converted" % (video))

    return True


def main():
    usage = "usage: youtube-to-web-anim [--verbose n] [--offset o] [--duration d] [--size s] [--framerate f] youtube-id output-dir"

    try:
        opts, args = getopt.getopt(sys.argv[1:], "v:o:d:s:f:", ["verbose=", "offset=", "duration=", "size=", "framerate="])

        if len(args) != 2:
            error(usage, 2)

        global VERBOSE

        offset = "00:00:00"
        duration = "00:00:05"
        size = "256x256"
        framerate = "10"
        video = args[0]
        destination = args[1]

        for o, a in opts:
            if o in ("-v", "--verbose"):
                VERBOSE = int(a)
            elif o in ("-o", "--offset"):
                offset = a
            elif o in ("-d", "--duration"):
                duration = a
            elif o in ("-s", "--size"):
                size = a
            elif o in ("-f", "--framerate"):
                framerate = a
            else:
                error("unhandled option", 2)

        return convert(video, destination, offset, duration, framerate, size)

    except (ValueError, getopt.GetoptError) as e:
        if VERBOSE >= 1:
            error(e)
            error(usage, 2)
        return False


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
