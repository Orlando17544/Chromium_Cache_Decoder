''' Documentation: (I used 122.0.6253.1 because it will never change, I could have used main branch but it always changes)

    https://chromium.googlesource.com/chromium/src.git/+/refs/tags/122.0.6253.1/net/disk_cache/README.md
    https://chromium.googlesource.com/chromium/src.git/+/refs/tags/122.0.6253.1/net/disk_cache/simple/simple_entry_format.h
'''


import os
import struct
import re
from urllib.parse import urlparse

SIMPLE_INITIAL_MAGIC_NUMBER = '0xfcfb6d1ba7725c30'
SIMPLE_FINAL_MAGIC_NUMBER = '0xf4fa6f45970d41d8'

'''
    You can personalize:
        1.- The directory in which you want to make the search for the cache files.
        2.- The regex pattern to make the search.
'''

# Put the directory where the cache files are located
directory = '/home/orlando/.cache/BraveSoftware/Brave-Browser/Default/Cache/Cache_Data/'

# Inside this directory is going to be all of the cache files
os.mkdir('results')

count = 0
for filename in os.listdir(directory):
    path = os.path.join(directory, filename)
    if os.path.isfile(path):
        with open(path, "rb") as f:
            # Check if this file is a simple entry file, here I am reading only 8 bytes because the data type is uint64_t
            if SIMPLE_INITIAL_MAGIC_NUMBER == hex(struct.unpack("<Q", f.read(8))[0]):
                # Extract the remaining values of the SimpleFileHeader. version, key_length and key_hash are uint32_t, for that reason I read 12 bytes for those variables (null only contains \x00 values and it takes up 4 bytes)
                version, key_length, key_hash, null = struct.unpack("<LLLL", f.read(16))
                key = f.read(key_length).decode("UTF-8")
                if len(key) > 0:
                    remaining_data = f.read()
                    # Convert hexadecimal magic number to uint64_t in bytes
                    binary_simple_final_magic_number = struct.pack("<Q",int(SIMPLE_FINAL_MAGIC_NUMBER, 16))
                    data_with_trailer = remaining_data.split(binary_simple_final_magic_number)

                    # Only interested in files containing the data from stream 1
                    if len(data_with_trailer) == 3:
                        data_stream1 = data_with_trailer[0]

                        # Put the regex pattern you would like to search for
                        if re.search(r'\.jpg$', key):
                            url = key.split()[-1]
                            url = urlparse(url)
                            
                            if not os.path.isdir('results/' + url.hostname):
                                os.mkdir('results/' + url.hostname)

                            with open('results/' + url.hostname + '/' + str(count), "wb") as out:
                                out.write(data_stream1)

                            count += 1
