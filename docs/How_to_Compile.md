## How to compile a PySimpleGUI (or TKinter!) app

1. You must use Python 3.8 or above or it will crash Mojave and possibly Catalina.

2. Use PyInstaller, although I have admittedly not tried with nuitka. Nuitka would probably take all day to compile.

3. `Python310 -m PyInstaller  --onefile --add-binary='/System/Library/Frameworks/Tk.framework/Tk':'tk' --windowed --add-binary='/System/Library/Frameworks/Tcl.framework/Tcl':'tcl' -p ./path/to/imports/ path/to/script.py'  

The `-p` switch forces it to look for local imports. There is probably a better way to do it and it may not be necessary if the import statements are crafted correctly (cf. `dryad2dataverse`).

See the Pysimplegui.org page and look for `PyInstaller` for their most recent Mac/PC compilation notes.


16 Feb 22

python310 -E -m PyInstaller  --onefile --add-binary='/System/Library/Frameworks/Tk.framework/Tk':'tk' --windowed --add-binary='/System/Library/Frameworks/Tcl.framework/Tcl':'tcl' --additional-hooks-dir ~/Documents/Work/Projects/fcheck/py_install/ /path/to/05_app.py  
