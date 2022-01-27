# Frequently asked questions

**Why would you call the software "damage"?**

* Command line utility names are not easy to remember. Typing 'damage [filename'] for the first time will burn the name into your memory.

**Can I rename the program?**

* If you don't like the *frisson* of danger from the name, you can rename the binary files to whatever you like. `manifest_generator` is an obvious, if lengthy choice.

**Why does the software hang during examination of text files?**

* Most of the time, the software hasn't actually crashed; it's still doing its processing, possibly more slowly than one would like. There can be two reasons for this:
	1. Every character in a text file is examined; if your file is large, the amount of time this requires is not negligble.
	2. There have been instances of file corruption where data is replaced by [null characters](https://en.wikipedia.org/wiki/Null_character). Using versions previous to v0.1.3 output the row and column location of every such character, which takes a very long time if there are, as has happened, tens of millions of these characters. Versions >= v0.1.3 changed this behaviour and simply output a count.
	3. TLDR; upgrade to the latest version.
