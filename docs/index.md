# Data file manifest generator: mgen

## Overview

This is a simple utility which creates file manifests in a variety of formats. A created manifest includes, for all file types:

* Checksum in your choice of hash for the file. Current flavours of hashes are: sha1, sha224, sha256, sha384, sha512, blake2b, blake2s, md5 

For **plain text files**, often used for microdata, the utility also produces information on:

* Minimum line length
* Maximum line length
* Number of records
* Constant records flag (ie, all lines are of the same length)
* Row and column of non-ASCII characters
* Flag for DOS/Windows formatting (ie, carriage return + line feed as opposed to just a line feed).

Output formats are:

* Plain text
* Comma Separated Value (ie, a spreadsheet)
* JSON. This JSON doesn't conform to any particular standard, but is valid JSON object — one object for all the files.
 
## Obtaining the software/installation

The software is written in Python (>= 3.6), and the source is available as a single file in `mgen.py`. If you have Python3 installed you can either just download that single file to a place of convenience, or you can install it as a Python library by running the following commands in a terminal:

```
git clone https://github.com/ubc-library-rc/mgen.git
cd mgen 
pip install .
```

This second method will allow you to use the mgen.Checker class in your own projects. If you don't care about that, just download a binary or use the Python file directly.

Console binaries are available for Windows and Mac (Intel) in the `binaries` directory.

## How to use mgen

Currently, this utility works as a *console* utility, ie. a Windows command prompt or terminal is required for use.

**If using the binary, and the binary is in your $PATH**

`mgen [options]`


**If using Python, invoke the utility with:**

`python3 /path/to/mgen.py [options]`

Note that on Windows this means something like:

`python3 C:\path\to\mgen.py [options]`

**Outputting to a file**

By default, the program will spit its results to the screen (stdout). To send the output to a file, run the utility and pipe the output to a file. For example:

`mgen -o csv -r ./ > C:\temp\output.csv`

#### Program options

```
usage: mgen.py [-h] [-v] [-o OUT] [-n] [-r] [-t DIGEST] files [files ...]

Produces a text, csv or JSON output with checksums for files, testing for Windows CRLF combinations, as well as checking text files for regularity and non/ASCII characters

positional arguments:
  files                 Files to check. Wildcards acceptable (eg, *)

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         Show version number and exit
  -o OUT, --output OUT  Output format. One of txt, csv, json
  -n, --no-flat         Don't check text files for rectangularity
  -r, --recursive       Recursive *directory* processing of file tree. Assumes that the arguments point to a directory (eg, tmp/), and a slash will be appended if one does not exist
  -t DIGEST, --hash-type DIGEST
                        Checksum hash type. Supported hashes: 'sha1', 'sha224', 'sha256', 'sha384', 'sha512', 'blake2b', 'blake2s', 'md5'. Default: 'md5'
```

## Compiling the software on your platform

You can compile the software on your own platform with [PyInstaller](https://pyinstaller.readthedocs.io/en/stable/)

`pyinstaller -F mgen.py`

or 

`python3 -m PyInstaller -F mgen.py`
