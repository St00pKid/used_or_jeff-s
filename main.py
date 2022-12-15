import json
import os
import shutil
import time
from distutils import dir_util

import pyairtable
from dotenv import load_dotenv
from osxmetadata import *

import create_folder_list as cfl

# This is a workaround to needing an API key saved to your OS config. 
# If the API key is saved to the OS enviroment this code is no longer needed.
# There is a .env file in the directory with this file, this command sets that file as the development enviroment.
# The API key is stored there. 
load_dotenv()
api_key = os.environ["AIRTABLE_API_KEY"]

# These numbers are the unique IDs for the bases on airtable and will need to be updated each month. 
# Or ideally a new table is created on the same base so only one number will need to be changed.
# The new numbers can be found on the airtable API. The API updates based on your changes to the base or tables, it's very intuitive.
table = pyairtable.Table(api_key, 'appzG2a8ZqQgffECD', 'tblUjl5O7XITtaORx')

def sorter(sort_me, tobeposted, used):
    """Sorts folders in first argument to second argument or third argument based on if they are in the used_records.json. 
    used_records.json needs to be in the same folder as this file. Arguments for paths are used make it easier to change where the script is pointing.
    
    All u‚sed items in inventory are in used_records.json. Sorter looks to see if the items has an assigned ebay_id or if it has a ebay status of shipped. 
    If True the folder with photos is moved to whatever folder is assigned to the used argument. If False the are moved to the tobeposted argument.
    After folders are moved the individual image files in the used item folders are moved from their folders to the used directory and the original folders
    are deleted."""
    HEADER_FM = ['ItemID', 'ebay_id', 'instock_qty', 'warehouse_qty', 'ebay_team_qty', 'newitemreceiveddate', 
             'last_upload_date', 'ebay_status', 'last_markedforebay']
    HEADER_MODULE = ['eBayModuleID', 'ItemID', 'Condition', 'PhotographedBy', 'PhotographedAt', 'DateMarkedForEbay', 'WholesaleCost']
    
    cfl.create_json('Untitled.csv', 'Untitled.csv', HEADER_FM, 'used_records.json')
    cfl.create_json('eBay Module - Photography - All Records.csv', 'eBay Module - Photography - All Records.csv', HEADER_MODULE, 'module_records.json')
    
    folder_list = list()
    used_dir = list()
    module_list = list()
    
    with open('module_records.json', 'r') as x:
        module_dict = json.load(x)
    with open('used_records.json', 'r') as x:
        used_dict = json.load(x)

    # Sort the folders from source dir to either used or tobeposted locations.
    # Original folders are deleted from sort_me after they're moved.
    cfl.create_folder_list(sort_me, folder_list)
    for itemID in folder_list:
        
        if itemID in module_dict:
            module_list.append(itemID)
            
        if itemID not in module_dict and itemID not in used_dict:
            if ' ' in itemID:
                itemID_split = itemID.split(' ')
                itemID_split = itemID_split[0] # Try removing additional strs from folder name, eg; prop or trade.
                if itemID_split not in module_dict and itemID_split not in used_dict:
                    print(f"{itemID} not used or in the module.")   
            
        if itemID not in used_dict:
            dir_util.copy_tree(f"{sort_me}/{itemID}",
                                    f"{tobeposted}/{itemID}")

        elif used_dict[f'{itemID}']['ebay_id'] == '' or used_dict[f'{itemID}']['ebay_status'] == "Shipped":
            dir_util.copy_tree(f"{sort_me}/{itemID}",
                                    f"{used}/{itemID}")
            
        else:
            dir_util.copy_tree(f"{sort_me}/{itemID}",
                                    f"{tobeposted}/{itemID}")

        try:
            shutil.rmtree(f'{sort_me}/{itemID}/')
        except Exception:
            continue

    # After the folders are sorted the individual photo files for used items are pulled from itemID folders and placed into used
    # Then empty folder is deleted. 
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
            table.create(at_dict)
            
        except Exception:
            continue
          
    # Add " Trade" to folders for trade-in itemIDs. 
    for itemID in module_list:
        itemID = itemID.split(' ').pop()
        if module_dict[f'{itemID}']['Condition'] == 'T':
            try:
                dir_util.copy_tree(f"{tobeposted}/{itemID}",
                                    f"{tobeposted}/{itemID} Trade")
                md = OSXMetaData(f"{tobeposted}/{itemID} Trade")
                md.tags = [Tag("eBay", FINDER_COLOR_RED)]
                shutil.rmtree(f'{tobeposted}/{itemID}')
            except Exception:
                print(f'Error: add "Trade" loop - {itemID}')
        else:
            try:
                md = OSXMetaData(f"{tobeposted}/{itemID}")
                md.tags = [Tag("eBay", FINDER_COLOR_RED)]
            except Exception:
                print(f'Error: adding finder tag - {itemID}') 
                continue
            
        
        
###########################
start = time.perf_counter()

sorter('/Volumes/ebay/ToBeEdited/tobesorted', '/Volumes/ebay/testtobeposted', '/Volumes/ImageEngine/testusedinbox')

finish = time.perf_counter()
############################

print(f"completed in {finish - start:0.4f} seconds")


# TODO: working GUI to make this runable by others.
#       Buttons to run the sorters, an exceptions field to skip certain items if they're kicking errors.
