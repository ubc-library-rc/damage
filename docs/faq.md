# Frequently asked questions

**Why is there no printer dialogue when I print from _Damage_?**

* The application prints text directly to default printer; there's no formatting. For more nicely formatted text, consider opening the output document in a text editor or spreadsheet

**I can't edit values in _Damage's_ csv mode?**

* This is the expected behaviour. If you need to edit the CSV, please use a spreadsheet application.

**Why would you call the software "damage"?**

* Command line utility names are not easy to remember. Typing 'damage [filename'] for the first time will burn the name into your memory.

**Can I rename the program?**

* If you don't like the *frisson* of danger from the name, you can rename the binary files to whatever you like. `manifest_generator` is an obvious, if lengthy choice.

**Why does the software hang during examination of text files?**

* Most of the time, the software hasn't actually crashed; it's still doing its processing, possibly more slowly than one would like. There can be two reasons for this:
	1. Every character in a text file is examined; if your file is large, the amount of time this requires is not negligble.
	2. There have been instances of file corruption where data is replaced by [null characters](https://en.wikipedia.org/wiki/Null_character). Using versions previous to v0.1.3 output the row and column location of every such character, which takes a very long time if there are, as has happened, tens of millions of these characters. Versions >= v0.1.3 changed this behaviour and simply output a count.
	3. TLDR; upgrade to the latest version.

**I try to run _damage_ from Windows explorer or Finder and it doesn't work. What's going on?**

* _damage_ is a _console_ program. That means it runs from with a Windows command prompt session or PowerShell session, and in the case of other computer sessions, within a terminal session. At this point, it doesn't have a GUI, although there's a chance that one may be added in the future.

**What's all this PATH and /usr/local/bin stuff?**

* PATH is an environment variable on your computer which allows programs to invoked without laboriously typing out the full location of the program. On linux-like systems, _/usr/local/bin_ is already part of the PATH environment variable, so just moving/copying the damage executable file there will do all the work in one step. If you are using _damage.py_, ie, you installed _fcheck_ with _pip_, you don't need to do any of this unless you really want to.
 
