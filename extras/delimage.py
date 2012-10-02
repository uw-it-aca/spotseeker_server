import getopt
import os
import sys

__doc__ = """
Script to delete images labeled by a number ID. This can be useful if only the
web server has permission to make changes to the directory where media is
uploaded.

Usage: 
    Deleting a range of image_ids: python delimage.py [path] [range] [ext]
    Deleting a single file: python delimage.py [path] [name]
    
Example: python delimage.py --path="/home/foo/bar/" --range="12-35" --ext=".jpg"
Example2: python delimage.py --path="test/" --name="foobar.jpg"

[path] is the relative or absolute path to the folder. Note: The arguments
    don't support the script living in the same folder as the images. Must
    also include trailing slash.
[range] is any range of numbers min-max.
[name] is the name of the image to delete.
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
            'ext=',
        ]
        options, args = getopt.getopt(sys.argv[1:], 'h', long_args)
    except getopt.error, msg:
        print msg
        print "for help use -h or --help"
        sys.exit(2)

    delimage(options)
    
def delimage(options):
    path = None
    ext = None
    min = None
    max = None
    name = None
    
    # Process arguments.
    for o, a in options:
        if o in ("-h", "--help", "help"):
            print __doc__
            sys.exit(0)
        
        if o == "--path":
            path = a
        elif o == "--range":
            temp = a.split("-")
            min = int(temp[0])
            max = int(temp[1])
        elif o == "--name":
            name = a
        elif o == "--ext":
            ext = a
    
    list_of_files = os.listdir(path)
    
    for f in list_of_files:
        file_name, extension = os.path.splitext(f)
        
        # Check delete by range parameters.
        if min and max:
            image_id = int(file_name)
            
            if image_id >= min and image_id <= max and extension == ext:
                os.remove(path + f)
                
        #  Check delete by name.
        elif name:
            full_name = file_name + extension
            
            if full_name == name:
                os.remove(path + f)
                
    
if __name__ == "__main__":
    main()
