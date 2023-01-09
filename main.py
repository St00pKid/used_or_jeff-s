import glob
import json
import os
import shutil
import time
from distutils import dir_util

import pyairtable
import PySimpleGUIWx as sg
from dotenv import load_dotenv
from osxmetadata import *

import create_folder_list as cfl

# Gui variables
sg.theme('SystemDefault1')

gui_font = ('arial', 16, 'white')

layout = [
    [sg.Text(
        "Directory where files to be sorted currently reside.", 
        font=gui_font)],
    [sg.Input(
        default_text='/Volumes/ebay/ToBeEdited/tobesorted', 
        key='guiToBeSorted',
        font=gui_font),
     sg.FolderBrowse(
        initial_folder='/Volumes/ebay/ToBeEdited/tobesorted', 
        font=gui_font)],
    [sg.Text(
        "Directory where used items will go. Most likely in imageengine.", 
        font=gui_font)],
    [sg.Input(
        default_text='/Volumes/ImageEngine/testusedinbox', 
        key='guiToBeUsed', 
        font=gui_font),
     sg.FolderBrowse(
        initial_folder='/Volumes/ImageEngine/testusedinbox', 
        font=gui_font)],
    [sg.Text(
        "Directory where non-used (anything for Jeff's Music Gear) will go.", 
        font=gui_font)],
    [sg.Input(
        default_text='/Volumes/ebay/testtobeposted', 
        key='guiToBePosted', 
        font=gui_font),
        sg.FolderBrowse(
        initial_folder='/Volumes/ebay/testtobeposted', 
        font=gui_font)],
    [sg.Button(
        'Submit', 
        auto_size_button=True, 
        font=gui_font, 
        border_width=5),
     sg.Button(
        'Quit', 
        auto_size_button=True, 
        font=gui_font, 
        border_width=5)],
    [sg.Text(
        ' ', 
        key="-STATUS-", 
        font=gui_font)],
    [sg.Button(
        "RUN", 
        font=gui_font, 
        auto_size_button=True), 
     sg.Text
        ("Update the csv files before doing this!!")],
]

updated = False

window = sg.Window('Distressed Gear Team Tools', layout)

# This is a workaround to needing an API key saved to your OS config. 
# If the API key is saved to the OS environment this code is no longer needed.
# There is a .env file in the directory with this file, 
# this command sets that file as the development environment.
# The API key is stored there. 
load_dotenv()
api_key = os.environ["AIRTABLE_API_KEY"]

# These numbers are the unique IDs for the bases on airtable and
# will need to be updated each month. Or ideally a new
# table is created on the same base so only one number will need to be changed. 
# The new numbers can be found on the airtable API. 
# The API updates based on your changes to the base or tables, 
# it's very intuitive.
table = pyairtable.Table(api_key, 'app7wwyKDrOI3hgc6', 'tbl5Lha83X1UPjLEB')


def sorter(
    sort_me = '/Volumes/ebay/ToBeEdited/tobesorted', 
    tobeposted = '/Volumes/ebay/testtobeposted', 
    used = '/Volumes/ImageEngine/testusedinbox'
    ):
    """Sorts folders in first argument to second argument or 
    third argument based on if they are in the used_records.json."""
    
    start = time.perf_counter()

    HEADER_FM = ['ItemID', 
                 'ebay_id', 
                 'ebay_status', 
                 'marked_for_ebay', 
                 'instock-qty', 
                 'condition',
                 'last-photo-by'
                 ]
   
    cfl.create_json('Untitled.csv', 'Untitled.csv', HEADER_FM, 'used_records.json')
             
    backup_Dir = 'backup/*'
    folder_list = list()
    used_dir = list()
    module_list = list()
    photog = dict()
    folder_list = list()
    
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
        try:
            # Copy items with condition U(sed) to correct location.
            # All other conditions need to go to tobeposted.
            if used_dict[f'{itemID}']['condition'] == 'U': 
                if (used_dict[f'{itemID}']['ebay_id'] != "" and 
                        used_dict[f'{itemID}']['ebay_status'] != 'Shipped'):
                    dir_util.copy_tree(f"{sort_me}/{itemID}",
                                    f"{tobeposted}/{itemID}")
                    module_list.append(itemID)
                    shutil.move(f'{sort_me}/{itemID}/',
                                f'backup/{itemID}')
                    
                elif (used_dict[f'{itemID}']['ebay_status'] == '' or 
                        used_dict[f'{itemID}']['ebay_status'] == 'Shipped'):
                    dir_util.copy_tree(f"{sort_me}/{itemID}",
                                       f"{used}/{itemID}")
                    photog['Photographer'] = used_dict[f'{itemID}']['last-photo-by']
                    shutil.move(f'{sort_me}/{itemID}/', 
                                f'backup/{itemID}')
            else:
               raise KeyError
        # Error is raised if the itemID is not in our assigned workload.
        # These items are to be sent to the tobeposted folder.
        except KeyError:
            module_list.append(itemID)
            dir_util.copy_tree(f"{sort_me}/{itemID}",
                               f"{tobeposted}/{itemID}")
            shutil.move(f'{sort_me}/{itemID}/', 
                        f'backup/{itemID}')
        
    # After the folders are sorted the individual photo files 
    # for used items are pulled from itemID folders and
    # placed into the used dir. Then empty folder is deleted.
    cfl.create_folder_list(used, used_dir)
    at_dict = dict()

    for itemID in used_dir:
        sub_folder = list()
        try:
            cfl.create_folder_list(f'{used}/{itemID}', sub_folder)

            for photo in sub_folder:
                shutil.copy(f'{used}/{itemID}/{photo}', 
                            f'{used}')
            shutil.rmtree(f'{used}/{itemID}')

            # Writes new used records to Airtable.
            # Keys are the unique IDs Airtable uses for that column, 
            # it will need to be updated for each month.
            at_dict['fldH5f1pGVdCjJGyr'] = itemID
            at_dict.update({'fld3CtQJDviDuMpnX': 
                                used_dict[f'{itemID}']['last-photo-by']})
            table.create(at_dict)
        except Exception:
            print(f'{itemID}: Error pulling individual files.')

    # Add " Trade" to folders for trade-in itemIDs. 
    for itemID in module_list:
        itemID = itemID.split(' ')
        itemID = itemID[0]
        try:
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
                    continue
        except KeyError:
            print(f"KeyError: {itemID}")        
        
    
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
        if updated is True:
            sorter(toBeSorted, toBePosted, used)
        elif updated is False:
            sorter()

############################
