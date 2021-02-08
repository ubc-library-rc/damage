'''
Manifest generator for data files.

Produces a text file with md5 or sha1 sums for all files
from the top of a specified tree and checks line length
and ASCII character status for text files.

'''
#import glob
import argparse
#import csv
import hashlib
#import io
import json
import os.path
import string

#import PySimpleGUI as sg
#https://stackoverflow.com/questions/10937350/how-to-check-type-of-files-without-extensions-in-pythonimport magic
class Checker(object):
    '''
    A collection of various tools attached to a file
    '''

    def __init__(self, fname: str):
        '''
        Initializes Checker instance

        fname : str
            path to file
        '''
        self.fname = fname
        self._ext = os.path.splitext(fname)[1][1:]
        #self._flatfile = ['txt', 'dat', 'csv', 'tab', 'asc', 'md', '.py', 'sps', 'sas', 'do']
        try:
            self._fobj = open(self.fname)
            self._fobj.read() #Exceptions occur on read
            self._istext = True
        except UnicodeDecodeError:
            try:
                #Many statcan files uses win
                self._fobj = open(self.fname, encoding='windows-1252')
                self._fobj.read() #To raise an error if this codec is no good
                self._istext = True
            except Exception:
                self._fobj = None
                self._istext = False


        self._fobj_bin = open(self.fname, 'rb')
        self.csv_header = None

    def __del__(self):
        '''
        Destructor closes file
        '''
        if self._istext:
            self._fobj.close()
        self._fobj_bin.close()

    def produce_digest(self, prot: str = 'md5', blocksize: int = 2*16) -> str:
        '''
        Returns hex digest for object

        fname : str
            Path to a file object
        prot : str
            One of 'md5' or 'sha1'
        blocksize : int
            Read block size in bytes
        '''
        self._fobj_bin.seek(0)
        if prot == 'md5':
            _hash = hashlib.md5()
        else:
            _hash = hashlib.sha1()
        fblock = self._fobj_bin.read(blocksize)
        while fblock:
            _hash.update(fblock)
            fblock = self._fobj_bin.read(blocksize)
        return _hash.hexdigest()

    def flat_tester(self, **kwargs) -> dict:
        '''
        Checks file for line length and number of records.
        Returns a dictionary:
        {'min': int, 'max' : int, 'numrec':int, 'constant' : bool}

        Keyword arguments:
            flatfile : optional list
                List file extensions which will produce meaningful output.
                Flat file testing only makes sense on rectangular data files
        '''
        #print(f'kwargs {kwargs}')

        if self._ext in kwargs.get('flatfile', []) or not self._istext:
            #return {'min': 0, 'max': 0, 'numrec' : 0, 'constant': False}
            return {'min': 'N/A', 'max': 'N/A', 'numrec' : 'N/A', 'constant': 'N/A'}
        linecount = 0
        self._fobj.seek(0)
        maxline = len(self._fobj.readline())
        minline = maxline
        orig = maxline   # baseline to which new values are compared
        self._fobj.seek(0)
        for row in self._fobj:
            linecount += 1
            if len(row) > maxline:
                maxline = len(row)
            if len(row) < maxline:
                minline = len(row)
        constant = bool(maxline == orig == minline)
        #if maxline == orig and orig == minline:
            #constant = True
        #else:
            #constant = False
        return {'min': minline, 'max': maxline, 'numrec' : linecount, 'constant': constant}

    def non_ascii_tester(self, **kwargs) -> list:
        '''
        Returns a list of dicts of positions of non-ASCII characters in a text file
        [{'row': int, 'col':int, 'char':str}...] where cr in

        fname : str
            path/filename

        Keyword arguments:
            flatfile : optional list
                List file extensions which will produce meaningful output.
                Flat file testing only makes sense on rectangular data files

        '''
        if self._ext not in kwargs.get('flatfile', []) or not self._istext:
            return []
        #all_asc = string.ascii_uppercase + string.ascii_lowercase
        outlist = []
        self._fobj.seek(0)
        for rown, row in enumerate(self._fobj):
            for coln, char in enumerate(row):
                if char not in string.printable:
                    non_asc = {'row':rown+1, 'col': coln+1, 'char':char}
                    outlist.append(non_asc)
        return outlist

    def dos(self, **kwargs) -> bool:
        '''
        Checks for presence of carriage returns in file

        Returns True if a carriage return ie, ord(13) is present

        Keyword arguments:
            flatfile : optional list
                List file extensions which will produce meaningful output.
                Windows CRLF checking only makes sense on text files
        '''
        if self._ext not in kwargs.get('flatfile', []) or not self._istext:
            return None 
        self._fobj_bin.seek(0)
        for text in self._fobj_bin:
            if b'\r\n' in text:
                return True
        return None 

    def _report(self, **kwargs) -> dict:
        '''
        Returns a dictionary of outputs based on keywords below.
        Performs each test and returns the appropriate values. A convenience
        function so that you don't have to run the tests individually.

        Additionally, sets Checker.csv_header to be the dict keys, in case
        you need a header.
        eg. Checker.csv_header = '"filename", "digestType", "digest"'

        Sample output:
        {'filename':'/tmp/test.csv',
        'flat':{'min': 100, 'max': 100, 'numrec' : 101, 'constant': True},
        'nonascii':False,
        'dos':False}
,

        Accepted keywords and defaults:
            digest : str
                Hash algorithm. Default 'md5'
            flat : bool
                Flat file checking. Default True
            nonascii : bool
                Check for non-ASCII characters. Default True
            dos : bool
                check for Windows CR/LF combo. Default True
            flatfile : list
                List of filetypes which are considered rectangular.
                Default ['txt', 'dat', 'csv', 'tab', 'asc']
        '''
        #print(f'_report {kwargs}') 
        out = {'filename': self.fname}
        digest = kwargs.get('digest', 'md5')
        nonascii = kwargs.get('nonascii', True)
        dos = kwargs.get('dos', True)
        flat = kwargs.get('flat', True)
        flatfile = kwargs.get('flatfile')
        
        out.update({'digestType' : digest})
        out.update({'digest' : self.produce_digest(digest)})
        out.update({'flat': self.flat_tester(**kwargs)}, flatfile=flatfile)
        out.update({'nonascii': self.non_ascii_tester(**kwargs)}, flatfile=flatfile)
        if dos:
            out.update({'dos' : self.dos(**kwargs)}, flatfile=flatfile)
        #print(f'_report {out}')
        del out['flatfile']
        return out

    def _manifest_txt(self, **kwargs) -> str:
        '''
        Returns text-based file information
        '''
        #print(f'_manifest_txt {kwargs}')
        output = self._report(**kwargs)
        #if not output.get('flatfile'):
        #    output.update({'flatfile' : ['txt', 'dat', 'csv', 'tab', 'asc']})
        textout = (f"{output['filename']}\n"
                   f"{output['digestType']} checksum : {output['digest']}\n")
        if output.get('flat'):
            textout += f"Number of records: {output['flat']['numrec']}\n"
            #print(f"_manifest {output['flat'].get('constant')}")
            if output['flat'].get('constant'):
                if output['flat'].get('constant') == 'N/A':
                    flatout = f"Line length N/A\n"
                else: flatout = f"Line length {output['flat']['max']} constant records\n"
            else:
                flatout = (f"Minimum line length {output['flat']['min']}, "
                           f"maximum line length {output['flat']['max']}, "
                           "variable records\n")
            textout += flatout
        if output.get('nonascii'):
            nonascii = 'Non-ASCII characters found: \n'
            nonascii += '\n'.join([(f"{x['char']} in row {x['row']}, "
                                    f"column {x['col']}") for x in output['nonascii']])
            textout += 60 * '-' + '\n'
            textout += nonascii + '\n'
            textout += 60 * '-' + '\n'

        if output.get('dos'):
            dosout = 'Windows file (CRLF found in document)\n'
            textout += dosout
        return textout

    def _manifest_json(self, **kwargs) -> str:
        '''
        Returns JSON manifest as string
        '''
        return  json.dumps(self._report(**kwargs))

    @staticmethod
    def _make_csv_data(_dict) -> str:
        '''
        Returns dictionary keys as str
        '''
        head = []
        data = []
        for key, value in _dict.items():
            head.append(f'"{key}"')
            if isinstance(value, bool):
                data.append(f'"{value}"')
            #if not isinstance(value, int):
            #    data.append(f'"{value}"')
            else:
                data.append(value)
        head = ','.join(head)
        data = ','.join([f'{x}' for x in data])
        return (head, data)

    def _manifest_csv(self, **kwargs) -> str:
        '''
        Returns manifest as CSV

        header : bool
            add header to data string
        '''
        output = self._report(**kwargs)
        #print(f'_manifest_csv {output}')
        head = []
        data = []
        for key, value in output.items():
            if isinstance(value, list) and key != 'flatfile':#only nonascii fits this
                head.append(f'"{key}"')
                badchar = []
                for rcc in value:
                    #print(f'rcc {rcc}')
                    badchar.append(f"(r{rcc['row']}c{rcc['col']} {rcc['char']})")
                badchar = ','.join(badchar)
                data.append(f'"{badchar}"')
                continue
            if isinstance(value, dict):
                outp = self._make_csv_data(value)
                head.append(outp[0])
                data.append(outp[1])
                #continue
            else:
                head.append(f'"{key}"')
                if not value:
                    value = ''
                data.append(f'"{value}"')
        head = ','.join(head)
        data = ','.join(data)
        if kwargs.get('headers'):
            return '\n'.join([head, data])
        return data

    def manifest(self, out: str = 'txt', **kwargs):
        '''
        Returns your desired output type as string

        out : str
            Acceptable values are 'txt', 'csv', 'json'

        Accepted keywords and defaults:
            digest : str
                Hash algorithm. Default 'md5'
            flat : bool
                Flat file checking. Default True
            nonascii : bool
                Check for non-ASCII characters. Default True
            dos : bool
                check for Windows CR/LF combo. Default True
            flatfile : list
                List of filetypes which are considered rectangular. Only these
                get checked for rectangularity regardless of flat flag
                Default ['txt', 'dat', 'csv', 'tab', 'asc']
            headers : bool
                Include csv header (only has any effect with out='csv')
                Default is False
        '''
        #print(f'manifest {kwargs}')
        if out == 'txt':
            return self._manifest_txt(**kwargs)
        if out == 'json':
            return self._manifest_json(**kwargs)
        if out == 'csv':
            return self._manifest_csv(**kwargs)
        return None

def parse() -> argparse.ArgumentParser():
    '''
    Separates argparser into function. Returns arparse.ArgumentParser()
    '''
    desc = ('Produces a text, csv or JSON output with md5 or sha1 sums for files, '
            'testing for Windows CRLF combinations, '
            'as well as checking text files for regularity and non/ASCII characters')
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('files', help='Files to check. Wildcards acceptable (eg, *)',
                        nargs='+')
    parser.add_argument('-o', '--output', dest='out',
                        help='Output format. One of txt, csv, json',
                        default='txt')
    parser.add_argument('-n', '--no-flat', action='store_true', dest='noflat',
                        help="Don't check text files for rectangularity")
    parser.add_argument('-r', '--recursive', action='store_true', dest='recur',
                        help='Recursive *directory* processing of file tree. Assumes that the '
                             'arguments point to a directory (eg, tmp/), and a slash will '
                             'be appended if one does not exist')

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
        tree = [x for x in os.walk(fpath)]
        tree = [f'{p[0]}{os.sep}{f}' for p in tree for f in p[2]]
        tree = list(set(tree))
        outlist += tree
    return outlist

def main():
    '''
    Main function to output manifests to stdout.
    '''
    parser = parse()
    args = parser.parse_args()

    #print(args)
    #print(args.recur)
    if not args.recur:
        files = [x for x in args.files if os.path.isfile(x)]
    else:
        files = recurse_files(args.files) 
    #print(files)
    #print(args.noflat)
    for num, fil in enumerate(files):
        #print(f'Checking {fil}')
        if args.noflat:
            flatfile = [os.path.splitext(fil)[1][1:]]
            #print(f'EXTENSION {flatfile}')
        else:
            flatfile = None
        testme = Checker(fil)
        if args.out == 'csv' and num == 0:
            if flatfile:
                print(testme.manifest('csv', flatfile=flatfile,
                                      headers=True))
            else:
                print(testme.manifest('csv', headers=True))
            continue
        if flatfile:
            #print(f'tried this: {flatfile}')
            print(testme.manifest(args.out, flatfile=flatfile))
        else:
            print(testme.manifest(args.out))


if __name__ == '__main__':
    main()
