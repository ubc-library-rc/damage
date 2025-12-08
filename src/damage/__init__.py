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
import multiprocessing
import pathlib
import string
import sys
import time

import charset_normalizer
import pandas as pd
import pyreadstat
import tqdm

LOGGER = logging.getLogger()

VERSION = (0, 5, 6)
__version__ = '.'.join([str(x) for x in VERSION])

#PDB note check private variables with self._Checker__private_var
#Note *single* underscore before Checker
class Checker():
    '''
    A collection of various tools attached to a file
    '''

    def __init__(self, fname: str, **kwargs) -> None: #DONE,
        '''
        Initializes Checker instance

        Parameters
        ----------
        fname : str
            Path to file
        **kwargs : dict
            Additional keyword parameters

        Other parameters
        ----------------
        weight : bool
            Weight towards a specific encoding
        target_encoding : str
            Specific target encoding, like 'cp1252'

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

        with tqdm.tqdm(total=self.fname.stat().st_size,
                       desc=f'Loading {self.fname.name}') as pbar:
            self.__fobj_bin = io.BytesIO()
            with open(self.fname, 'rb') as f:
                bsize=2**16
                fblock  = f.read(bsize)
                pbar.update(bsize)
                while fblock:
                    self.__fobj_bin.write(fblock)
                    pbar.update(bsize)
                    fblock = f.read(bsize)


        self.encoding = self.__encoding(**kwargs)
        #Using RAM speeds it up by several orders of magnitude
        if self.__istext:
            self.__text_obj = io.StringIO(self.__fobj_bin.getvalue().decode(
                self.encoding.get('encoding', 'utf-8')))
            self.__fobj_bin.seek(0)

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
        It's not perfect but at least it's something.
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

    def __encoding(self, weight:bool=True,#pylint: disable=unused-argument
                     target:str='cp1252',
                     **kwargs:dict)-> dict:
        '''
        Returns most likely encoding of self.fname, dict with keys
        encoding, confidence, language
        and sets Checker.__is_text. It will make the assumption
        that if cp1252 (Windows-1252) is in the top 3, it *is*
        Windows-1252. Turn off this behaviour with 'weight'

        Parameters
        ----------
        weight : bool, default=True

        target : str, default='cp1252'
            If weight is True, if target appears in the top three encodings then the
            encoding will be assigned as target.
        **kwargs : dict
            Other miscellaneous things that may have been passed. They will be ignored.

        Notes
        -----
        Defaults to cp1252 because this was written to deal largely with
        Statistics Canada material, and that's in English or French. And apparently
        UTF-8 is too modern for them.
        '''
        null = {'encoding': None,
                    'confidence': 0.0,
                    'language' : ''}
        encoding = {}
        read_position = 0
        enc_raw = charset_normalizer.from_bytes(self.__fobj_bin.getvalue())
        if not enc_raw:
            return null
        encoding['encoding'] = enc_raw.best().encoding
        if weight:
            if target in [x.encoding for x in enc_raw][:3]:
                read_position = [x.encoding for x in enc_raw][:3].index(target)
                print(f'read position:{read_position}')
        encoding['encoding'] = enc_raw[read_position].encoding
        encoding['language'] = enc_raw[read_position].language
        #Ripped straight from charset_normalizer source
        #confidence = 1.0 - r.chaos if r is not None else None
        encoding['confidence'] = 1.0 - enc_raw[read_position].chaos

        if self.__istext:
            return encoding
        return null

    def __del__(self) -> None:#DONE
        '''
        Destructor closes file
        '''
        self.__fobj_bin.close()

    def produce_digest(self, prot: str = 'md5', blocksize: int = 2**16) -> str: #DONE
        '''
        Returns hex digest for object

        Parameters
        ----------
        prot : str, default='md5'
            Hash type. Supported hashes: 'sha1', 'sha224', 'sha256',
            'sha384', 'sha512', 'blake2b', 'blake2s', 'md5'.
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

        Parameters
        ----------
        **kwargs : dict

        flatfile : bool
            If not flatfile check will be ignored
        '''
        if not kwargs.get('flatfile'):
            return {'min_cols': 'N/A', 'max_cols': 'N/A', 'numrec' : 'N/A',
                    'constant': 'N/A', 'encoding': 'N/A'}

        options = {'.sav' : pyreadstat.read_sav,
                   '.dta' : pyreadstat.read_dta,
                   '.sas7bdat' : pyreadstat.read_sas7bdat}

        #Note: Pyreadstat is written in C, and the C library
        #asks for file paths, so good luck getting it to read a BytesIO object
        start = time.perf_counter()
        #There is no obvious way to get a tqdm progress bar for this operation
        #short of reprogramming the C code, and that's not going to happen.
        #So you get this.
        print(f'Analyzing statistical package file {self.fname}.',
              file=sys.stderr, end=' ')
        #--------
        #Use multiprocessing, because no one can wait two hours to process
        #a single large file
        _, meta = pyreadstat.read_file_multiprocessing(
                                read_function=options[self.fname.suffix.lower()],
                                file_path=self.fname,
                                num_processes=multiprocessing.cpu_count())
        #-----------
        finish = time.perf_counter()
        print(f'Elapsed time: {round(finish - start, 2)} seconds.',
              file=sys.stderr)
        self.encoding['encoding'] = meta.file_encoding
        return {'min_cols':meta.number_columns,
                'max_cols':meta.number_columns,
                #'numrec': len(content),
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

        Parameters
        ----------
        **kwargs: dict

        Other parameters
        ----------------
        fname : str
            Path/filename
        flatfile : bool
            Boolean representing a flat ascii file
        asctest : bool
            Perform character check, if the file is a text file

        Returns
        -------
        `[{'row': int, 'col':int, 'char':str}...]`

        Notes
        -----
        returns [] if not self.__istext
        '''
        if (not kwargs.get('asctest', False)#AAAGH
            or not self.__istext
            or not kwargs.get('flatfile')):
            return []
        outlist = []
        total = self.__text_obj.getvalue().count('\n')+1
        self.__text_obj.seek(0)
        for rown, row in tqdm.tqdm(enumerate(self.__text_obj),
                                   total=total,
                                   desc=f'Non-ASCII character check for {self.fname.name}'):
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

        Parameters
        ----------
        **kwargs : dict

        Other parameters
        ----------------
        flatfile : bool
            Test is useless if not a text file. If False, returns 'N/A'
        '''
        if (not kwargs.get('flatfile')
                or not self.__istext
                or not kwargs.get('null_chars')):
            return None
        if '\x00' in self.__text_obj.getvalue():
            return self.__text_obj.getvalue().count('\x00')
        return None

    def dos(self, **kwargs) -> bool: #DONE
        '''
        Checks for presence of carriage returns in file

        Returns True if a carriage return ie, ord(13) is present

        Parameters
        ----------
        **kwargs : dict

        Other parameters
        ----------------
        flatfile : bool
            Perform rectangularity check. If False, returns dictionary
            with all values as 'N/A'
        '''
        if not kwargs.get('flatfile') or not self.__istext:
            return None
        return b'\r\n' in self.__fobj_bin.getvalue()

    def _mime_type(self, fname:pathlib.Path)->tuple:
        '''
        Returns mimetype or 'application/octet-stream'

        Parameters
        ---------
        fname : pathlib.Path
            pathlib.Path to file
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

        Parameters
        ----------
        **kwargs : dict
        digest : str
            Hash algorithm. Default 'md5'
        flat : bool
            Flat file checking.
        nonascii : bool
            Check for non-ASCII characters.
        flatfile : bool
            Perform rectangularity check. If False, returns dictionary
            with all values as 'N/A'
        null_chars : bool
            Check for null characters

        Notes
        -----
        Sample output:
        ```
        {'filename':'/tmp/test.csv',
        'flat': True,
        'min_cols': 100, 'max_cols': 100, 'numrec' : 101, 'constant': True,
        'nonascii':False,
        'dos':False}
        ```
        '''
        out = {'filename': self.fname}
        digest = kwargs.get('digest', 'md5')
        #dos = kwargs.get('dos')
        update_these = [
        {'digestType' : digest},
        {'digest' : self.produce_digest(digest)}, #OK
        self.flat_tester(**kwargs), #OK
        {'nonascii': self.non_ascii_tester(**kwargs)}, # Slow but acceptable
        {'encoding': self.encoding['encoding']}, #OK
        {'null_chars': self.null_count(**kwargs)}, #Not great, but better
        {'mimetype': self._mime_type(self.fname)}, #OK
        {'dos': self.dos(**kwargs)}]

        #for upd in tqdm.tqdm(update_these, desc='Processing'):
        for upd in update_these:
            out.update(upd)

        return out

    def _manifest_txt(self, **kwargs)->str:
        '''
        Returns manifest as plain text

        Parameters
        ----------
        **kwargs : dict
        '''
        return '\n'.join([f'{k}: {v}' for k,v in kwargs['report'].items()
                          if v not in ['', None]])

    def _manifest_json(self, **kwargs)->str:
        '''
        Returns manifest as JSON

        Parameters
        ----------
        **kwargs : dict
        '''
        out = kwargs['report'].copy()
        out['filename'] = str(kwargs['report']['filename'])
        return json.dumps(out)

    def _manifest_csv(self, **kwargs)->str:
        '''
        Returns manifest as [whatever]-separated value

        Parameters
        ----------
        **kwargs : dict
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

        Parameters
        ----------
        **kwargs : dict

        Other parameters
        ----------------
        out : str
            Acceptable values are 'txt', 'json', 'csv'
            'txt' Plain text
            'json' JSON
            'csv' Comma-separated value
        digest : str
            Hash algorithm. Default 'md5'
        flat : bool
            Flat file checking. Default True
        nonascii : bool
            Check for non-ASCII characters. Default True
        dos : bool
            check for Windows CR/LF combo. Default True
        flatfile : bool
            Perform rectangularity check. If False, returns dictionary
            with all values as 'N/A'
        headers : bool, default=False
            Include csv header (only has any effect with out='csv')
        sep : str
            Separator if you want a different plain text separator like a
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
