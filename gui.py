import PySimpleGUIWx as sg

toBeSorted = '/Volumes/ebay/ToBeEdited/tobesorted'
used = '/Volumes/ImageEngine/testusedinbox'
toBePosted = '/Volumes/ebay/testtobeposted'
# font = ('arial', 13, 'white')

sg.theme('SystemDefault1')

layout = [
    [sg.Text("Directory where files to be sorted currently reside. Most likely tobesorted in tobeedited")],
    [sg.Input(default_text = '/Volumes/ebay/ToBeEdited/tobesorted', key = 'guiToBeSorted'), sg.FolderBrowse(initial_folder = '/Volumes/ebay/ToBeEdited/tobesorted', font=('arial', 16))],
    [sg.Text("Directory where used items will go. Most likely in imageengine.")],
    [sg.Input(default_text = '/Volumes/ImageEngine/testusedinbox', key = 'guiToBeUsed'), sg.FolderBrowse(initial_folder = '/Volumes/ImageEngine/testusedinbox', font=('arial', 16))],
    [sg.Text("Directory where non-used (anything for Jeff's Music Gear) will go. Most likely tobeposted")],
    [sg.Input(default_text = '/Volumes/ebay/testtobeposted', key = 'guiToBePosted'), sg.FolderBrowse(initial_folder = '/Volumes/ebay/testtobeposted', font=('arial', 16))],       
    [sg.Button('Submit', auto_size_button=True, font=('arial', 16)), sg.Button('Quit', auto_size_button=True, font=('arial', 16))],
    [sg.Button("RUN Used or Jeff's Script",font=('arial', 16),auto_size_button=True),sg.Text("Update the csv files before doing this!!")]
    ]

window = sg.Window('Distressed Gear Team Tools', layout)

while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == 'Quit':
            break
        
        if event =='Submit':
            toBeSorted = values['guiToBeSorted']
            used = values['guiToBeUsed']
            toBePosted = values['guiToBePosted']
            