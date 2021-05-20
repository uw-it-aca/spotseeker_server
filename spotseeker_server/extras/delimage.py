# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

""" Copyright 2012, 2013 UW Information Technology, University of Washington

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

import getopt
import os
import sys
import re

__doc__ = """
Script to delete images labeled by a number ID. This can be useful if only the
web server has permission to make changes to the directory where media is
uploaded.

Usage:
    Deleting a range of image_ids: python delimage.py [path] [range] [ext]
    Deleting a named range of images: python delimage.py [path] [name-prefix]
                                      [range] [ext]
    Deleting a single file: python delimage.py [path] [name]

Example: python delimage.py --path="/home/foo/bar/" --range="12-35"
         --ext=".jpg"
Example: python delimage.py --path="/home/foo/bar/" --name-prefix="image-"
         --range="12-35" --ext=".jpg"
Example: python delimage.py --path="test/" --name="foobar.jpg"

[path] is the relative or absolute path to the folder. Note: The arguments
    don't support the script living in the same folder as the images. Must
    also include trailing slash.
[range] is any range of numbers min-max.
[name] is the name of the image to delete.
[name-prefix] is the text prefix to an otherwise numbered range. For example,
    'image-345.jpg' would have a name-prefix of 'image-'. Requires a range to
    be passed.
[ext] is the extension of the image file(s).
"""


def main():
    # Get arguments
    try:
        long_args = [
            'help',
            'path=',
            'range=',
            'name=',
            'name-prefix=',
            'ext=',
        ]
        options, args = getopt.getopt(sys.argv[1:], 'h', long_args)
    except getopt.error, msg:
        print(msg)
        print("for help use -h or --help")
        sys.exit(2)

    delimage(options)


def delimage(options):
    path = None
    ext = None
    min = None
    max = None
    name = None
    prefix = None

    # Process range first as it's required for name-prefix
    for o, a in options:
        if o == "--range":
            temp = a.split("-")
            min = int(temp[0])
            max = int(temp[1])
    # Process the rest of the arguments.
    for o, a in options:
        if o in ("-h", "--help", "help"):
            print(__doc__)
            sys.exit(0)
        if o == "--path":
            path = a
        elif o == "--name":
            name = a
        elif o == "--name-prefix":
            if not min or not max:
                print("--name-prefix requires a range")
                print(__doc__)
                sys.exit(0)
            else:
                prefix = a
        elif o == "--ext":
            ext = a

    list_of_files = os.listdir(path)

    for f in list_of_files:
        file_name, extension = os.path.splitext(f)
        image_id = None

        # Check delete by range parameters.
        if min and max and prefix:
            numsearch = re.search(r'(\d+)', file_name)
            if numsearch:
                image_id = int(numsearch.group(0))
        elif min and max:
            image_id = int(file_name)

            if image_id >= min and image_id <= max and extension == ext:
                os.remove(path + f)

        # Check name-prefix.
        if prefix and image_id:
            image_name = prefix + str(image_id)

            if image_name == file_name:
                os.remove(path + f)

        #  Check delete by name.
        elif name:
            full_name = file_name + extension

            if full_name == name:
                os.remove(path + f)


if __name__ == "__main__":
    main()
