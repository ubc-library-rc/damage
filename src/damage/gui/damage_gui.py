'''
Damage GUI application
'''
#import base64
import csv
#import io
import os
import shlex
import shutil
import subprocess
import tempfile
import textwrap
import webbrowser

import damage
#import PySimpleGUI as sg
import FreeSimpleGUI as sg

#Put ICON here
if sg.running_mac():
    import plistlib
    ttk_theme = 'aqua'
    FONTSIZE = 14
    BASEFONT = 'System'
    MOD = '\u2318' #CMD key unicode 2318 Place of Interest
    CMDCTRL = 'Command' #tkinter bind string sans <>
if sg.running_windows():
    ttk_theme =  'vista'
    FONTSIZE = 9
    BASEFONT = 'Arial' #GRR
    MOD = 'Ctrl-'
    CMDCTRL = 'Control'
if sg.running_linux():
    ttk_theme =  'alt'
    FONTSIZE = 9
    BASEFONT = 'TkDefaultFont' #GRR
    MOD = 'Ctrl-'
    CMDCTRL = 'Control'
sg.set_options(font=f'{BASEFONT} {FONTSIZE}')

PROGNAME = (os.path.splitext(os.path.basename(__file__))[0])
VERSION = (0,4,4)
__version__ = '.'.join([str(x) for x in VERSION])

#ICON is base64 text just above __main__ section
#with open(os.path.dirname(__file__) + f'{os.sep}..{os.sep}assets{os.sep}DamageAppIcon.png', 'rb') as f:
#    ICON = base64.b64encode(f.read())

#TODO parse licence from main repo licence when ui moved to final directory.
#This is probably not worth the effort. Similarly for the icon.

LICENCE = textwrap.fill(replace_whitespace=False, text=
'''
MIT License

Copyright 2023 University of British Columbia Library

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
    NB: headers is set to False as the header
    is hardcoded into the sg.Table on creation.
    '''
    if not flist:
        return None
    #kwargs['headers'] = False
    output = []
    for fil in flist:
        testme = damage.Checker(fil)
        output.append(testme.manifest(**kwargs))

    return '\n'.join(output)
    #return output

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
                 source_url = 'https://github.com/ubc-library-rc/damage',
                 documentation = 'https://ubc-library-rc.github.io/damage'
                 )
    displayname = f'{PROGNAME[:PROGNAME.find("_")].capitalize()} v{__version__}'
    name = [[sg.Text(displayname, font=f'{BASEFONT} {FONTSIZE+4} bold')]]
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
    window = sg.Window('Credits & Details', modal=True,
                       icon=ICON,
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
    rectang = ('Text file rectangularity '
                '& statistics file column check' )
    layout = [[sg.Text('Damage Preferences', font=f'{BASEFONT} {FONTSIZE+4} bold')],
             [sg.Checkbox('Shorten file paths in output',
                           key= '-SHORT-',
                           default=prefdict['short'], )],
             [sg.Checkbox(text=rectang,
                           key= '-FLATFILE-',
                           default=prefdict['flatfile'], )],
             [sg.Checkbox('Recursively add files from directories',
                           key='-RECURSE-', default=prefdict['recurse'])],
             [sg.Text('Hash type'),
              sg.Combo(values=hashes, default_value=prefdict['digest'],
                       key='-DIGEST-', readonly=True)],
             [sg.Text('Output format'),
              sg.Combo(values=outputs, default_value=prefdict['out'],
                       key='-OUT-', readonly=True)],
             [sg.Ok(bind_return_key=True, button_text='OK')]]
    pwindow = sg.Window(title='Preferences',
                    icon=ICON,
                     resizable=True,
                     layout=layout,
                     ttk_theme=ttk_theme,
                     use_ttk_buttons=True,
                     keep_on_top=True,
                     modal=True, finalize=True)
    pwindow.bind('<Escape>', 'Exit')
    pevent, pvalues = pwindow.read()
    if pevent:
        for key in ['short', 'flatfile', 'recurse', 'digest', 'out']:
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
    window.bind(f'<{CMDCTRL}-m>', '-MANIFEST-')

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

    #Menu section
    menu = sg.Menu([['File',['Add &Files',
                             'Add Fol&der',
                             'Remove Files::-DELETE-']],
                     ['Edit', [f'&Copy     {MOD}C::-COPY-',
                                 f'&Paste    {MOD}V::-PASTE-',
                              'Preferences']],
                     ['Actions', [f'Create &Manifest               {MOD}M::-MANIFEST-',
                                  '---',
                                  f'!&Save Output to File          {MOD}S::-SAVE-',
                                  f'!&Print Output                      {MOD}P::-PRINT-']],
                     ['Help', ['Damage Help', 'Credits and Details']]],
                    key='-MENUBAR-')
    #Chosen file (left) section
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
             sg.FolderBrowse(button_text='Add Folder', key='-FOLDER-', 
                             target='-IFOLD-',
                             initial_folder=os.path.expanduser('~')),
             sg.Button(button_text='Remove Files',
                       enable_events=True, key='-DELETE-')]]

    #Right side (output) section
    #This is more complicated than it should be because psg doesn't
    #flip correctly between Multiline and Table elements and doesn't hide
    #the Table scrollbars, and resizing is also affected. The (a) solution
    #is to put each of them in a Frame.
    #But the best solution would be to use straight tkinter but it's too
    #late for that, isn't it.

    #First determine which one should be shown at startup
    txtout = True if prefdict.get('out') != 'csv' else False
    #Text and JSON output, Frame 1
    #Text output box
    outbox = sg.Multiline(key='-OUTPUT-',
                           size=40,
                           expand_x=True,
                           expand_y=True,
                           visible=True)
    frame_1=sg.Frame(title ='',
                     layout=[[outbox]],
                     expand_x=True,
                     expand_y=True,
                     border_width=0,
                     key='F1',
                     visible=txtout)

    #CSV/tabular output box
    #hardcoding the headers seems dumb but this is alpha
    headers = ['filename', 'digestType', 'digest',
                'min_cols', 'max_cols', 'numrec',
                'constant', 'encoding', 'nonascii',
                'encoding', 'null_chars', 'dos']

    #right side layout
    csvout = sg.Table([['' for x in range(len(headers))]], #Need data to create the table
                headings=headers,
                key='-CSV-',
                #num_rows=40, #not needed with expansion
                alternating_row_color='#FFA805',
                #size=(800,40),
                expand_x=True,
                expand_y=True,
                hide_vertical_scroll=False,
                vertical_scroll_only=False,
                auto_size_columns=True,
                #def_col_width=200,#If this is at default window expansion doesn't work
                #max_col_width=2000,#This ought to be enough
                visible=True,
                enable_events=True
                )
    frame_2=sg.Frame(title ='',
                     layout=[[csvout]],
                     expand_x=True,
                     expand_y=True,
                     border_width=0,
                     key='F2',
                     visible=not txtout)


    right = [[frame_1, frame_2],
             [sg.Text(expand_x=True),
              sg.Button('Generate Manifest',
                         key='-MANIFEST-') ]]

    #Main window layout using all the elements above
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

    #print(prefdict.get('main_size'))
    window = sg.Window(title='Damage', layout=layout, resizable=True,
                      size = prefdict.get('main_size', (None, None)),
                      icon=ICON,
                      ttk_theme=ttk_theme,
                      use_ttk_buttons=True,
                      location= prefdict.get('main_location', (None, None)),
                      finalize=True, enable_close_attempted_event=True)
    lbox.Widget.config(borderwidth=0)
    #sg.Print(vars(layout[1][0]))
    window.set_min_size((875,400))
    window_binds(window)
    return window

def show_output_pane(window:sg.Window)->None:
    '''
    Flips output from CSV to plain text as required
    '''
    #Show correct window pane for output.
    if prefdict.get('out') =='csv':
        window['F1'].update(visible=False)
        window['F2'].update(visible=True)
    else:
        window['F1'].update(visible=True)
        window['F2'].update(visible=False)
    if window['F1'].visible:
        window['F1'].expand(expand_x=True, expand_y=True)
        window['F2'].expand(expand_x=False, expand_y=False)
    if window['F2'].visible:
        window['F2'].expand(expand_x=True, expand_y=True)
        #sg.Print(window['F2'].get_size())
    window.read()

def main()->None:
    '''
    Main loop
    '''
    #TODONE Windows not stripping out dups when adding from two different methods.
    #TODONE Icon
    #TODONE CSV tabular output
    #TODONE Help
    #TODONE platform specific menu shortcuts
    #TODONE DONE File menus behave differently from buttons
    #TODONE bind keys to shortcuts

    get_prefs()
    window  = main_window()
    #FFFFUUUUU
    menulayout = window['-MENUBAR-'].MenuDefinition
    #sg.Print(menulayout)
    #Why don't I just do it all in TK? Jesus
    #talk about undocumented.
    #also: https://tkdocs.com/tutorial/menus.html
    #window.TKroot.tk.createcommand('tk::mac::ShowPreferences', prefs_window ) # How to get root? What is the function where None is?
    #root = window.hidden_master_root #(see PySimpleGUI.py.StartupTK, line 16008)
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
                    #too bad damage doesn't.
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
            if event in ('Add Folder',):
                #Not implementing same behaviour in button
                #requires rewriting menu
                #TODO find a way to have the menu item
                #and button have the behaviour below
                #probably by having the button replaced by a function call.
                #initiald = window['-IFOLD-'].get()
                #if not initiald:
                #    initiald = os.path.expanduser('~')
                initiald = os.path.expanduser('~')
                newfiles = get_folder_files(sg.popup_get_folder('',
                                                                no_window=True,
                                                                initial_folder=initiald),
                                             prefdict['recurse'])
            else:
                newfiles = get_folder_files(values['-IFOLD-'], prefdict['recurse'])
                #sg.Print(newfiles, c='red on yellow')
            upd_list = (window['-SELECT-'].get_list_values() +
                   [x[0]+os.sep+x[1] for x in newfiles if
                    x[0]+os.sep+x[1] not in window['-SELECT-'].get_list_values()])
            upd_list = [x for x in upd_list if os.path.isfile(x)]
            window['-SELECT-'].update(upd_list)



        if event.endswith('-DELETE-'):
            nlist = [x for x in window['-SELECT-'].get_list_values() if
                    x not in values['-SELECT-']]
            window['-SELECT-'].update(nlist)
            #print(nlist)

        if event.endswith('-MANIFEST-'):
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

                if prefdict.get('out') == 'csv':
                    txt = txt.split('\n')
                    reader=csv.reader(txt[1::2], delimiter=',')#Strip out the headers
                    window['-CSV-'].update(values=list(reader))
                    nout = [txt[0]] + txt[1::2]#combine header with data
                    #sg.Print(f'NOUT {nout}')
                    window['-OUTPUT-'].update('\n'.join(nout))#and send to output window for printing/saving


            except (ValueError, NameError, AttributeError):
                window['-OUTPUT-'].update('')

        if event == 'Preferences':
            prefs_window()
            #Show correct window pane for output.
            if prefdict.get('out') =='csv':
                window['F1'].update(visible=False)
                window['F2'].update(visible=True)
            else:
                window['F1'].update(visible=True)
                window['F2'].update(visible=False)
            if window['F1'].visible:
                window['F1'].expand(expand_x=True, expand_y=True)
                window['F2'].expand(expand_x=False, expand_y=False)
            if window['F2'].visible:
                window['F2'].expand(expand_x=True, expand_y=True)
                window['F1'].expand(expand_x=False, expand_y=False)
                #sg.Print(window['F2'].get_size())
            window['-OUTPUT-'].update('')
            #window.read()
            window.refresh()

        if window['-OUTPUT-'].get():
            #update menu. This is a PIA.
            menulayout[2][1][2] = f'&Save Output to File          {MOD}S::-SAVE-'
            menulayout[2][1][3] = f'&Print Output                      {MOD}P::-PRINT-'
            window['-MENUBAR-'].update(menulayout)

            if event.endswith('-SAVE-'):
                send_to_file(values['-OUTPUT-'])

            if event.endswith('-PRINT-'):
                send_to_printer(values['-OUTPUT-'])
        else:
            menulayout[2][1][2] = f'!&Save Output to File          {MOD}S::-SAVE-'
            menulayout[2][1][3] = f'!&Print Output                      {MOD}P::-PRINT-'
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
            webbrowser.open('https://ubc-library-rc.github.io/damage')

        #Copypasta
        if event.endswith(':-COPY-'):
            #sg.clipboard_get()
            try:
                sg.clipboard_set(window['-OUTPUT-'].Widget.selection_get())
            except sg.tkinter.TclError:
                pass
            #sg.Print('COPY!!!', c='white on blue')
            #sg.Print(sg.clipboard_get())
        if event.endswith(':-PASTE-'):#Menu only because pastes by default
            try:
                #sg.Print('PASTE!!!', c='white on orange')
                window['-OUTPUT-'].Widget.insert(sg.tk.INSERT,
                                                    sg.clipboard_get())
            except sg.tkinter.TclError:
                pass

    window.close()

ICON =  b'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'
sg.DEFAULT_WINDOW_ICON = ICON
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

