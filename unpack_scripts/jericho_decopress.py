# N.Kindt - Script to decompress files extracted from CBJ *.packed archive.
# Usage: python3 -path E:\Games\CBJ\Data03

import sys
import os
import struct
import zlib

pathname = ''
if "-path" in sys.argv:
    j = sys.argv.index("-path")
    try:
        pathname = sys.argv[j+1]
        if pathname[-1] != os.sep:
            pathname += os.sep
    except Exception as reason:
        print(reason)
        sys.exit(-1)
    
# Decompress files in extra directory
newdir = pathname + "_decompressed" + os.sep
try:
    if not os.path.isdir(newdir):
        os.mkdir(newdir)
except Exception as reason:
    print(reason)
    sys.exit(-2)

# Collect files in given directory
filelist = []
for (dirpath, dirnames, filenames) in os.walk(pathname):
    filelist.extend(filenames)
    break

done, failed = 0, 0
for file in filelist:
    filename = pathname + file
    with open(filename, 'rb') as f:
        done += 1
        # For now handle only first block in file (some files have multiple 78 9C blocks)
        size = struct.unpack('I', f.read(4))[0]
        magic = struct.unpack('H', f.read(2))[0]
        if magic != 40056:
            print(r'<?> %.4u/%.4u  Invalid magic:  %s  (Bytes: %u)  (skipped)' % (done, len(filelist), file, size))
            continue
        try:
            print(r'%.4u/%.4u  Unpacking:  %s  (Bytes: %u)' % (done, len(filelist), file, size))
            bytes = f.read(size - 6)
            data = zlib.decompress(bytes, -15)
        except Exception as reason:
            failed += 1
            print(r'<!> %.4u/%.4u  Failed:  %s  (Bytes: %u)   (%s)' % (done, len(filelist), file, size, reason))
            continue
        
        if file.endswith(".dds1"):
            file = file[:-1]
        with open(newdir + file, 'wb') as w:
            w.write(data)
print("Done. Unpacked: %u;  Failed: %u" % (done, failed))