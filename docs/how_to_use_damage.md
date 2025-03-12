# How to use the Damage console utility

Documentation is for the  *console* utility. That means a Windows command prompt or terminal is required for use. The console utility is normally referred to with a lowercase initial 'd' (ie, **damage**) and the full GUI application as **damage_gui**. Whether or not you call the application with a straight `damage` or `python damage.py` will depend on how you work, but the first will be more common.

#### Program options

```nohighlight
usage: damage [-h] [-v] [-o {txt,csv,tsv,json}] [-n] [-r]
              [-t {md5,sha1,sha224,sha256,sha384,sha512,blake2b,blake2s}]
              [-a] [-f TO_FILE]
              files [files ...]

Produces a text, csv or JSON output with checksums for files, testing for
Windows CRLF combinations, as well as checking text files for regularity and
non/ASCII characters

positional arguments:
  files                 Files to check. Wildcards acceptable (eg, *)

options:
  -h, --help            show this help message and exit
  -v, --version         Show version number and exit
  -o, --output {txt,csv,tsv,json}
                        Output format. One of txt, csv, json, tsv
  -n, --no-flat         Don't check text files for rectangularity
  -r, --recursive       Recursive *directory* processing of file tree. Assumes
                        that the arguments point to a directory (eg, tmp/),
                        and a slash will be appended if one does not exist
  -t, --hash-type {md5,sha1,sha224,sha256,sha384,sha512,blake2b,blake2s}
                        Checksum hash type. Supported hashes: 'sha1',
                        'sha224', 'sha256', 'sha384', 'sha512', 'blake2b',
                        'blake2s', 'md5'. Default: 'md5'
  -a, --no-ascii        Don't check text files for non-ASCII characters
  -f, --to-file TO_FILE
                        Output to -f [file] instead of stdout
```

## Compiling/packaging the software on your platform

Making your own *damage* binary if the supplied ones don't meet your needs is easy. See the [how to create a standalone application](building_damage_binary.md) page for details.
