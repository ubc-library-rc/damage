#Data file manifest generator

## Overview

This is a (very) simple utility which creates a file manifest in a variety of formats. The manifest includes:

* Checksum in md5 or sha1 for the file [note: md5 only implemented as of 23 Feb 2021]

For text files, often used for microdata, the utility also produces information on:

* Minimum line length
* Maximum line length
* Number of records
* Constant records flag (ie, all lines are of the same length)
* Row and column of non-ASCII characters
* Flag for DOS/Windows formatting (ie, carriage return + line feed as opposed to just a line feed).

Output formats are:

* Plain text
* Comma Separated Value (ie, a spreasheet)
* JSON (experimental). This JSON doesn't conform to any particular standard.


## Obtaining the software

The software is written in Python (>= 3.6), and the source is available as a single file in `stc_manifest_generator.py`

Console binaries are available for Windows and Mac (Intel) in the `binaries` directory.

### Usage

Currently, this utility works as a *console* utility, ie. a Windows command prompt or terminal is required for use.

**If using the binary, and the binary is in your $PATH**

`stcman [options]`


**If using Python, invoke the utility with:**

`python3 /path/to/stc_manifest_generator.py [options]`

Note that on Windows this means something like:

`python3 C:\path\to\stc_manifest_generator.py [options]`

**Outputting to a file**

By default, the program will spit its results to the screen. To send the output to a file, run the utility and pipe the output to a file. For example:

`stcman -o csv -r ./ > C:\temp\output.csv`

####Program options

```
usage: stc_manifest_generator.py [-h] [-o OUT] [-n] [-r] files [files ...]

Produces a text, csv or JSON output with md5 or sha1 sums for files, testing for Windows CRLF combinations, as well as checking text files for regularity and non/ASCII characters

positional arguments:
  files                 Files to check. Wildcards acceptable (eg, *)

optional arguments:
  -h, --help            show this help message and exit
  -o OUT, --output OUT  Output format. One of txt, csv, json
  -n, --no-flat         Don't check text files for rectangularity
  -r, --recursive       Recursive *directory* processing of file tree. Assumes that the arguments point to a directory (eg, tmp/), and a slash will be appended if one does not exist
```

## Compiling the software on your platform

You can compile the software on your own platform with [PyInstaller](https://pyinstaller.readthedocs.io/en/stable/)

`pyinstaller -F stc_manifest_generator.py`

or 

`python3 -m PyInstaller -F stc_manifest_generator.py`



