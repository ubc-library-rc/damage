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

import copy
import csv
import hashlib
import io
import json
import logging
import mimetypes
import pathlib
import string

import chardet
import pyreadstat

LOGGER = logging.getLogger()

VERSION = (0, 3, 15)
__version__ = '.'.join([str(x) for x in VERSION])

#PDB note check private variables with self._Checker__private_var
#Note *single* underscore before Checker
class Checker():
    '''
    A collection of various tools attached to a file
    '''

    def __init__(self, fname: str) -> None: #DONE
        '''
        Initializes Checker instance

            fname : str
                Path to file
        '''
        #Commercial stats files extensions
        #I am aware that extension checking is not perfect
        self.statfiles = ['.dta', '.sav', '.sas7bdat']
        #brute force is best force
        self.textfiles= ['.dat', '.txt', '.md', '.csv',
                        '.tsv', '.asc', '.html', '.xml',
                        '.xsd', '.htm', '.log', '.nfo',
                        '.text', '.xsl', '.py', '.r',
                         '.toml', '.yaml', '.yml', '.prn',
                         '.data']
        self.fname = pathlib.Path(fname)
        #self._ext = fname.suffix
        self.__istext = self.__istextfile()
        self.__text_obj = None
        with open(self.fname, 'rb') as fil:
            self.__fobj_bin = io.BytesIO(fil.read())
        self.encoding = self.__encoding()
        if self.__istext:
            with open(self.fname, encoding=self.encoding.get('encoding')) as f:
                self.__text_obj = io.StringIO(f.read())


    @property
    def hidden(self)->bool:
        '''
        Returns True if file is hidden (ie, startswith '.')
        or is in in a hidden directory (ie, any directory on the path
        starts with '.')
        '''
        if any(x.startswith('.') for x in self.fname.parts):
            return True
        return False

    def __istextfile(self):
        '''
        Check to see if file is a text file based on mimetype.
        Works with extensions only which is not ideal
        '''
        try:
            if ('text' in mimetypes.guess_file_type(self.fname)
                or self.fname.suffix.lower() in self.textfiles):
                return True
        except AttributeError: #soft deprecation fix
            if ('text' in mimetypes.guess_type(self.fname)
                or self.fname.suffix.lower() in self.textfiles):
                return True

        return False

    def __encoding(self) -> dict: #DONE
        '''
        Returns most likely encoding of self.fname, dict with keys
        encoding, confidence, language (the output of chardet.detect)
        and sets Checker.__is_text
        '''
        enc = chardet.detect(self.__fobj_bin.read())
        self.__fobj_bin.seek(0) #leave it as you found it
        if self.__istext:
            return enc

        return {'encoding': None,
                    'confidence': 0.0,
                    'language' : ''}

    def __del__(self) -> None:#DONE
        '''
        Destructor closes file
        '''
        self.__fobj_bin.close()

    def produce_digest(self, prot: str = 'md5', blocksize: int = 2*16) -> str: #DONE
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

        self.__fobj_bin.seek(0)
        try:
            _hash = ok_hash[prot]
        except (UnboundLocalError, KeyError):
            message = ('Unsupported hash type. Valid values are '
                       f'{list(ok_hash)}.')
            LOGGER.exception('Unsupported hash type. Valid values are %s', message)
            raise

        fblock = self.__fobj_bin.read(blocksize)
        while fblock:
            _hash.update(fblock)
            fblock = self.__fobj_bin.read(blocksize)
        return _hash.hexdigest()

    def flat_tester(self, **kwargs) -> dict: #DONE
        '''
        Checks file for line length and number of records.

        Returns a dictionary:

        `{'min_cols': int, 'max_cols' : int, 'numrec':int, 'constant' : bool}`
        '''
        if not kwargs.get('flatfile'):
            return {'min_cols': 'N/A', 'max_cols': 'N/A', 'numrec' : 'N/A',
                    'constant': 'N/A', 'encoding' : 'N/A'}

        if self.fname.suffix.lower() in self.statfiles:
            return self._flat_tester_commercial(**kwargs)

        if self.__istext:
            return self._flat_tester_txt()
        #this should not happen but you never know
        return {'min_cols': 'N/A', 'max_cols': 'N/A', 'numrec' : 'N/A',
                'constant': 'N/A', 'encoding' : 'N/A'}

    def _flat_tester_commercial(self, **kwargs) -> dict: #DONE
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
        options = {'.sav' : pyreadstat.read_sav,
                   '.dta' : pyreadstat.read_dta,
                   '.sas7bdat' : pyreadstat.read_sas7bdat}
        meta = options[self.fname.suffix.lower()](self.fname)[1]
        #self._encoding = meta.file_encoding
        self.encoding['encoding'] = meta.file_encoding
        return {'min_cols':meta.number_columns,
                'max_cols':meta.number_columns,
                'numrec': meta.number_rows,
                'constant':True,
                'encoding': self.encoding['encoding']}

    def _flat_tester_txt(self) -> dict: #DONE
        '''
        Checks file for line length and number of records.

        Returns a dictionary:

        `{'min_cols': int, 'max_cols' : int, 'numrec':int, 'constant' : bool}`
        '''
        linecount = 0
        self.__text_obj.seek(0)
        if not self.__istext:
            raise TypeError('Not a text file')
        maxline = len(self.__text_obj.readline())
        minline = maxline
        orig = maxline   # baseline to which new values are compared
        for row in self.__text_obj.readlines():
            linecount += 1
            maxline = max(maxline, len(row))
            minline = min(minline, len(row))
        constant = bool(maxline == orig == minline)
        self.__text_obj.seek(0)
        return {'min_cols': minline, 'max_cols': maxline, 'numrec' : linecount,
                'constant': constant, 'encoding': self.encoding['encoding']}

    def non_ascii_tester(self, **kwargs) -> list: #DONE
        '''
        Returns a list of dicts of positions of non-ASCII characters in a text file.

        `[{'row': int, 'col':int, 'char':str}...]`

            fname : str
               Path/filename

            Keyword arguments:

                #flatfile : bool
                asctest : bool
                   — Perform character check (assuming it is text)
        '''
        if (kwargs.get('asctest', False)
            or not self.__istext
            or not kwargs.get('flatfile')):
            return []
        outlist = []
        self.__text_obj.seek(0)
        for rown, row in enumerate(self.__text_obj):
            for coln, char in enumerate(row):
                if char not in string.printable and char != '\x00':
                    non_asc = {'row':rown+1, 'col': coln+1, 'char':char}
                    outlist.append(non_asc)
        self.__text_obj.seek(0)
        return outlist

    def null_count(self, **kwargs) -> dict: #DONE
        '''
        Returns an integer count of null characters in the file
        ('\x00') or None if skipped

        Keyword arguments:

                flatfile : bool
                   — Test is useless if not a text file. If False, returns 'N/A'
        '''
        if (not kwargs.get('flatfile')
                or not self.__istext
                or not kwargs.get('null_chars')):
            return None
        self.__text_obj.seek(0)
        count = self.__text_obj.read().count('\x00')
        if not count:
            return None
        return count

    def dos(self, **kwargs) -> bool: #DONE
        '''
        Checks for presence of carriage returns in file

        Returns True if a carriage return ie, ord(13) is present

        Keyword arguments:

            flatfile : bool
                — Perform rectangularity check. If False, returns dictionary
                  with all values as 'N/A'
        '''
        if not kwargs.get('flatfile') or not self.__istext:
            return None
        self.__fobj_bin.seek(0)
        for text in self.__fobj_bin:
            if b'\r\n' in text:
                return True
        return False

    def _mime_type(self, fname:pathlib.Path)->tuple:
        '''
        Returns mimetype or 'application/octet-stream'
        '''
        try:
            out = mimetypes.guess_file_type(fname, strict=False)[0]
        except AttributeError:
            #soft deprecation
            out = mimetypes.guess_type(fname)[0]
        if not out:
            out = 'application/octet-stream'
        return out

    def _report(self, **kwargs) -> dict: #DONE
        '''
        Returns a dictionary of outputs based on keywords below.
        Performs each test and returns the appropriate values. A convenience
        function so that you don't have to run the tests individually.

        Sample output:

        ```
        {'filename':'/tmp/test.csv',
        'flat': True,
        'min_cols': 100, 'max_cols': 100, 'numrec' : 101, 'constant': True,
        'nonascii':False,
        'dos':False}
        ```
        Accepted keywords and defaults:
            digest : str
                — Hash algorithm. Default 'md5'

            flat : bool
                — Flat file checking.

            nonascii : bool
                — Check for non-ASCII characters.

            flatfile : bool
                — Perform rectangularity check. If False, returns dictionary
                  with all values as 'N/A'

            null_chars : bool
                - check for null characters
        '''
        out = {'filename': self.fname}
        digest = kwargs.get('digest', 'md5')
        #dos = kwargs.get('dos')

        out.update({'digestType' : digest})
        out.update({'digest' : self.produce_digest(digest)})
        #out.update({'flat': self.flat_tester(**kwargs)})
        out.update(self.flat_tester(**kwargs))
        #out.update({'flat':'FFFFFFFFFFFF'})
        out.update({'nonascii': self.non_ascii_tester(**kwargs)})
        out.update({'encoding': self.encoding['encoding']})
        out.update({'null_chars': self.null_count(**kwargs)})
        out.update({'mimetype': self._mime_type(self.fname)})
        #if dos:
        #    out.update({'dos' : self.dos(**kwargs)})
        #else:
        #    out.update({'dos': None})
        out.update({'dos': self.dos(**kwargs)})
        return out

    def _manifest_txt(self, **kwargs)->str:
        '''
        Returns manifest as plain text
        '''
        return '\n'.join([f'{k}: {v}' for k,v in kwargs['report'].items()
                          if v not in ['', None]])

    def _manifest_json(self, **kwargs)->str:
        '''
        Returns manifest as JSON
        '''
        out = kwargs['report'].copy()
        out['filename'] = str(kwargs['report']['filename'])
        return json.dumps(out)

    def _manifest_csv(self, **kwargs)->str:
        '''
        Returns manifest as [whatever]-separated value
        '''
        outstr = io.StringIO(newline='')
        writer = csv.DictWriter(outstr, fieldnames=kwargs['report'].keys(),
                                delimiter=kwargs.get('sep', ','),
                                quoting=csv.QUOTE_MINIMAL)
        if kwargs.get('headers'):
            writer.writeheader()
        writer.writerow(kwargs['report'])
        outstr.seek(0)
        return outstr.read()

    def manifest(self, **kwargs) -> str: #really as str #DONE
        '''
        Returns desired output type as string

        out : str
            — Acceptable values are 'txt', 'json', 'csv'
              'txt' Plain text
              'json' JSON
              'csv' Comma-separated value

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

            sep: str
              —  Separator if you want a different plain text separator like a
                tab (\t) or pipe (|). Only functional with csv output, obviously.

        '''
        report = self._report(**kwargs)
        report_type={'txt': self._manifest_txt,
                    'json': self._manifest_json,
                    'csv': self._manifest_csv,
                    'tsv': self._manifest_csv,
                    'psv': self._manifest_csv}

        try:
            return report_type[kwargs['out']](report=report, **kwargs)
        except KeyError:
            LOGGER.error('Unsupported manifest type %s; defaulting to text', kwargs['out'])
            return report_type[kwargs['out']](report=report, out='txt', **kwargs)

if __name__ == '__main__':
    pass
