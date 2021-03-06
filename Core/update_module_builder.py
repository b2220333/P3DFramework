"""

RenderPipeline

Copyright (c) 2014-2015 tobspr <tobias.springer1@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
 	 	    	 	
"""

# This script downloads and updates the module builder.


from __future__ import print_function

import os
import sys

import zipfile
import shutil

# Import appropriate StringIO class
try: from cStringIO import StringIO as BytesIO
except:
    try: from StringIO import StringIO as BytesIO
    except:
        try: from io import BytesIO
        except: print("Could not import StringIO!")

class SubmoduleDownloader:

    """ Util class to download and extract (sub-)modules from github """

    @staticmethod
    def download_submodule(author, module_name, dest_path, ignore_list):
        """ Downloads a submodule from the given author and module name, and extracts
        all files which are not on the ignore_list to the dest_path.

        Example: download_submodule("tobspr", "RenderPipeline", ".", ["README.md", "LICENSE"])
         """

        # Make directory, if it does not exist yet
        if not os.path.isdir(dest_path):
            os.makedirs(dest_path)

        # Construct download url
        source_url = "https://github.com/" + author + "/" + module_name + "/archive/master.zip"
        prefix = module_name + "-master"
        print("Fetching:", source_url)

        try:
            # Python 2.7
            import urllib
            urlopen = urllib.urlopen

        except:
            
            # Python 3.4
            import urllib.request
            urlopen = urllib.request.urlopen

        # Download the zip
        try:
            usock = urlopen(source_url)
            zip_data = usock.read()
            usock.close()
        except Exception as msg:
            print("ERROR: Could not fetch module", module_name, "! Reason:", msg, file=sys.stderr)
            sys.exit(2)

        # Extract the zip
        zip_ptr = BytesIO(zip_data)

        try:
            zip_handle = zipfile.ZipFile(zip_ptr)
        except zipfile.BadZipfile:
            print("ERROR: Invalid zip file!", file=sys.stderr)
            sys.exit(3)

        if zip_handle.testzip() is not None:
            print("ERROR: Invalid zip file checksums!", file=sys.stderr)
            sys.exit(1)

        num_files, num_dirs = 0, 0

        for fname in zip_handle.namelist():
            rel_name = fname.replace(prefix, "").replace("\\", "/").lstrip("/")
            if not rel_name:
                continue

            is_file = not rel_name.endswith("/")
            rel_name = dest_path.rstrip("/\\") + "/" + rel_name

            # Files
            if is_file:
                for ignore in ignore_list:
                    if ignore in rel_name:
                        break
                else:
                    with zip_handle.open(fname, "r") as source, open(rel_name, "wb") as dest:
                        shutil.copyfileobj(source, dest)
                    num_files += 1
                            
            # Directories
            else:
                if not os.path.isdir(rel_name):
                    os.makedirs(rel_name)
                num_dirs += 1

        print("Extracted", num_files, "files and", num_dirs, "directories")


if __name__ == "__main__":

    # Main update script
    ignore = ("__init__.py LICENSE README.md config.ini "
        "Source/ExampleClass.cpp Source/ExampleClass.h Source/ExampleClass.I").split()
    import os
    import sys
    curr_dir = os.path.dirname(os.path.realpath(__file__)); os.chdir(curr_dir);
    SubmoduleDownloader.download_submodule("tobspr", "P3DModuleBuilder", curr_dir, ignore)
    with open("Scripts/__init__.py", "w") as handle: pass
    try: os.remove(".gitignore")
    except: pass
    os.rename("prefab.gitignore", ".gitignore")
