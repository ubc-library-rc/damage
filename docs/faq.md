# Frequently asked questions

**What is the point of this application?**

* **Damage** is designed to ease the distribution of data by providing a standardized listing of checksums and record lengths, which ideally will be distributed with the data set itself. This allows end-users to duplicate the procedure and compare results.

    **If you're a data provider**

    Use **Damage** to create a data manifest which you distribute with your data and documentation. This will allow users to verify that they have *exactly* what you intend them to have.

    **If you're a data user**

    Use **Damage** to verify that what you've received from a data provider is what they're supposed to have given you.

    **Bonus points**

    If both parties shorten file paths and use the same directory structure, then the *manifests* can be compared. If the checksums of the manifests are not identical, then the data structures are not identical.

**Why is there no printer dialogue when I print from _Damage_?**

* The application prints text directly to default printer; there's no formatting. For more nicely formatted text, consider opening the output document in a text editor or spreadsheet.

**I can't edit values in _Damage's_ csv mode?**

* This is the expected behaviour. If you need to edit the CSV, please use a spreadsheet application.

**Why would you call the software "damage"?**

* Command line utility names are not easy to remember. Typing 'damage [filename'] for the first time will burn the name into your memory.

**Why does the software hang during examination of text files?**

* Most of the time, the software hasn't actually crashed; it's still doing its processing, possibly more slowly than one would like. There can be two reasons for this:
	1. Every character in a text file is examined; if your file is large, the amount of time this requires is not negligble.
	2. There have been instances of file corruption where data is replaced by [null characters](https://en.wikipedia.org/wiki/Null_character). Using versions previous to v0.1.3 output the row and column location of every such character, which takes a very long time if there are, as has happened, tens of millions of these characters. Versions >= v0.1.3 changed this behaviour and simply output a count.

**I try to run _damage_ from Windows explorer or Finder and it doesn't work. What's going on?**

* If you installed with `pipx` or `pip`, make sure you are running the GUI version of _damage_ and not the command line version.

* Multi-platform capablity is hard. I develop mostly for Mac and Linux, and Windows errors can slip through the cracks. If you are having problems, please [report an issue](https://github.com/ubc-library-rc/damage/issues).

**What's all this PATH and /usr/local/bin stuff?**

* PATH is an environment variable on your computer which allows programs to invoked without laboriously typing out the full location of the program. On linux-like systems, _/usr/local/bin_ is already part of the PATH environment variable, so just moving/copying the damage executable file there will do all the work in one step. If you are using _damage.py_, ie, you installed _fcheck_ with _pip_, you don't need to do any of this unless you really want to.
 
