# How to use the damage console utility

Documentation is for the  *console* utility. That means a Windows command prompt or terminal is required for use. The console utility is normally referred to with a lowercase initial 'd' (ie, **damage**) and the full GUI application as **Damage**

**If you have installed the fcheck module with _pip_**

`damage.py [options]`

**If using the binary, and the binary is in your $PATH**

`damage [options]`

**If using Python directly from the source code, invoke the utility with:**

`python3 /path/to/damage.py [options]`

Note that on Windows this means something like:

`python3 C:\path\to\damage.py [options]`

**Outputting to a file**

By default, the program will spit its results to the screen (stdout). To send the output to a file, run the utility and pipe the output to a file. For example:

`damage -o csv -r ./ > C:\temp\output.csv`

#### Program options

```nohighlight
usage: damage.py [-h] [-v] [-o OUT] [-n] [-r] [-t DIGEST] files [files ...]

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

## Compiling/packaging the software on your platform

Making your own *damage* binary if the supplied ones don't meet your needs is easy. See the [how to create a standalone application](building_damage_binary.md) page for details.
