import io
import os
import shlex
import shutil
import subprocess
import tempfile
import textwrap
import webbrowser

import fcheck
import PySimpleGUI as sg

if sg.running_mac():
    import plistlib
    ttk_theme = 'aqua'
    FONTSIZE = 14
    BASEFONT = 'System'
    MOD = '\u2318' #CMD key unicode 2318 Place of Interest
    CMDCTRL = 'Command' #tkinter bind string sans <>
else:
    ttk_theme =  'vista'
    FONTSIZE = 9
    BASEFONT = 'Arial' #GRR
    MOD = 'Ctrl'
    CMDCTRL = 'Control'
sg.set_options(font=f'{BASEFONT} {FONTSIZE}')

PROGNAME = (os.path.splitext(os.path.basename(__file__))[0])
VERSION = (0,2,0)
__version__ = '.'.join([str(x) for x in VERSION])

#TODO parse licence from main repo licence when ui moved to final directory.
LICENCE = textwrap.fill(replace_whitespace=False, text=
'''
MIT License

Copyright 2022 University of British Columbia Library

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
''' )

global prefdict

sg.theme('systemDefaultForReal')

def pref_path()->tuple:
    '''
    Returns path to preferences directory and preferences
    file name as a tuple
    '''
    if sg.running_linux():
        return (os.path.expanduser('~/.config/damage'),
                'damage.json')
    if sg.running_mac():
        return (os.path.expanduser('~/Library/Preferences'), 'ca.ubc.library.damage.prefs.plist')
    if sg.running_windows():
        return (os.path.expanduser('~/AppData/Local/damage'), 'damage.json')

def get_prefs()->None:
    '''
    Gets preferences from JSON or default dict. If no preferences
    file is found, one is written
    '''
    global prefdict
    fpath, fname = pref_path()
    preffile = fpath + os.sep +fname
    try:
        if sg.running_mac():
            with open(preffile, 'rb') as fn:
                prefdict = plistlib.load(fn)
        if sg.running_linux() or sg.running_windows():
            with open(preffile) as fn:
                prefdict = sg.json.load(fn)


    except FileNotFoundError:
        prefdict = dict(flatfile=False,
                        recurse=False,
                        digest='md5',
                        out='txt',
                        short=True,
                        headers=True,
                        nonascii=True
                        )
    #TODONE automatically fix prefdict['flat'] to be 'flatfile' or put in version check
    fixflat = prefdict.get('flat')
    if fixflat:
        prefdict['flatfile'] = fixflat
        del prefdict['flat']

def set_prefs()->None:
    '''
    Sets preferences
    '''
    fpath, fname = pref_path()
    preffile = fpath + os.sep + fname
    os.makedirs(fpath, exist_ok=True)
    if sg.running_mac():
        with open(preffile, 'wb') as fn:
            plistlib.dump(prefdict, fn)
    if sg.running_linux() or sg.running_windows():
        with open(preffile, 'w') as fn:
            sg.json.dump(prefdict, fn)

def damage(flist, **kwargs)->str:
    '''
    Text output from Damage utility
    '''
    if not flist:
        return None
    output = []
    for fil in flist:
        testme = fcheck.Checker(fil)
        output.append(testme.manifest(**kwargs))

    return '\n'.join(output)

def popup_files_chooser_mac(initialdir=None)->list:
    '''
    popup files chooser broken on Mac. This is the editted replacement.
    '''
    root = sg.tk.Toplevel()
    try:
        root.attributes('-alpha', 0)  # hide window while building it. makes for smoother 'paint'
        # if not running_mac():
        try:
            root.wm_overrideredirect(True)
        except Exception as e:
            print('* Error performing wm_overrideredirect in get file *', e)
        root.withdraw()
    except:
        pass
    #filename = sg.tk.filedialog.askopenfilenames(filetypes=[('All','*.*')],
    #                                          initialdir=os.path.expanduser('~'),
    #                                          #initialfile=default_path,
    #                                          parent=root if not sg.running_mac() else None)
    #                                          #defaultextension=default_extension)  # show the 'get file' dialog box
    filenames = sg.tk.filedialog.askopenfilenames(parent=root if not sg.running_mac() else None,
                                                  initialdir=initialdir)
    root.destroy()
    return filenames

def damage_table(flist, **kwargs)->(list, str): # Not used yet
    '''
    Create data for a tabular display
    '''
    output = []
    kwargs['header'] = True
    testme = fcheck.Checker(flist[0], **kwargs)
    #headers = testme.manifest(**kwargs)).split('\n')[0].split(',')
    #headers = [x.strip('"') for x in headers]
    output.append(testme.manifest(**kwargs))

    for fil in flist[1:]:
        kwargs['header'] = False
        testme=Checker(fil, **kwargs)
        output.append(testme.manifest(**kwargs))
    data = output.split('\n')
    data =[x.split(',') for x in data]
    data = [[y.strip('"')] for y in x for x in data]
    return data, output

def get_folder_files(direc:str, recursive:bool=False, hidden:bool=False)->list:
    '''
    Returns files in a folder, recursive or no
    direc : str
        path to directory
    recursive : bool
        Return a recursive result. Default False
    hidden : bool
        Show hidden files. Default False
    '''
    if not direc:#Possible if window call cancelled, as I have discovered
        #return None
        return []
    if not recursive:
        flist = [[direc, x] for x in os.listdir(os.path.expanduser(direc))
                 if os.path.isfile(os.path.expanduser(direc)+os.sep+x)]
    if recursive:
        flist = [[a, d] for a, b, c in os.walk(os.path.expanduser(direc)) for d in c]
    if not hidden:
        flist=[x for x in flist if not x[1].startswith('.')]
    #will this work?
    if sg.running_windows():
        flist = [[x[0].replace('/', os.sep), x[1]] for x in flist]
        #sg.Print(flist)
    return flist

def send_to_file(outstring)->None:
    '''
    Sends string output to file

    Creates a tk.asksaveasfile dialogue and saves
    '''
    #Because TK is just easier
    outfile = sg.tk.filedialog.asksaveasfile(title='Save Output',
                                       initialfile=f'output.{prefdict["out"]}',
                                       confirmoverwrite=True)
    if outfile:
        outfile.write(outstring)
        outfile.close()

def send_to_printer(outstring:str)->None:
    '''
    Sends output to lpr on Mac/linux and to default printer in Windows
    Data is unformatted. If you want formatting save to a file and use
    a text editor. Assumes UTF-8 for Mac/linux.
    '''
    #https://stackoverflow.com/questions/12723818/print-to-standard-printer-from-python
    outfile = tempfile.NamedTemporaryFile(mode='w', encoding='utf-8',
                                          suffix='.txt', delete=False)
    outfile.write(outstring)
    outfile.close()

    if sg.running_mac() or sg.running_linux():
        #lpr =  subprocess.Popen(shutil.which('lpr'), stdin=subprocess.PIPE)
        #lpr.stdin.write(bytes(outstring, 'utf-8'))
        subprocess.run([shutil.which('lpr'), outfile.name])

    if sg.running_windows():

        #List of all printers names and shows default one
        #wmic printer get name,default
        #https://stackoverflow.com/questions/13311201/get-default-printer-name-from-command-line
        subout = subprocess.run(shlex.split('wmic printer get name,default'),
                                capture_output=True)
        #the following only makes sense of you look at the output of the
        #windows shell command above. stout is binary, hence decode.
        printerinfo = [[x[:6].strip(), x[6:].strip()] for x in
                        subout.stdout.decode().split('\n')[1:]]
        default_printer = [x for x in printerinfo if x[0] == 'TRUE'][0][1]
        subprocess.run(['print', f'/D:{default_printer}', outfile.name])
        #tempfile must be removed manually because of delete=False above
    os.remove(outfile.name)
    sg.popup('Output sent to default printer', title='Job Completed', any_key_closes=True)

def platform_menu(): # Not used yet
    '''
    Platform specific menus
    '''
    if running_mac():
        pass
        #Goddamn it

def about_window()->sg.Window:
    '''
    Creates the "About" window
    '''
    about = dict(developers = ['Paul Lesack'],
                 user_testers = ['Jeremy Buhler'],
                 source_url = 'https://github.com/ubc-library-rc/fcheck',
                 documentation = 'https://ubc-library-rc.github.io/fcheck'
                 )
    name = [[sg.Text(f'{PROGNAME} v{__version__}', font=f'{BASEFONT} {FONTSIZE+4} bold')]]
    source =[[sg.Text('Source code', font=f'{BASEFONT} {FONTSIZE+2} bold')],
              [sg.Text(about['source_url'], enable_events=True, text_color='blue', k='-SC-')]]
    documentation =[[sg.Text('Documentation', font=f'{BASEFONT} {FONTSIZE+2} bold')],
                     [sg.Text(about['source_url'], enable_events=True, text_color='blue', k='-DOC-')]]
    devs =[[sg.Text('Developers', font=f'{BASEFONT} {FONTSIZE+2} bold',)],
            [sg.Text(x) for x in about['developers']]]
    testers = [[sg.Text('Testers', font=f'{BASEFONT} {FONTSIZE+2} bold')],
               [sg.Text(x) for x in about['user_testers']]]
    licence =[[sg.Text('Licence information', font=f'{BASEFONT} {FONTSIZE+2} bold')],
              [sg.Text(LICENCE, font=f'{BASEFONT} {FONTSIZE-2}')]]
    layout = name + documentation + devs + testers + source + licence
    window = sg.Window('About', modal=True,
                       keep_on_top=True,
                       layout=layout,
                       finalize=True)
    while True:
        event, values = window.read()
        if event == '-SC-':
            webbrowser.open(about['source_url'])
        if event == '-DOC-':
            webbrowser.open(about['documentation'])
        if event == sg.WIN_CLOSED:
            break
    window.close()

def prefs_window()->sg.Window:
    '''
    Creates a preferences popup window.
    Values from window  saved to the preferences dictionary prefdict
    '''
    #All the options
    hashes =['md5','sha1', 'sha224', 'sha256', 'sha384', 'sha512',
             'blake2b', 'blake2s']
    outputs = ['txt','csv', 'json']
    layout = [[sg.Text('Damage Preferences', font=f'{BASEFONT} {FONTSIZE+4} bold')],
             [sg.Checkbox('Shorten file paths in output',
                           key= '-SHORT-',
                           default=prefdict['short'], )],
             [sg.Checkbox('Text file rectangularity check',
                           key= '-FLAT-',
                           default=prefdict['flatfile'], )],
             [sg.Checkbox('Recursively add files from directories',
                           key='-RECURSE-', default=prefdict['recurse'])],
             [sg.Text('Hash type'),
              sg.Combo(values=hashes, default_value=prefdict['digest'],
                       key='-DIGEST-', readonly=True)],
             [sg.Text('Output format'),
              sg.Combo(values=outputs, default_value=prefdict['out'],
                       key='-OUT-', readonly=True)],
             [sg.Ok(bind_return_key=True)]]
    pwindow = sg.Window(title='Preferences',
                     resizable=True,
                     layout=layout,
                     ttk_theme=ttk_theme,
                     use_ttk_buttons=True,
                     keep_on_top=True,
                     modal=True, finalize=True)
    pwindow.bind('<Escape>', 'Exit')
    pevent, pvalues = pwindow.read()
    if pevent:
        for key in ['short', 'flat', 'recurse', 'digest', 'out']:
            prefdict[key] = pvalues[f'-{key.upper()}-']
    set_prefs()
    if pevent == 'Exit':
        pwindow.close()
    pwindow.close()

def window_binds(window:sg.Window)->None:
    '''
    Bind keys to main window
    '''
    #window.bind(f'<{CMDCTRL}>', eventname)
    #sg.Print(f'<{CMDCTRL}-c>', '-COPY-')
    #window.bind(f'<{CMDCTRL}-c>', '-COPY-')
    #sg.Print(f'<{CMDCTRL}-v>', '-PASTE-')
    window.bind(f'<{CMDCTRL}-v>', '-PASTE-')
    window.bind(f'<{CMDCTRL}-s>', '-SAVE-')
    window.bind(f'<{CMDCTRL}-p>', '-PRINT-')

def main_window()->sg.Window:
    '''
    The main damage window
    '''
    #def get_folder_items()->list:
    #    '''
    #    Get all items from a folder listing
    #    '''
    #I gave up attaching preferences to the mac menu
    #because there's too much hidden using sg.
    #You may as well use straight tk if you want that.
    menu = sg.Menu([['File',['Add &Files',
                             'Add Fol&der',
                             '---',
                             f'!&Save Output to File          {MOD}S::-SAVE-',
                             f'!&Print Output                      {MOD}P::-PRINT-']],
                             ['Edit', [f'&Copy     {MOD}C::-COPY-',
                                 f'&Paste    {MOD}V::-PASTE-',
                              'Preferences']],
                    ['Help', ['Damage Help', 'Credits and Details']]],
                    key='-MENUBAR-')

    lbox = sg.Listbox(values=[], key='-SELECT-',
                          enable_events=True,
                          size=20,
                          select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED,
                          horizontal_scroll=True,
                          expand_y=True,
                          expand_x=True)
    left = [[lbox],
            [sg.Input(visible=False, enable_events=True, key='-IN-'),
             sg.FilesBrowse(button_text='Add Files', target='-IN-'),
             sg.Input(visible=False, enable_events=True, key='-IFOLD-'),
             sg.FolderBrowse(button_text='Add Folder', key='-FOLDER-', target='-IFOLD-'),
             sg.Button(button_text='Remove Files',
                       enable_events=True, key='-DELETE-')]]

    right = [[sg.Multiline(key='-OUTPUT-',
                           size=40,
                           expand_x=True,
                           expand_y=True)],
             [sg.Text(expand_x=True),
              sg.Button('Generate Manifest',
                         key='-MANIFEST-') ]]

    layout = [[menu],
                [sg.Frame(title='File Section',
                         layout=left,
                         size=(400,800),
                         expand_y=True,
                         expand_x=True),
            sg.Frame(title='Output Section',
                     size=(800,800),
                     layout=right,
                     expand_y=True,
                     expand_x=True)]]

    print(prefdict.get('main_size'))
    window = sg.Window(title='Damage', layout=layout, resizable=True,
                      size = prefdict.get('main_size', (None, None)),
                      ttk_theme=ttk_theme,
                      use_ttk_buttons=True,
                      location= prefdict.get('main_location', (None, None)),
                      finalize=True, enable_close_attempted_event=True)
    lbox.Widget.config(borderwidth=0)
    #sg.Print(vars(layout[1][0]))
    window.set_min_size((875,400))
    window_binds(window)
    return window

def main()->None:
    '''
    Main loop
    '''
    #TODO Windows not stripping out dups when adding from two different methods. 
    #TODO Icon
    #TODO CSV tabular output
    #TODONE Help
    #TODONE platform specific menu shortcuts
    #TODONE DONE File menus behave differently from buttons
    #TODONE bind keys to shortcuts

    get_prefs()
    window  = main_window()
    #FFFFUUUUU
    menulayout = window['-MENUBAR-'].MenuDefinition
    #Why don't I just do it all in TK? Jesus
    #talk about undocumented.
    #also: https://tkdocs.com/tutorial/menus.html
    #window.TKroot.tk.createcommand('tk::mac::ShowPreferences', prefs_window ) # How to get root? What is the function where None is?
    root = window.hidden_master_root #(see PySimpleGUI.py.StartupTK, line 16008)
    #sg.Print(type(poot))
    #root.createcommand('tk::mac::ShowPreferences', prefs_window )
    #root.createcommand('tk::mac::ShowPreferences', lambda:  None)
    #Also, why does the window stop responding after calling the prefs? But only half? It's
    #a fucking mystery. And it doesn't happen with straight TK so it's something to with psg.
    #root.createcommand('tk::mac::standardAboutPanel', about_window)
    while True:
        event, values = window.read()
        #sg.Print(relative_location=(700,0))
        #sg.Print(event, values)
        #print(event)
        #sg.Print(prefdict)
        if event in (sg.WINDOW_CLOSE_ATTEMPTED_EVENT,):
            prefdict['main_size'] = window.size
            prefdict['main_location'] = window.current_location()
            set_prefs()
            break

        if event in (sg.WINDOW_CLOSED,):
            break

        if event == '-IN-':
            #sg.Print(f"Values=| {values['-IN-']} |", c='white on red')
            if len(values['-IN-']): # No way to set None, so empty is '', or len() == 0.
                if sg.running_windows():#FFFUUUU TK
                    #tk automatically replaces backlashes with slashes.
                    #too bad fcheck doesn't.
                    upd_list = (window['-SELECT-'].get_list_values() +
                                [x.replace('/', os.sep) for x in values['-IN-'].split(';') if
                                 x.replace('/', os.sep) not in window['-SELECT-'].get_list_values()])
                else:
                    upd_list = (window['-SELECT-'].get_list_values() +
                                [x for x in values['-IN-'].split(';') if
                                 x not in window['-SELECT-'].get_list_values()])
                upd_list = [x for x in upd_list if os.path.isfile(x)]
                #Fuck you tkinter for replacing os.sep with a slash
                #Maybe make this a function
                #if sg.running_windows():
                #    upd_list = [x.replace('/', os.sep) for x in upd_list]
                window['-SELECT-'].update(upd_list)
                window['-IN-'].update(value='')

        if event in ('-IFOLD-', 'Add Folder'):
            if event == 'Add Folder':
                newfiles = get_folder_files(sg.popup_get_folder('', no_window=True))
            else:
                newfiles = get_folder_files(values['-IFOLD-'], prefdict['recurse'])
                #sg.Print(newfiles, c='red on yellow')
            upd_list = (window['-SELECT-'].get_list_values() +
                   [x[0]+os.sep+x[1] for x in newfiles if
                    x[0]+os.sep+x[1] not in window['-SELECT-'].get_list_values()])
            upd_list = [x for x in upd_list if os.path.isfile(x)]
            window['-SELECT-'].update(upd_list)
        
        

        if event == '-DELETE-':
            nlist = [x for x in window['-SELECT-'].get_list_values() if
                    x not in values['-SELECT-']]
            window['-SELECT-'].update(nlist)
            #print(nlist)

        if event == '-MANIFEST-':
            try:
                delme = ''
                upd_list = window['-SELECT-'].get_list_values()
                if upd_list == ['']:
                    upd_list = []
                window['-OUTPUT-'].update('')
                if upd_list:
                    txt = damage(upd_list, **prefdict)
                    if prefdict['short'] and len(upd_list) > 1:
                        delme = os.path.commonpath(upd_list) + os.sep
                        window['-OUTPUT-'].update(txt.replace(delme,''))
                    elif prefdict['short'] and len(upd_list) == 1:
                        delme = os.path.split(upd_list[0])[0] + os.sep
                    txt = txt.replace(delme,'')
                    window['-OUTPUT-'].update(txt)

            except (ValueError, NameError, AttributeError):
                window['-OUTPUT-'].update('')

        if event == 'Preferences':
            prefs_window()
            window['-OUTPUT-'].update('')

        if window['-OUTPUT-'].get():
            #update menu. This is a PIA.
            menulayout[0][1][3] = f'&Save Output to File          {MOD}S::-SAVE-'
            menulayout[0][1][4] = f'&Print Output                      {MOD}P::-PRINT-'
            window['-MENUBAR-'].update(menulayout)

            if event.endswith('-SAVE-'):
                send_to_file(values['-OUTPUT-'])

            if event.endswith('-PRINT-'):
                send_to_printer(values['-OUTPUT-'])
        else:
            menulayout[0][1][3] = f'!&Save Output to File          {MOD}S::-SAVE-'
            menulayout[0][1][4] = f'!&Print Output                      {MOD}P::-PRINT-'
            window['-MENUBAR-'].update(menulayout)

        #Menubar events
        if event == 'Add Files':
            if sg.running_mac():#Mac will crash using sg.popup_get_file
                newfiles = popup_files_chooser_mac()
            else:
                newfiles = sg.popup_get_file(message='', no_window=True,
                                             multiple_files=True,
                                             file_types = sg.FILE_TYPES_ALL_FILES)
                if sg.running_windows():#Again, TK replaces \ with /.
                    newfiles= [x.replace('/', os.sep) for x in newfiles]
            upd_list = (window['-SELECT-'].get_list_values() +
                   [x for x in newfiles if
                    x not in window['-SELECT-'].get_list_values()])
            window['-SELECT-'].update(upd_list)

        if event == 'Credits and Details':
            about_window()
        if event == 'Damage Help':
            webbrowser.open('https://ubc-library-rc.github.io/fcheck')

        #Copypasta
        if event.endswith(':-COPY-'):
            #sg.clipboard_get()
            sg.clipboard_set(window['-OUTPUT-'].Widget.selection_get())
            #sg.Print('COPY!!!', c='white on blue')
            #sg.Print(sg.clipboard_get())
        if event.endswith(':-PASTE-'):#Menu only because pastes by default
            sg.Print('PASTE!!!', c='white on orange')
            window['-OUTPUT-'].Widget.insert(sg.tk.INSERT,
                                                sg.clipboard_get())

    window.close()

if __name__ == '__main__':
    main()


'''
#https://stackoverflow.com/questions/12723818/print-to-standard-printer-from-python
#printing
#MAC and Linux
import io
import subprocess
import shutil

fil = io.BytesIO(b'aljfdladjfa')
lpr = subprocess.Popen(shutil.which('lpr'), stdin=subprocess.PIPE)
lpr.stdin.write(fil.read())
'''


'''
#THIS PRINTS ON WINDOWS!
import os
import shlex #see splitting expression here: https://docs.python.org/3/library/subprocess.html
import tempfile
#import win32print
#https://pypi.org/project/pywin32/
#pywin32 comes with win32print
#text will be unformatted
outfile = tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.txt', delete=False)
outfile.write('your data here')
outfile.close()

#get a list of printers on windows:
subout = subprocess.run(shlex.split('wmic printer get name,default'), capture_output=True)
printerinfo = [[x[:6].strip(), x[6:].strip()] for x in subout.stdout.decode().split('\n')[1:]]
default_printer = [x for x in printerinfo if x[0] == 'TRUE'][0][1]

#List of all printers names and shows default one
#wmic printer get name,default
#https://stackoverflow.com/questions/13311201/get-default-printer-name-from-command-line
#subprocess.run(['print', f'/D:{win32print.GetDefaultPrinter()}', outfile.name])

subprocess.run(['print', f'/D:default_printer}', outfile.name])
os.remove(outfile.name)
'''

