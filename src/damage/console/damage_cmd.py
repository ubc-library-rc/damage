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
import glob #God I hate Windows
import json
import os
import pathlib
import sys

import damage

def parse() -> argparse.ArgumentParser(): #DONE
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
    parser.add_argument('-v', '--version', action='version', version='%(prog)s '+damage.__version__,
                        help='Show version number and exit')
    parser.add_argument('-o', '--output', dest='out',
                        help='Output format. One of txt, csv, json, tsv',
                        default='txt',
                        choices = ['txt', 'csv', 'tsv', 'json'],
                        type=str.lower)
    parser.add_argument('-n', '--no-flat', action='store_false', dest='flatfile',
                        help="Don't check text files for rectangularity")
    parser.add_argument('-r', '--recursive', action='store_true', dest='recur',
                        help='Recursive *directory* processing of file tree. Assumes that the '
                             'arguments point to a directory (eg, tmp/), and a slash will '
                             'be appended if one does not exist')
    parser.add_argument('-t', '--hash-type', dest='digest', default='md5',
                        help="Checksum hash type. Supported hashes: 'sha1', "
                             "'sha224', 'sha256', 'sha384', 'sha512', 'blake2b', "
                             "'blake2s', 'md5'.  Default: 'md5'",
                        choices = ['md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512',
                                   'blake2b', 'blake2s'],
                        type=str.lower)
    parser.add_argument('-a', '--no-ascii', action='store_false', dest='asctest',
                        help="Don't check text files for non-ASCII characters")
    parser.add_argument('-f', '--to-file',
                        help='Output to -f [file] instead of stdout')
    return parser

def recurse_files(inlist) -> map:
    '''
    Returns a map object with pathlib.Paths of files
    '''
    outlist = []
    for flist in inlist:
        rec = os.walk(flist)
        outlist += [pathlib.Path(x[0], y) for x in rec for y in x[2]]
    return outlist #includes hidden files

def main(): #pylint: disable=too-many-branches
    '''
    Main function to output manifests to stdout.
    '''
    separator_types = {'csv': ',', 'tsv': '\t'}
    #Purely for formatting output
    line_spacer = {'txt':'\n\n', 'csv':'', 'tsv': ''}
    parser = parse()
    args = parser.parse_args()
    if not args.recur:
        #Windows does not do wildcard expansion at the shell level
        if sys.platform.startswith('win'): #Maybe they will have win64 sometime:
            files = map(pathlib.Path, [y for x in args.files for y in glob.glob(x)])
        else:
            files = map(pathlib.Path, list(args.files))
    else:
        files = recurse_files(args.files)


    output = []
    try: ###
        for num, fil in enumerate(files):
            if not fil.is_file() or not fil.exists():
                continue
            testme = damage.Checker(fil)
            if args.out in separator_types and num == 0:
                output.append(testme.manifest(headers=True,
                                              sep=separator_types.get(args.out),
                                              **vars(args)))
            else:
                output.append(testme.manifest(sep=separator_types.get(args.out),
                                              **vars(args)))
        if not args.out == 'json':
            #print(line_spacer[args.out].join(output).strip())
            out_info =line_spacer[args.out].join(output).strip()
        else:
            outjson = ('{"files" :' +
                       '[' + ','.join(output) + ']'
                       + '}')
            out_info = json.dumps(json.loads(outjson)) #validate
    except Exception as err: #pylint: disable=broad-exception-caught
        print(f'Abnormal program termination {err}', file=sys.stderr)
        sys.exit()

    if args.to_file:
        with open(pathlib.Path(args.to_file), mode='w',
                  encoding='utf-8') as outf:
            outf.write(out_info)
    else:
        print(out_info)

if __name__ == '__main__':
    main()
