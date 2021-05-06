<a name="fcheck"></a>
# fcheck

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

<a name="fcheck.Checker"></a>
## Checker Objects

```python
class Checker()
```

A collection of various tools attached to a file

<a name="fcheck.Checker.__init__"></a>
#### \_\_init\_\_

```python
 | __init__(fname: str)
```

Initializes Checker instance

    fname : str
        Path to file

<a name="fcheck.Checker.__del__"></a>
#### \_\_del\_\_

```python
 | __del__()
```

Destructor closes file

<a name="fcheck.Checker.produce_digest"></a>
#### produce\_digest

```python
 | produce_digest(prot: str = 'md5', blocksize: int = 2*16) -> str
```

Returns hex digest for object

    fname : str
       Path to a file object

    prot : str
       Hash type. Supported hashes: 'sha1', 'sha224', 'sha256',
          'sha384', 'sha512', 'blake2b', 'blake2s', 'md5'.
          Default: 'md5'

    blocksize : int
       Read block size in bytes

<a name="fcheck.Checker.flat_tester"></a>
#### flat\_tester

```python
 | flat_tester(**kwargs) -> dict
```

Checks file for line length and number of records.

Returns a dictionary:

`{'min_cols': int, 'max_cols' : int, 'numrec':int, 'constant' : bool}`

<a name="fcheck.Checker.non_ascii_tester"></a>
#### non\_ascii\_tester

```python
 | non_ascii_tester(**kwargs) -> list
```

Returns a list of dicts of positions of non-ASCII characters in a text file.

`[{'row': int, 'col':int, 'char':str}...]`

    fname : str
       Path/filename

    Keyword arguments:

        flatfile : bool
           — Perform rectangularity check. If False, returns dictionary
             with all values as 'N/A'

<a name="fcheck.Checker.dos"></a>
#### dos

```python
 | dos(**kwargs) -> bool
```

Checks for presence of carriage returns in file

Returns True if a carriage return ie, ord(13) is present

Keyword arguments:

    flatfile : bool
        — Perform rectangularity check. If False, returns dictionary
          with all values as 'N/A'

<a name="fcheck.Checker.manifest"></a>
#### manifest

```python
 | manifest(out: str = 'txt', **kwargs)
```

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

