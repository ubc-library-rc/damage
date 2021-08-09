#! python
'''
Manifest generator for data files.

Produces a text file with user specified checksums for all files
from the top of a specified tree and checks line length
and ASCII character status for text files.

For statistics program files:
  SAS .sas7bdat
  SPSS .sav
  Stata .dta

Checker() will report number of cases and variables as
rows and columns respectively.

'''

import argparse
import json
import os
import sys
import fcheck

def parse() -> argparse.ArgumentParser():
    '''
    Separates argparser into function. Returns arparse.ArgumentParser()
    '''
    desc = ('Produces a text, csv or JSON output with checksums for files, '
            'testing for Windows CRLF combinations, '
            'as well as checking text files for regularity and non/ASCII characters')
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('files', help='Files to check. Wildcards acceptable (eg, *)',
                        nargs='+', default=' ')
    #note 'prog' is built into argparse
    parser.add_argument('-v', '--version', action='version', version='%(prog)s '+fcheck.__version__,
                        help='Show version number and exit')
    parser.add_argument('-o', '--output', dest='out',
                        help='Output format. One of txt, csv, json',
                        default='txt')
    parser.add_argument('-n', '--no-flat', action='store_false', dest='flatfile',
                        help="Don't check text files for rectangularity")
    parser.add_argument('-r', '--recursive', action='store_true', dest='recur',
                        help='Recursive *directory* processing of file tree. Assumes that the '
                             'arguments point to a directory (eg, tmp/), and a slash will '
                             'be appended if one does not exist')
    parser.add_argument('-t', '--hash-type', dest='digest', default='md5',
                        help="Checksum hash type. Supported hashes: 'sha1', "
                             "'sha224', 'sha256', 'sha384', 'sha512', 'blake2b', "
                             "'blake2s', 'md5'.  Default: 'md5'")
    return parser

def recurse_files(parsed_args):
    '''
    Transforms parsed args into a list of unique files.
    '''
    outlist = []
    for tree in parsed_args:
        if not tree.endswith(os.sep):
            tree += os.sep
        fpath = os.path.split(os.path.expanduser(tree))[0]
        ftree = [x for x in os.walk(fpath)]
        ftree = [f'{p[0]}{os.sep}{f}' for p in ftree for f in p[2]]
        ftree = list(set(ftree))
        outlist += ftree
    return outlist

def main():
    '''
    Main function to output manifests to stdout.
    '''
    parser = parse()
    args = parser.parse_args()
    if not args.recur:
        #Windows does not do wildcard expansion at the shell level
        if sys.platform == 'win32':
            import glob
            import ntpath
            files = [y for x in args.files for y in glob.glob(x) if ntpath.isfile(y)]
        else:
            files = [x for x in args.files if os.path.isfile(x)]
    else:
        files = recurse_files(args.files)


    output = []
    for num, fil in enumerate(files):
        testme = fcheck.Checker(fil)
        if args.out == 'csv' and num == 0:
            output.append(testme.manifest(headers=True, **vars(args)))
        else:
            output.append(testme.manifest(**vars(args)))
    if not args.out == 'json':
        print('\n'.join(output))
    else:
        outjson = ('{"files" :' +
                   '[' + ','.join(output) + ']'
                   + '}')
        outjson = json.dumps(json.loads(outjson)) #validate
        print(outjson)

if __name__ == '__main__':
    main()
