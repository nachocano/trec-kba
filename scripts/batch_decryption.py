#!/usr/bin/python
import os
import sys
import subprocess
import argparse
import time

def decrypt(filename):
    gpg_child = subprocess.Popen(
        ['/usr/bin/gpg', '--output', filename[:-4], '--decrypt', filename],
        stderr=subprocess.PIPE)
    gpg_child.communicate()
    os.remove(filename)

def main():
    parser = argparse.ArgumentParser(description='TODO')
    parser.add_argument('-i', '--input_dir', required=True)
    args = parser.parse_args()

    start = time.time()
    date_hour_list = os.listdir(args.input_dir)
    left = len(date_hour_list)
    for date_hour in date_hour_list:
        print '%d folders left...' % left
        print '#### starting decrypting folder %s' % date_hour
        date_hour_path = os.path.join(args.input_dir, date_hour)
        if not os.path.isdir(date_hour_path):
            print '%s is not dir' % date_hour_path
            continue
        for chunk_file_name in os.listdir(date_hour_path):
            to_decrypt = os.path.join(date_hour_path, chunk_file_name)
            if to_decrypt.rfind('xz.gpg') != -1:
                print 'decrypting %s' % chunk_file_name
                decrypt(to_decrypt)
        print '#### finished decrypting folder %s' % date_hour
        left -= 1

    print 'decryption took %s' % (time.time() - start)

if __name__ == '__main__':
    main()
