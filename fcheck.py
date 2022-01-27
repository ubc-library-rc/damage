'''
Manifest generator for data files.

Produces a text file with user specificied checksums for all files
from the top of a specified tree and checks line length
and ASCII character status for text files.

For statistics program files:
  SAS .sas7bdat
  SPSS .sav
  Stata .dta

Checker() will report number of cases and variables as
rows and columns respectively.

'''

import hashlib
import json
import os.path
import string

import pyreadstat
#import PySimpleGUI as sg
#https://stackoverflow.com/questions/10937350/
#how-to-check-type-of-files-without-extensions-in-pythonimport magic
#https://thepythonguru.com/writing-packages-in-python/

VERSION = (0, 1, 5)
__version__ = '.'.join([str(x) for x in VERSION])

#Commercial stats files extensions
#I am aware that extension checking is not perfect
STATFILES = ['dta', 'sav', 'sas7bdat']

class Checker():
    '''
    A collection of various tools attached to a file
    '''

    def __init__(self, fname: str):
        '''
        Initializes Checker instance

            fname : str
                Path to file
        '''
        self.fname = fname
        self._ext = os.path.splitext(fname)[1][1:]
        try:
            self._fobj = open(self.fname)
            self._fobj.read() #Exceptions occur on read
            self._istext = True
            self._encoding = 'utf-8'
        except UnicodeDecodeError:
            try:
                #Many statcan files uses win
                self._fobj = open(self.fname, encoding='windows-1252')
                self._fobj.read() #To raise an error if this codec is no good
                self._istext = True
                self._encoding = 'windows-1252'
            except UnicodeDecodeError: #Still raises unicode error on failure
                self._fobj = None
                self._istext = False
                self._encoding = None


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
               Hash type. Supported hashes: 'sha1', 'sha224', 'sha256',
                  'sha384', 'sha512', 'blake2b', 'blake2s', 'md5'.
                  Default: 'md5'

            blocksize : int
               Read block size in bytes
        '''
        ok_hash = {'sha1' : hashlib.sha1(),
                   'sha224' : hashlib.sha224(),
                   'sha256' : hashlib.sha256(),
                   'sha384' : hashlib.sha384(),
                   'sha512' : hashlib.sha512(),
                   'blake2b' : hashlib.blake2b(),
                   'blake2s' : hashlib.blake2s(),
                   'md5': hashlib.md5()}

        self._fobj_bin.seek(0)
        try:
            _hash = ok_hash[prot]
        except (UnboundLocalError, KeyError):
            message = ('Unsupported hash type. Valid values are '
                       f'{list(ok_hash)}.')
            print(message)
            raise

        fblock = self._fobj_bin.read(blocksize)
        while fblock:
            _hash.update(fblock)
            fblock = self._fobj_bin.read(blocksize)
        return _hash.hexdigest()

    def flat_tester(self, **kwargs) -> dict:
        '''
        Checks file for line length and number of records.

        Returns a dictionary:

        `{'min_cols': int, 'max_cols' : int, 'numrec':int, 'constant' : bool}`
        '''
        flat = kwargs.get('flatfile')
        if not flat:
            return {'min_cols': 'N/A', 'max_cols': 'N/A', 'numrec' : 'N/A',
                    'constant': 'N/A', 'encoding' : 'N/A'}

        if self._ext.lower() in STATFILES:
            return self._flat_tester_commercial(**kwargs)

        if self._istext:
            return self._flat_tester_txt()

        return {'min_cols': 'N/A', 'max_cols': 'N/A', 'numrec' : 'N/A',
                'constant': 'N/A', 'encoding' : 'N/A'}

    def _flat_tester_commercial(self, **kwargs) -> dict:
        '''
        Checks SPSS sav, SAS sas7bdat and Stata .dta files for rectangularity

        Returns a dictionary:

        `{'min_cols': int, 'max_cols': int, 'numrec' : int,
                    'constant': True, 'encoding': str}`

        These files are by definition rectanglar, at least as checked here
        by pyreadstat/pandas, so constant will always == True.
        '''
        if not kwargs.get('flatfile'):
            return {'min_cols': 'N/A', 'max_cols': 'N/A', 'numrec' : 'N/A',
                    'constant': 'N/A', 'encoding': 'N/A'}
        options = {'sav' : pyreadstat.read_sav,
                   'dta' : pyreadstat.read_dta,
                   'sas7bdat' : pyreadstat.read_sas7bdat}
        meta = options[self._ext.lower()](self.fname)[1]
        self._encoding = meta.file_encoding
        return {'min_cols':meta.number_columns,
                'max_cols':meta.number_columns,
                'numrec': meta.number_rows,
                'constant':True,
                'encoding': self._encoding}

    def _flat_tester_txt(self) -> dict: #kwargs not used
        '''
        Checks file for line length and number of records.

        Returns a dictionary:

        `{'min_cols': int, 'max_cols' : int, 'numrec':int, 'constant' : bool}`
        '''
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
        return {'min_cols': minline, 'max_cols': maxline, 'numrec' : linecount,
                'constant': constant, 'encoding': self._encoding}

    def non_ascii_tester(self, **kwargs) -> list:
        '''
        Returns a list of dicts of positions of non-ASCII characters in a text file.

        `[{'row': int, 'col':int, 'char':str}...]`

            fname : str
               Path/filename

            Keyword arguments:

                flatfile : bool
                   — Perform rectangularity check. If False, returns dictionary
                     with all values as 'N/A'
        '''
        if not kwargs.get('flatfile') or not self._istext:
            return []
        outlist = []
        self._fobj.seek(0)
        for rown, row in enumerate(self._fobj):
            for coln, char in enumerate(row):
                if char not in string.printable and char != '\x00':
                    non_asc = {'row':rown+1, 'col': coln+1, 'char':char}
                    outlist.append(non_asc)
        return outlist

    def null_count(self, **kwargs) -> dict:
        '''
        Returns an integer count of null characters in the file
        ('\x00') or None if skipped

        Keyword arguments:

                flatfile : bool
                   — Test is useless if not a text file. If False, returns 'N/A'
        '''
        if (not kwargs.get('flatfile')
                or not self._istext
                or not kwargs.get('null_chars')):
            return None
        self._fobj.seek(0)
        count = self._fobj.read().count('\x00')
        if not count:
            return None
        return count

    def dos(self, **kwargs) -> bool:
        '''
        Checks for presence of carriage returns in file

        Returns True if a carriage return ie, ord(13) is present

        Keyword arguments:

            flatfile : bool
                — Perform rectangularity check. If False, returns dictionary
                  with all values as 'N/A'
        '''
        if not kwargs.get('flatfile') or not self._istext:
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

        ```
        {'filename':'/tmp/test.csv',
        'flat':{'min_cols': 100, 'max_cols': 100, 'numrec' : 101, 'constant': True},
        'nonascii':False,
        'dos':False}
        ```
        Accepted keywords and defaults:
            digest : str
                — Hash algorithm. Default 'md5'

            flat : bool
                — Flat file checking. Default True

            nonascii : bool
                — Check for non-ASCII characters. Default True

            dos : bool
                — check for Windows CR/LF combo. Default True

            flatfile : bool
                — Perform rectangularity check. If False, returns dictionary
                  with all values as 'N/A'
            null_chars : bool
                - check for null characters
        '''
        out = {'filename': self.fname}
        digest = kwargs.get('digest', 'md5')
        dos = kwargs.get('dos', True)
        #flatfile = kwargs.get('flatfile')

        out.update({'digestType' : digest})
        out.update({'digest' : self.produce_digest(digest)})
        out.update({'flat': self.flat_tester(**kwargs)})
        out.update({'nonascii': self.non_ascii_tester(**kwargs)})
        out.update({'encoding': self._encoding})
        out.update({'null_chars': self.null_count(**kwargs)})
        if dos:
            out.update({'dos' : self.dos(**kwargs)})
        return out

    def _manifest_txt(self, **kwargs) -> str:
        '''
        Returns text-based file information
        '''
        output = self._report(**kwargs)
        textout = (f"{output['filename']}\n"
                   f"{output['digestType']} checksum : {output['digest']}\n"
                   f"Encoding: {output['encoding']}\n")
        if output.get('flat'):
            textout += f"Number of records: {output['flat']['numrec']}\n"
            if output['flat'].get('constant'):
                if output['flat'].get('constant') == 'N/A':
                    flatout = "Columns: N/A\n"
                else: flatout = f"Columns: {output['flat']['max_cols']} constant records\n"
            else:
                flatout = (f"Minimum line length {output['flat']['min_cols']}, "
                           f"maximum line length {output['flat']['max_cols']}, "
                           "variable records\n")
            textout += flatout
        if output.get('nonascii'):
            nonascii = 'Non-ASCII characters found: \n'
            msg = [(f"{x['char']} in row {x['row']}, column {x['col']}")
                   for x in output['nonascii']]
            nonascii += '\n'.join(msg)
            textout += 60 * '-' + '\n'
            textout += nonascii + '\n'
            textout += 60 * '-' + '\n'

        if output.get('dos'):
            dosout = 'Windows file (CRLF found in document)\n'
            textout += dosout
        if output.get('null_chars'):
            textout += f"Null characters: {output.get('null_chars')}"

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
            else:
                data.append(value)
        head = ','.join(head)
        data = ','.join([f'{x}' for x in data])
        return (head, data)

    def _manifest_csv(self, **kwargs) -> str:
        '''
        Returns manifest as CSV

        header : bool
            — add header to data string
        '''
        output = self._report(**kwargs)
        head = []
        data = []
        for key, value in output.items():
            if isinstance(value, list) and key != 'flatfile':#only nonascii fits this
                head.append(f'"{key}"')
                badchar = []
                for rcc in value:
                    badchar.append(f"(r{rcc['row']}c{rcc['col']} {rcc['char']})")
                badchar = ','.join(badchar)
                data.append(f'"{badchar}"')
                continue
            if isinstance(value, dict):
                outp = self._make_csv_data(value)
                head.append(outp[0])
                data.append(outp[1])
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
            — Acceptable values are 'txt', 'csv', 'json'

        Accepted keywords and defaults:
            digest : str
                — Hash algorithm. Default 'md5'

            flat : bool
                — Flat file checking. Default True

            nonascii : bool
                — Check for non-ASCII characters. Default True

            dos : bool
                — check for Windows CR/LF combo. Default True
            flatfile : bool
                — Perform rectangularity check. If False, returns dictionary
                  with all values as 'N/A'

            headers : bool
               —  Include csv header (only has any effect with out='csv')
                  Default is False
        '''
        if out == 'txt':
            return self._manifest_txt(**kwargs)
        if out == 'json':
            return self._manifest_json(**kwargs)
        if out == 'csv':
            return self._manifest_csv(**kwargs)
        return None

if __name__ == '__main__':
    pass
