#!/usr/bin/env python

"""
    Written by Tony Sangha - Nov 2015
    Github: https://github.com/tonysangha
    Blog: http://tonysangha.com

    * Script to save images received via iMessage on your MAC *

    Tested on OSX Yosemite and El Capitan
    Tested with Python 2.7.10
"""

import os
import sys
import hashlib
import shutil
import exifread
from datetime import datetime
from random import randint

# Declare empty dictionary/lists for use later in the code
src_dict = {}  # Store all files in source
dst_dict = {}  # Store all files in destination
non_exif_filenames = []  # Store FileNames without DateTime EXIF TAG
# Path to iMessage directory, based upon User Log
path = "/Users/" + os.getlogin() + "/Library/Messages/Attachments/"

def md5(fname):
    """ 
    return HASH value for file 
    """
    hash = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash.update(chunk)
    return hash.hexdigest()

def image_Type(rawname):
    """ 
    Return the File Extension 
    """
    return os.path.splitext(rawname)[1]

def rename_pics(filename, rawName):
    """ 
    If the file contains the EXIF tags for DateTime, use tag to
    rename picture, otherwise just return the original filename with a 
    random prefix to help in the event there are duplicate filenames but
    hash value differs 
    """
    f = open(filename, 'rb')
    processed = exifread.process_file(f)
    stripped = str(processed.get('Image DateTime'))
    if processed.get('Image DateTime') is not None:
        dt = datetime.strptime(stripped, '%Y:%m:%d %H:%M:%S')
        return '{2:02}-{1}-{0}_{03}.{04}.{05}'.format(dt.day, dt.month,
                                                      dt.year, dt.hour,
                                                      dt.minute, dt.second) \
                                                      + imageType(rawName)
    else:
        return str(randint(0, 999999)) + "-" + rawName

def populate_dict(directory, diction):
    """ 
    Method injests a directiory and creates a dictionary to represent
    the contents of the directory. The HASH value (unique) is used as the
    dictionary key and filename and path as values associated to the key 
    """
    for root, dirs, files in os.walk(directory):
        for name in files:
            if str(name).endswith((".jpg", ".JPEG", ".JPG", ".PNG", ".png")):
                newName = rename_pics(os.path.abspath(os.path.join
                                                     (directory, root, name)),
                                     name)
                diction[md5(os.path.abspath(os.path.join(directory, 
                            root, name)))] = name, \
                    os.path.abspath(os.path.join(directory, root, name)), \
                    newName
    return diction

def rename(oldName, newName, destination):
    """ 
    Rename the files in the destination 
    """
    return os.rename((destination) + "/" + str(oldName), (destination) + "/"
                     + str(newName))

def copy_files(destination):
    """ 
    Execute copy function of files 
    """
    for x in range(len(src_dict)):
        if src_dict.keys()[x] in dst_dict:
            pass
        else:
            shutil.copy(src_dict.values()[x][1], destination)
            rename(
                   src_dict.values()[x][0], src_dict.values()[x][2], destination)

def main(argv):
    populate_dict(path, src_dict)
    populate_dict(argv[1], dst_dict)
    copy_files(argv[1])

if __name__ == "__main__":
    main(sys.argv)
