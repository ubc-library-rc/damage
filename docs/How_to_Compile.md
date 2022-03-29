## How to compile a PySimpleGUI (or TKinter!) app

1. You must use Python 3.8 or above or it will crash Mojave and possibly Catalina.

2. Use PyInstaller, although I have admittedly not tried with nuitka. Nuitka would probably take all day to compile.

3. `Python310 -m PyInstaller  --onefile --add-binary='/System/Library/Frameworks/Tk.framework/Tk':'tk' --windowed --add-binary='/System/Library/Frameworks/Tcl.framework/Tcl':'tcl' -p ./path/to/imports/ path/to/script.py'  

The `-p` switch forces it to look for local imports. There is probably a better way to do it and it may not be necessary if the import statements are crafted correctly (cf. `dryad2dataverse`).

See the Pysimplegui.org page and look for `PyInstaller` for their most recent Mac/PC compilation notes.


16 Feb 22

python310 -E -m PyInstaller  --onefile --add-binary='/System/Library/Frameworks/Tk.framework/Tk':'tk' --windowed --add-binary='/System/Library/Frameworks/Tcl.framework/Tcl':'tcl' --additional-hooks-dir ~/Documents/Work/Projects/fcheck/py_install/ /path/to/05_app.py  

#23 Mar 22
Also
<https://pyinstaller.readthedocs.io/en/stable/spec-files.html>

Adding to the plist:

app = BUNDLE(exe,
         name='myscript.app',
         icon=None,
         bundle_identifier=None,
         version='0.0.1',
         info_plist={
            'NSPrincipalClass': 'NSApplication',
            'NSAppleScriptEnabled': False,
            'CFBundleDocumentTypes': [
                {
                    #'CFBundleTypeName': 'My File Format',
                    'CFBundleTypeIconFile': 'MyFileIcon.icns',
                    'LSItemContentTypes': ['com.example.myformat'],
                    'LSHandlerRank': 'Owner'
                    }
                ]
            },
         )

find pyi-makespec with more `which pyi-makespec`

*NOTE: --onefile on Mac isn't even required.* Doing so just makes one file, which must then be unpacked to make an app package which isn't even even a single file in the first place. It then doesn't have to unpack itself into a temp file and runs like a normal app. Jesus.

python310 -E -m PyInstaller   --add-binary='/System/Library/Frameworks/Tk.framework/Tk':'tk' --add-binary='/System/Library/Frameworks/Tcl.framework/Tcl':'tcl' --additional-hooks-dir ../py_install/ --icon=assets/DamageAppIcon.icns src/damage_gui.py --osx-bundle-identifier=ca.ubc.library --target-arch=x86_64 --noconsole

so, in the above, for mac, --onefile is not there. Add --noconsole so you don't get the annoying console window.

## Building a specfile for Mac
python310 -m PyInstaller.utils.cliutils.makespec --noconsole --add-binary='/System/Library/Frameworks/Tk.framework/Tk':'tk' --add-binary='/System/Library/Frameworks/Tcl.framework/Tcl':'tcl' --additional-hooks-dir ../py_install/ --icon=assets/DamageAppIcon.icns --osx-bundle-identifier=ca.ubc.library --target-arch=x86_64 src/damage_gui.py


Then manually add plist info to the specfile before using the spec file. For better versioning, read the VERSION string from the source code and insert it as a version number so that it does not have to be done manually.

Note that the mac does *not* have  --onefile OR --windowed. I reiterate because it's important.

## Building a specfile for Windows
It's very similar, except use --onefile, ignore the --add-binary, --osx-bundle-identifer (although I think you can include it), and use
--icon=assets/DamageAppIcon.ico

**a note about the ICO** file
If the ICO file is in the wrong format, the application will fail to compile. Worse, it can appear to compile successfully, but no output exe is made. The only successful method of creating an ICO I have found is as follows.
1. RGB (not RGBA)
2. Save original as JPG
3. Using Irfanview, save as an .ico file without transparency

This produces an overly large .ico, but it works. Normal methods, such as using  PIL.Image.sav('somefile.ico', sizes=[(128,128),(64,64)], produce an ICO but the application fails to compile without any indication as to why. Just renaming a solitary jpg or png to ico (which is also supposed to work) will cause PyInstaller to fail, but at least it will tell you it fails.

##Combined spec file
It is possible to make a multiplatform spec (which is there as `gui/damaage_gui_combined.spec`. This compiles successfully on both Windows and Mac. They were manually combined, so any changes in a .spec will have to be updated manually.

Using the spec file is easy:

`python310 -m PyInstaller --clean damage_gui_combined.spec` 

The --clean is optional, as is --noconfirm

#Building a mac application that doesn't run from a temporary directory

1. Build the application, not a specfile, using the command above.
2. Manually add the information to the generated plist, which is at:
`dist/damage_gui.app/Contents/Info.plist`
3. Use the python plist tools (plistlib) to add the correct keys:
```
 info_plist={
	       	    'NSPrincipalClass': 'NSApplication',
	       	    'NSAppleScriptEnabled': False,
	       	    'CFBundleDocumentTypes': [
	       		{
	       		    #'CFBundleTypeName': 'My File Format',
	       		    'CFBundleTypeIconFile': 'assets/DamageAppIcon.icns',
	       		    '#LSItemContentTypes': ['com.example.myformat'],
	       		    'LSHandlerRank': 'Alternate',
			    'CFBundleTypeRole': 'Editor'
	       		    }
```
 
