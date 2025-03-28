#API Reference
<a id="damage"></a>

## damage

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

<a id="damage.Checker"></a>

### Checker Objects

```python
class Checker()
```

A collection of various tools attached to a file

<a id="damage.Checker.__init__"></a>

##### \_\_init\_\_

```python
def __init__(fname: str) -> None
```

Initializes Checker instance

    fname : str
        Path to file

<a id="damage.Checker.__del__"></a>

##### \_\_del\_\_

```python
def __del__() -> None
```

Destructor closes file

<a id="damage.Checker.produce_digest"></a>

##### produce\_digest

```python
def produce_digest(prot: str = 'md5', blocksize: int = 2 * 16) -> str
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

<a id="damage.Checker.flat_tester"></a>

##### flat\_tester

```python
def flat_tester(**kwargs) -> dict
```

Checks file for line length and number of records.

Returns a dictionary:

`{'min_cols': int, 'max_cols' : int, 'numrec':int, 'constant' : bool}`

<a id="damage.Checker.non_ascii_tester"></a>

##### non\_ascii\_tester

```python
def non_ascii_tester(**kwargs) -> list
```

Returns a list of dicts of positions of non-ASCII characters in a text file.

`[{'row': int, 'col':int, 'char':str}...]`

    fname : str
       Path/filename

    Keyword arguments:

        `flatfile` : bool
        asctest : bool
           — Perform character check (assuming it is text)

<a id="damage.Checker.null_count"></a>

##### null\_count

```python
def null_count(**kwargs) -> dict
```

Returns an integer count of null characters in the file
(' ') or None if skipped

Keyword arguments:

        flatfile : bool
           — Test is useless if not a text file. If False, returns 'N/A'

<a id="damage.Checker.dos"></a>

##### dos

```python
def dos(**kwargs) -> bool
```

Checks for presence of carriage returns in file

Returns True if a carriage return ie, ord(13) is present

Keyword arguments:

    flatfile : bool
        — Perform rectangularity check. If False, returns dictionary
          with all values as 'N/A'

<a id="damage.Checker.manifest"></a>

##### manifest

```python
def manifest(**kwargs) -> str
```

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
        tab (	) or pipe (|). Only functional with csv output, obviously.

