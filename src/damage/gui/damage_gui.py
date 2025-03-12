'''
Damage GUI application
'''
#import base64
import base64
import json
import os
import pathlib
import shlex
import shutil
import subprocess
import sys
import tempfile
import textwrap
import webbrowser
import FreeSimpleGUI as sg

import damage
#pylint: disable = possibly-used-before-assignment

#TODO put the application into a class or function
#Prettify the name
PROGNAME = pathlib.Path(__file__).stem.capitalize().replace('_gui','')
__version__ = '.'.join([str(x) for x in damage.VERSION])

BASEDIR = pathlib.Path(__file__).parent

with open(pathlib.Path(BASEDIR, 'assets', 'DamageAppIcon.png'),
          'rb') as f:
    ICON = base64.b64encode(f.read())

with open(pathlib.Path(BASEDIR, 'assets', 'LICENCE.txt'),
          mode='r', encoding='utf-8') as lic:
    LICENCE = textwrap.fill(lic.read(), width=70,
                            replace_whitespace=False)

sg.DEFAULT_WINDOW_ICON = ICON

if sg.running_mac():
    import plistlib
    TTK_THEME = 'aqua'
    # make FONTSIZE dependent on homebrew in path because only brew python
    # compiles successfully on MacOS on a case-insensitive file system
    # and for some inconceivable reason the font size changes
    FONTSIZE = 14
    for hack in ['homebrew', 'MacOS']:
        if hack in {y for x in sys.path for y in pathlib.Path(x).parts}:
            FONTSIZE = 10
    BASEFONT = 'System'
    MOD = '\u2318' #CMD key unicode 2318 Place of Interest
    CMDCTRL = 'Command' #tkinter bind string sans <>

if sg.running_windows():
    TTK_THEME =  'vista'
    FONTSIZE = 9
    BASEFONT = 'Arial' #GRR #TODO no longer basefont on Windows
    MOD = 'Ctrl-'
    CMDCTRL = 'Control'

if sg.running_linux():
    TTK_THEME =  'alt'
    FONTSIZE = 9
    BASEFONT = 'TkDefaultFont' #GRR
    MOD = 'Ctrl-'
    CMDCTRL = 'Control'
sg.set_options(font=f'{BASEFONT} {FONTSIZE}')

sg.theme('systemDefaultForReal')

# I dislike having this as a global variable
# TODO find a better way to store PREFDICT
PREFDICT = None

def debug_mode():
    '''
    Turn on debugger from the command line
    '''
    yes_to_debug = ['debug', 'd', '1']
    if len(sys.argv) > 1:
        debug = sys.argv[1]
        if debug.lower() in yes_to_debug:
            sg.show_debugger_window(location=(10,10))

def is_csv(indict:dict)->bool:
    '''
    Convenience function to see if output is csv

    '''
    #I really need to redo the whole works from scratch
    if indict.get('out') == 'csv':
        return True
    return False

def pref_path()->pathlib.Path:
    '''
    Returns path to preferences directory and preferences
    file name as a tuple
    '''
    if sg.running_mac():
        return pathlib.Path(pathlib.Path('~/Library/Preferences').expanduser(),
                'ca.ubc.library.damage.prefs.plist')
    if sg.running_windows():
        return pathlib.Path(pathlib.Path('~/AppData/Local/damage').expanduser(), 'damage.json')
    #Linux and everything else
    return pathlib.Path(pathlib.Path('~/.config/damage').expanduser(),
                'damage.json')

def get_prefs()->None:
    '''
    Gets preferences from JSON or default dict. If no preferences
    file is found, one is written
    '''
    global PREFDICT
    try:
        if sg.running_mac():
            with open(pref_path(), 'rb') as fn:
                PREFDICT = plistlib.load(fn)
        if sg.running_linux() or sg.running_windows():
            with open(pref_path(), encoding='utf-8') as fn:
                PREFDICT = sg.json.load(fn)


    except FileNotFoundError:
        PREFDICT = { 'flatfile' :False,
                      'recurse' :False,
                      'digest' :'md5',
                      'out' :'txt',
                      'short' :True,
                      'headers' :True,
                      'nonascii' :True,
                      'hidden' : False}

    fixflat = PREFDICT.get('flat')
    if fixflat:
        PREFDICT['flatfile'] = fixflat
        del PREFDICT['flat']
    # Add new keys here when expanding prefs
    PREFDICT['hidden'] = PREFDICT.get('hidden', False)

def set_prefs()->None:
    '''
    Sets preferences
    '''
    if not pref_path().parent.exists():
        os.makedirs(pref_path().parent)
    if sg.running_mac():
        with open(pref_path(), 'wb') as fn:
            plistlib.dump(PREFDICT, fn)
    if sg.running_linux() or sg.running_windows():
        with open(pref_path(), 'w', encoding='utf-8') as fn:
            sg.json.dump(PREFDICT, fn)

def damager(flist, **kwargs)->str:
    '''
    Text output from Damage utility
    '''
    output = []
    for num, fil in enumerate(flist):
        if not pathlib.Path(fil).is_file() or not pathlib.Path(fil).exists():
            continue
        testme = damage.Checker(fil)
        if kwargs['out'] == 'csv' and num == 0:
            kwargs['headers'] = True
            output.append(testme.manifest(**kwargs))
        else:
            kwargs['headers'] = False
            output.append(testme.manifest(**kwargs))
    if kwargs['out'] =='txt':
        return '\n\n'.join(output)
    if kwargs['out'] == 'csv':
        return ''.join(output)#Horrible hack; excel dialiect automatically adds \r\n
    outjson = ('{"files" :' +
               '[' + ','.join(output) + ']'
               + '}')
    outjson = json.dumps(json.loads(outjson)) #validate
    return outjson

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
    #HACKME
    if not hidden:
        hidden = PREFDICT.get('hidden', False)
    if not direc:#Possible if window call cancelled, as I have discovered
        #return None
        return []
    walker = pathlib.Path(direc).walk()
    if not recursive:
        walker = [next(walker)]
    else:
        walker = list(walker)
    flist=[]
    #Hidden is a property in the Checker object, but this comes before instantiation
    if hidden:
        #flist = [[x[0], pathlib.Path(x[0], y).name] for x in walker for y in x[2]
        #         if pathlib.Path(x[0],y).is_file()]
        flist = [pathlib.Path(x[0], y) for x in walker for y in x[2]
                 if pathlib.Path(x[0],y).is_file()]

    else:
        #hidden defined as any part of the path starts with '.'
        flist = [pathlib.Path(x[0],y) for x in walker for y in x[2]
                if not any(z.startswith('.') for z in
                            pathlib.Path(x[0], y).parts)]
    return flist

def send_to_file(outstring)->None:
    '''
    Sends string output to file

    Creates a tk.asksaveasfile dialogue and saves
    '''
    #Because TK is just easier
    outfile = sg.tk.filedialog.asksaveasfile(title='Save Output',
                                       initialfile=f'output.{PREFDICT["out"]}',
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
    #outfile = tempfile.NamedTemporaryFile(mode='w', encoding='utf-8',
    #                                      suffix='.txt', delete=False)
    #outfile.write(outstring)
    #outfile.close()
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8',
                                     suffix='.txt', delete=False) as outfile:
        outfile.write(outstring)

    if sg.running_mac() or sg.running_linux():
        #lpr =  subprocess.Popen(shutil.which('lpr'), stdin=subprocess.PIPE)
        #lpr.stdin.write(bytes(outstring, 'utf-8'))
        subprocess.run([shutil.which('lpr'), outfile.name], check=False)

    if sg.running_windows():

        #List of all printers names and shows default one
        #wmic printer get name,default
        #https://stackoverflow.com/questions/13311201/get-default-printer-name-from-command-line
        subout = subprocess.run(shlex.split('wmic printer get name,default'),
                                capture_output=True,
                                check=False)
        #the following only makes sense of you look at the output of the
        #windows shell command above. stout is binary, hence decode.
        printerinfo = [[x[:6].strip(), x[6:].strip()] for x in
                        subout.stdout.decode().split('\n')[1:]]
        default_printer = [x for x in printerinfo if x[0] == 'TRUE'][0][1]
        subprocess.run(['print', f'/D:{default_printer}', outfile.name], check=False)
        #tempfile must be removed manually because of delete=False above
    os.remove(outfile.name)
    sg.popup('Output sent to default printer', title='Job Completed', any_key_closes=True)

def about_window()->sg.Window:
    '''
    Creates the "About" window
    '''
    about = { 'developers' : ['Paul Lesack'],
             'user_testers' : ['Alex Alisauskas','Jeremy Buhler', 'Cheryl Niamath'],
             'source_url' : 'https://github.com/ubc-library-rc/damage',
             'documentation' : 'https://ubc-library-rc.github.io/damage'
             }
    #displayname = f'{PROGNAME[:PROGNAME.find("_")].capitalize()} v{__version__}'
    displayname = f'{PROGNAME} v{__version__}'
    name = [[sg.Text(displayname, font=f'{BASEFONT} {FONTSIZE+4} bold')]]
    source =[[sg.Text('Source code', font=f'{BASEFONT} {FONTSIZE+2} bold')],
              [sg.Text(about['source_url'], enable_events=True, text_color='blue', k='-SC-')]]
    documentation =[[sg.Text('Documentation', font=f'{BASEFONT} {FONTSIZE+2} bold')],
                     [sg.Text(about['source_url'], enable_events=True,
                              text_color='blue', k='-DOC-')]]
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
        #event, values = window.read()
        # don't need values
        event = window.read()[0]
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
    Values from window  saved to the preferences dictionary PREFDICT
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
                           default=PREFDICT['short'], )],
             [sg.Checkbox(text=rectang,
                           key= '-FLATFILE-',
                           default=PREFDICT['flatfile'], )],
             [sg.Checkbox('Recursively add files from directories',
                           key='-RECURSE-', default=PREFDICT['recurse'])],
             [sg.Checkbox('Include hidden files',
                           key='-HIDDEN-', default=PREFDICT['hidden'])],
             [sg.Text('Hash type'),
              sg.Combo(values=hashes, default_value=PREFDICT['digest'],
                       key='-DIGEST-', readonly=True)],
             [sg.Text('Output format'),
              sg.Combo(values=outputs, default_value=PREFDICT['out'],
                       key='-OUT-', readonly=True)],
             [sg.Ok(bind_return_key=True, button_text='OK')]]
    pwindow = sg.Window(title='Preferences',
                    icon=ICON,
                     resizable=True,
                     layout=layout,
                     ttk_theme=TTK_THEME,
                     use_ttk_buttons=True,
                     keep_on_top=True,
                     modal=True, finalize=True)
    pwindow.bind('<Escape>', 'Exit')
    pevent, pvalues = pwindow.read()
    if pevent:
        for key in ['short', 'flatfile', 'recurse', 'digest', 'out', 'hidden']:
            PREFDICT[key] = pvalues[f'-{key.upper()}-']
    set_prefs()
    if pevent == 'Exit':
        pwindow.close()
    pwindow.close()

def window_binds(window:sg.Window)->None:
    '''
    Bind keys to main window
    '''
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
    debug_mode()
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
                             initial_folder=pathlib.Path('~').expanduser()),
             sg.Button(button_text='Remove Files',
                       enable_events=True, key='-DELETE-')]]

    #Right side (output) section
    #This is more complicated than it should be because psg doesn't
    #flip correctly between Multiline and Table elements and doesn't hide
    #the Table scrollbars, and resizing is also affected. The (a) solution
    #is to put each of them in a Frame.
    #But the best solution would be to use straight tkinter but it's too
    #late for that, isn't it.

    outbox = sg.Multiline(key='-OUTPUT-',
                           size=10000, #Auto-expansion has a bug
                           expand_x=True,
                           expand_y=True,
                           visible=True,
                           auto_refresh=True)
    frame_1=sg.Frame(title ='',
                     layout=[[outbox]],
                     expand_x=True,
                     expand_y=True,
                     border_width=0,
                     key='F1',
                     visible=not is_csv(PREFDICT))

    #CSV/tabular output box
    #hardcoding the headers seems dumb,
    #but the headers have to be read *after* instantiation of a Checker object
    #TODONE used these ones for now, not really happy about it
    headers = ['filename', 'digestType', 'digest',
                'min_cols', 'max_cols', 'numrec',
                'constant', 'encoding', 'nonascii',
                'null_chars', 'mimetype', 'dos']

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
                #visible=is_csv(PREFDICT),
                visible=True,
                enable_events=True
                )
    frame_2=sg.Frame(title ='',
                     layout=[[csvout]],
                     expand_x=True,
                     expand_y=True,
                     border_width=0,
                     key='F2',
                     visible=True)


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

    window = sg.Window(title='Damage', layout=layout, resizable=True,
                      size = PREFDICT.get('main_size', (None, None)),
                      icon=ICON,
                      ttk_theme=TTK_THEME,
                      use_ttk_buttons=True,
                      location= PREFDICT.get('main_location', (None, None)),
                      finalize=True, enable_close_attempted_event=True)
    lbox.Widget.config(borderwidth=0)
    window.set_min_size((875,400))
    window_binds(window)
    return window

def main()->None:
    '''
    Main loop
    '''
    get_prefs()
    window  = main_window()
    #FFFFUUUUU
    menulayout = window['-MENUBAR-'].MenuDefinition
    #sg.easy_print(menulayout)
    #Why don't I just do it all in TK? Jesus
    #talk about undocumented.
    #also: https://tkdocs.com/tutorial/menus.html
    #window.TKroot.tk.createcommand('tk::mac::ShowPreferences', prefs_window )
    # How to get root? What is the function where None is?
    #root = window.hidden_master_root #(see PySimpleGUI.py.StartupTK, line 16008)
    #sg.easy_print(type(poot))
    #root.createcommand('tk::mac::ShowPreferences', prefs_window )
    #root.createcommand('tk::mac::ShowPreferences', lambda:  None)
    #Also, why does the window stop responding after calling the prefs? But only half? It's
    #a fucking mystery. And it doesn't happen with straight TK so it's something to with psg.
    #root.createcommand('tk::mac::standardAboutPanel', about_window)
    while True:
        event, values = window.read()

        if event in (sg.WINDOW_CLOSE_ATTEMPTED_EVENT,):
            PREFDICT['main_size'] = window.size
            PREFDICT['main_location'] = window.current_location()
            set_prefs()
            break

        if event in (sg.WINDOW_CLOSED,):
            break

        if event == '-IN-':
            #sg.easy_print(f"Values=| {values['-IN-']} |", c='white on red')
            upd_list = (window['-SELECT-'].get_list_values() +
                        [x for x in values['-IN-'].split(';') if
                         x not in window['-SELECT-'].get_list_values()])
            if PREFDICT.get('hidden', False):
                upd_list = [x for x in upd_list if pathlib.Path(x).is_file()]
            else:
                upd_list = [x for x in upd_list if pathlib.Path(x).is_file()
                            and not any(z.startswith('.')
                            for z in pathlib.Path(x).parts)]
            window['-SELECT-'].update(upd_list)
            window['-IN-'].update(value='')

        if event in ('-IFOLD-', 'Add Folder'):
            if event in ('Add Folder',):
                #Not implementing same behaviour in button
                #requires rewriting menu
                #TODO find a way to have the menu item
                #and button have the behaviour below
                #probably by having the button replaced by a function call.
                initiald = pathlib.Path('~').expanduser()
                newfiles = get_folder_files(sg.popup_get_folder('',
                                                                no_window=True,
                                                                initial_folder=initiald),
                                             PREFDICT['recurse'])
            else:
                newfiles = get_folder_files(values['-IFOLD-'], PREFDICT['recurse'])
            upd_list = window['-SELECT-'].get_list_values()
            #sg.easy_print('Used Add Folder Button')
            upd_list = upd_list+ [x for x in newfiles if x not in upd_list]
            window['-SELECT-'].update(upd_list)

        if event.endswith('-DELETE-'):
            nlist = [x for x in window['-SELECT-'].get_list_values() if
                    x not in values['-SELECT-']]
            window['-SELECT-'].update(nlist)

        if event.endswith('-MANIFEST-'):
            #sg.easy_print(event, values)
            delme = ''
            #Only clear manifest
            window['-OUTPUT-'].update(delme)#clear first
            window['-CSV-'].update(delme)#clear first
            try:
                upd_list = window['-SELECT-'].get_list_values()
                if upd_list == ['']: #why
                    upd_list = []
                if upd_list:
                    txt = damager(upd_list, **PREFDICT)
                    if PREFDICT['short'] and len(upd_list) > 1:
                        #commonpath does not include last sep, very annoying
                        delme = os.path.commonpath(upd_list) + os.sep
                        window['-OUTPUT-'].update(txt.replace(delme,''))
                    elif PREFDICT['short'] and len(upd_list) == 1:
                        #delme = os.path.split(upd_list[0])[0] + os.sep
                        delme = pathlib.Path(upd_list[0]).parts[0] + os.sep #consistency
                    txt = txt.replace(delme,'')
                    window['-OUTPUT-'].update(txt)

                if PREFDICT.get('out') == 'csv':
                    txt = txt.split('\n')
                    #reader=csv.reader(txt[1::2], delimiter=',')#Strip out the headers
                    #window['-CSV-'].update(values=list(reader))
                    #nout = [txt[0]] + txt[1::2]#combine header with data
                    ##and send to output window for printing/saving
                    #window['-OUTPUT-'].update('\n'.join(nout))

                    #new
                    #This is like it is because window['-CSV-'] takes lists
                    #as values and window['-OUTPUT-] is text output
                    #and csv.Reader adds windows \r\n.
                    nout = [x.strip().split(',') for x in txt[1:]]
                    nout = [x for x in nout if x !=['']]
                    window['-CSV-'].update(nout)
                    nout = [txt[0].strip()]+[','.join(z) for z in nout]
                    nout = '\n'.join(nout)
                    window['-OUTPUT-'].update(nout)



            except (ValueError, NameError, AttributeError):
                window['-OUTPUT-'].update(delme)

        if event == 'Preferences':
            #sg.easy_print(values)
            prefs_window()
            #Show correct window pane for output.
            xpandr = is_csv(PREFDICT)
            window['F1'].update(visible=not xpandr)
            window['F2'].update(visible=xpandr)
            window['F1'].expand(expand_x=not xpandr, expand_y=not xpandr)
            window['F2'].expand(expand_x=xpandr, expand_y=xpandr)
            window['-OUTPUT-'].update('')
            #sg.easy_print(PREFDICT)
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
            newfiles = sg.popup_get_file(message='', no_window=True,
                                         multiple_files=True,
                                         file_types = sg.FILE_TYPES_ALL_FILES)

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
            #Oh look more straight Tkinter.
            try:
                sg.clipboard_set(window['-OUTPUT-'].Widget.selection_get())
            except sg.tkinter.TclError:
                pass
            #sg.easy_print('COPY!!!', c='white on blue')
            #sg.easy_print(sg.clipboard_get())
        if event.endswith(':-PASTE-'):#Menu only because pastes by default
            try:
                #sg.easy_print('PASTE!!!', c='white on orange')
                window['-OUTPUT-'].Widget.insert(sg.tk.INSERT,
                                                    sg.clipboard_get())
            except sg.tkinter.TclError:
                pass

    window.close()

if __name__ == '__main__':
    main()
