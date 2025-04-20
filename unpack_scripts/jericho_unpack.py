# N.Kindt - Script to extract all files from CBJ *.packed archive.
# Usage: python3 -file E:\Games\CBJ\Data00.packed

import sys
import os
import struct

filename = ''
if "-file" in sys.argv:
    j = sys.argv.index("-file")
    try:
        filename = sys.argv[j+1]
    except Exception as reason:
        print(reason)
        sys.exit(-1)

with open(filename, 'rb') as f:
    header = f.read(8)
    numfiles = struct.unpack('i', f.read(4))[0]
    dirname = os.path.splitext(filename)[0]
    try:
        if not os.path.isdir(dirname):
            os.mkdir(dirname)
    except Exception as reason:
        print(reason)
        sys.exit(-2)

    for i in range(0, numfiles):
        strlen = struct.unpack('i', f.read(4))[0]
        name = f.read(strlen).decode()
        name = name.split('/')[-1]
        size = struct.unpack('i', f.read(4))[0]
        offset = struct.unpack('i', f.read(4))[0]
        pos = f.tell()
        f.seek(offset)
        bytes = f.read(size)
        f.seek(pos)
        with open(dirname + os.sep + name, 'wb') as w:
            w.write(bytes)
            print("%.4u/%.4u - %s (Bytes: %u)" % (i+1, numfiles, name, size))