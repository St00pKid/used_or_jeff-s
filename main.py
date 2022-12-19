import json
import os, glob
import shutil
import time
from distutils import dir_util

import pyairtable
from dotenv import load_dotenv
from osxmetadata import *
import PySimpleGUIWx as sg

import create_folder_list as cfl

# Gui variables
sg.theme('SystemDefault1')

gui_font = ('arial', 16, 'white')

layout = [
    [sg.Text("Directory where files to be sorted currently reside. Most likely tobesorted in tobeedited", font=gui_font)],
    [sg.Input(default_text='/Volumes/ebay/ToBeEdited/tobesorted', key='guiToBeSorted', font=gui_font),
     sg.FolderBrowse(initial_folder='/Volumes/ebay/ToBeEdited/tobesorted', font=gui_font)],
    [sg.Text("Directory where used items will go. Most likely in imageengine.", font=gui_font)],
    [sg.Input(default_text='/Volumes/ImageEngine/testusedinbox', key='guiToBeUsed', font=gui_font),
     sg.FolderBrowse(initial_folder='/Volumes/ImageEngine/testusedinbox', font=gui_font)],
    [sg.Text("Directory where non-used (anything for Jeff's Music Gear) will go. Most likely tobeposted", font=gui_font)],
    [sg.Input(default_text='/Volumes/ebay/testtobeposted', key='guiToBePosted', font=gui_font),
     sg.FolderBrowse(initial_folder='/Volumes/ebay/testtobeposted', font=gui_font)],
    [sg.Button('Submit', auto_size_button=True, font=gui_font, border_width=5),
     sg.Button('Quit', auto_size_button=True, font=gui_font, border_width=5)],
    [sg.Text(' ', key="-STATUS-", font=gui_font)],
    [sg.Button("RUN", font=gui_font, auto_size_button=True), sg.Text("Update the csv files before doing this!!")],
]

updated = False

window = sg.Window('Distressed Gear Team Tools', layout)

# This is a workaround to needing an API key saved to your OS config. 
# If the API key is saved to the OS environment this code is no longer needed.
# There is a .env file in the directory with this file, this command sets that file as the development environment.
# The API key is stored there. 
load_dotenv()
api_key = os.environ["AIRTABLE_API_KEY"]

# These numbers are the unique IDs for the bases on airtable and will need to be updated each month. Or ideally a new
# table is created on the same base so only one number will need to be changed. The new numbers can be found on the
# airtable API. The API updates based on your changes to the base or tables, it's very intuitive.
table = pyairtable.Table(api_key, 'appzG2a8ZqQgffECD', 'tblUjl5O7XITtaORx')


def sorter(sort_me = '/Volumes/ebay/ToBeEdited/tobesorted', tobeposted = '/Volumes/ebay/testtobeposted', used = '/Volumes/ImageEngine/testusedinbox'):
    """Sorts folders in first argument to second argument or third argument based on if they are in the
    used_records.json. used_records.json needs to be in the same folder as this file. Arguments for paths are used
    make it easier to change where the script is pointing.
    
    All used items in inventory are in used_records.json. Sorter looks to see if the items has an assigned ebay_id or
    if it has an ebay status of Shipped. If True the folder with photos is moved to whatever folder is assigned to the
    used argument. If False they are moved to the tobeposted argument. After folders are moved the individual image
    files in the used item folders are moved from their folders to the used directory and the original folders are
    deleted. """
    start = time.perf_counter()

    HEADER_FM = ['ItemID', 'ebay_id', 'ebay_status', 'marked_for_ebay', 'instock-qty', 'condition',
                 'last-photo-by']
   
    cfl.create_json('Untitled.csv', 'Untitled.csv', HEADER_FM, 'used_records.json')
             
    backup_Dir = 'backup/*'
    folder_list = list()
    used_dir = list()
    module_list = list()
    photog = dict()

    # clean the backup folder
    d = glob.glob(backup_Dir)
    for i in d:
        shutil.rmtree(i)
        
    with open('used_records.json', 'r') as x:
        used_dict = json.load(x)

    # Sort the folders from source dir to either used or tobeposted locations.
    # Original folders are deleted from sort_me after they're moved.
    cfl.create_folder_list(sort_me, folder_list)
    
    for itemID in folder_list:

        if itemID not in used_dict:
            if ' ' in itemID:
                itemID_split = itemID.split(' ')
                itemID_split = itemID_split[0]  # Try removing additional strs from folder name, eg; prop or trade.
                if itemID_split not in used_dict:
                    dir_util.copy_tree(f"{sort_me}/{itemID}",
                            f"{tobeposted}/{itemID}")
                    shutil.move(f'{sort_me}/{itemID}/', f'backup/{itemID}')                   
                    
        elif itemID in used_dict:
            if used_dict[f'{itemID}']['ebay_id'] != "" and used_dict[f'{itemID}']['ebay_status'] != 'Shipped':
                dir_util.copy_tree(f"{sort_me}/{itemID}",
                                f"{tobeposted}/{itemID}")
                module_list.append(itemID)
                shutil.move(f'{sort_me}/{itemID}/', f'backup/{itemID}')
                
            elif used_dict[f'{itemID}']['condition'] == 'U':
                if used_dict[f'{itemID}']['ebay_status'] == '' or used_dict[f'{itemID}']['ebay_status'] == 'Shipped':
                    dir_util.copy_tree(f"{sort_me}/{itemID}",
                                    f"{used}/{itemID}")
                    photog['Photographer'] = used_dict[f'{itemID}']['last-photo-by']
                    shutil.move(f'{sort_me}/{itemID}/', f'backup/{itemID}')
                                        
        else:
            dir_util.copy_tree(f"{sort_me}/{itemID}",
                               f"{tobeposted}/{itemID}")
            shutil.move(f'{sort_me}/{itemID}/', f'backup/{itemID}')
        
    # After the folders are sorted the individual photo files for used items are pulled from itemID folders and
    # placed into used. Then empty folder is deleted.
    cfl.create_folder_list(used, used_dir)
    at_dict = dict()

    for itemID in used_dir:
        sub_folder = list()
        try:
            cfl.create_folder_list(f'{used}/{itemID}', sub_folder)

            for photo in sub_folder:
                shutil.copy(f'{used}/{itemID}/{photo}', f'{used}')
            shutil.rmtree(f'{used}/{itemID}')

            # Writes new used records to Airtable.
            # This string is the unique ID airtable uses for that column, it will need to be updated for each month.
            at_dict['fldhMuDWW6xC763vG'] = itemID
            at_dict.update({'fldvCCUR9V8KpNFrM': used_dict[f'{itemID}']['last-photo-by']})
            table.create(at_dict)
        except Exception:
            print(f'{itemID}: Error in used inbox while shuffling files and sending to Airtable.')

    # Add " Trade" to folders for trade-in itemIDs. 
    for itemID in module_list:
        itemID = itemID.split(' ').pop()
        if used_dict[f'{itemID}']['condition'] == 'T':
            try:
                os.rename(f"{tobeposted}/{itemID}",
                                   f"{tobeposted}/{itemID} Trade")
                md = OSXMetaData(f"{tobeposted}/{itemID} Trade")
                md.tags = [Tag("eBay", FINDER_COLOR_RED)]
            except Exception:
                print(f'{itemID} : Unable to add trade to folder name')
                
        else:
            try:
                md = OSXMetaData(f"{tobeposted}/{itemID}")
                md.tags = [Tag("eBay", FINDER_COLOR_RED)]
            except Exception:
                print(f'Error: adding finder tag - {itemID}')
                continue
    
    finish = time.perf_counter()
    print(f"completed in {finish - start:0.4f} seconds")


###########################

while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED or event == 'Quit':
        break

    if event == 'Submit':
        toBeSorted = values['guiToBeSorted']
        used = values['guiToBeUsed']
        toBePosted = values['guiToBePosted']
        window["-STATUS-"].update("Locations updated")
        updated = True

    if event == 'RUN':
        if updated == True:
            sorter(toBeSorted, toBePosted, used)
        elif updated == False:
            sorter()

############################
