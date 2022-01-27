# Creating a binary damage

Not everyone has a python installation on their computer, and even if they do, they don't necessarily know how to use it. As damage is supposed to be simple to use, the easiest way to use it is as a traditional application. This means it needs to be compiled or packaged into, ideally, a single file.

> Note that you only need to this if there is not a binary version of **damage** available for your platform. Normally you would just download the software from the [releases](https://github.com/ubc-library-rc/fcheck/releases) page. 

Users most likely to require a custom binary version of damage are:

* Linux users
* Mac users who are using machines with M1 processors
* Users with ARM chips or other uncommon system architecture

To perform these steps, you will need  [PyInstaller] along with an installed version of Python >= v3.6. Although these examples use absolute paths, that's not technically required. You can install PyInstaller the usual way with _pip_. ie. `pip install PyInstaller`

## Building with Pyinstaller

Depending on your Python installation, you may need to build with a virtual environment (which you should probably do anyway).

Damage doesn't have a lot of dependencies; you really only need pyreadstat, which installs pandas and numpy as dependencies.

or, as the output of `pip freeze`:

```
altgraph==0.17
importlib-metadata==4.0.1
macholib==1.14
numpy==1.20.2
pandas==1.2.4
pyinstaller==4.3
pyinstaller-hooks-contrib==2021.1
pyreadstat==1.1.0
python-dateutil==2.8.1
pytz==2021.1
six==1.15.0
typing-extensions==3.10.0.0
zipp==3.4.1
```

```
pyinstaller -F --additional-hooks-dir ./  --hidden-import pyreadstat._readstat_writer --hidden-import pandas --hidden-import pyreadstat.worker --hidden-import multiprocessing /path/to/damage.py
```
Alternately, you can simplify the PyInstaller command by using the `py_install/hook-fcheck.py` file:

```
pyinstaller -F --additional-hooks-dir=/path/to/py_install  /path/to/damage.py
```

This process will create a damage.spec file along with a *build* and a *dist* dir. Inside the *dist* dir will be your self-contained file, which you can do with as you like.

Normally, on MacOS and linux system, the resultant **damage** file is placed in `/usr/local/bin` and for Windows computers, the **damage.exe** file is placed somewhere on you system `PATH`.


