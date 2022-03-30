# Creating your own Damage app

The **Damage** GUI application, unlike the console program, isn't included when installing **fcheck**, either using `pip` or from the source code itself.

Because the **Damage** app uses **tkinter**, there are a number of problems that can arise, notably on Mac computers. Should you want to build the app, here are some guidelines on how to go about it.

* The build process doesn't use the same Python version as the **fcheck** module and the console utility. You will note in `setup.py` that it says `python_requires:'>=3.6'`. **THIS IS NOT (NECESSARILY) TRUE FOR BUILDING THE GUI APP**, notably on Mac computers, due to issues with **tkinter**. The app was built using Python 3.10.2 on Mac.

* Building the app requires the installation of **PyInstaller** and **PySimpleGUI**, as well as the installation of **fcheck**

## Procedure

### Windows and Linux computers
For Windows and Linux, the easiest way is to build using the included PyInstaller .spec file. Change to the `gui` directory and run

`python3 -m PyInstaller --clean --noconfirm damage_gui_combined.spec`

If you don't want to use the premade .spec file:

`python3 -m PyInstaller --onefile --additional-hooks-dir ../py_install/  --name  Damage --clean --noconfirm [any additional options go here] src/damage_gui.py`

Note that for Windows and Linux, any version of Python >=3.6 should suffice, unlike for Mac computers.

The resultant application will be in the `dist` directory; place it wherever you like,

### MacOS

For Mac computers, you can technically use the same procedure as above. However, it's a bit redunant for Mac, as there's no real reason to create the `--onefile --windowed` version as Mac apps are, by default, directories anyway.

The solution is to run PyInstaller without those options, editing the resulting plist file.

That is, in the source directory, run PyiInstaller, where `python310` is the path to your Python 3.10 or higher Python

`python310 -m PyInstaller   --add-binary='/System/Library/Frameworks/Tk.framework/Tk':'tk' --add-binary='/System/Library/Frameworks/Tcl.framework/Tcl':'tcl' --additional-hooks-dir ../py_install/ --icon=assets/DamageAppIcon.icns --osx-bundle-identifier=ca.ubc.library --target-arch=x86_64 --noconsole --clean --noconfirm --name Damage src/damage_gui.py`

And then,

from the same directory:

`python310 customize_pyinstaller_plist.py`

Once that is completed, there will be Mac app bundle in `dist` which doesn't require unpacking at runtime. The completed app bundle can then be placed into DMG container for distribution, if required.
