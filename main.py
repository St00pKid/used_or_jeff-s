import json
import create_folder_list as cfl
from distutils import dir_util
import shutil
import time
from osxmetadata import *
import os
import pyairtable
from dotenv import load_dotenv
load_dotenv()

api_key = os.environ["AIRTABLE_API_KEY"]
table = pyairtable.Table(api_key, 'appzG2a8ZqQgffECD', 'tblUjl5O7XITtaORx')

def sorter(sort_me, tobeposted, used):
    """Sorts folders in first argument to second argument or third argument based on if they are in the used_records.json. 
    used_records.json needs to be in the same folder as this file. Arguments for paths are used make it easier to change where the script is pointing.
    
    All used items in inventory are in used_records.json. Sorter looks to see if the items has an assigned ebay_id or if it has a ebay status of shipped. 
    If True the folder with photos is moved to whatever folder is assigned to the used argument. If False the are moved to the tobeposted argument.
    After folders are moved the individual image files in the used item folders are moved from their folders to the used directory and the original folders
    are deleted."""
    HEADER_FM = ['ItemID', 'ebay_id', 'instock_qty', 'warehouse_qty', 'ebay_team_qty', 'newitemreceiveddate', 
             'last_upload_date', 'ebay_status', 'last_markedforebay']
    HEADER_MODULE = ['eBayModuleID', 'ItemID', 'Condition', 'PhotographedBy', 'PhotographedAt', 'DateMarkedForEbay', 'WholesaleCost']
    
    cfl.create_new_list('Untitled.csv', 'used.csv', HEADER_FM, 'used_records.json')
    cfl.create_new_list('eBay Module - Photography - All Records.csv', 'distressed.csv', HEADER_MODULE, 'module_records.json')
    
    folder_list = []
    used_dir = []
    module_dir = []
    with open('used_records.json', 'r') as x:
        used_dict = json.load(x)

    # Sort the folders from source dir to either used or tobeposted locations.
    # Original folders are deleted from sort_me after they're moved.
    cfl.create_folder_list(sort_me, folder_list)
    for itemID in folder_list:
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
        except:
            continue
        
    # After the folders are sorted the individual photo files for used items are pulled from itemID folders and placed into used
    # Then empty folder is deleted. 
    cfl.create_folder_list(used, used_dir)
    
    at_dict = dict()

    for itemID in used_dir:
        sub_folder = []
        try:
            cfl.create_folder_list(f'{used}/{itemID}', sub_folder)
        
            for photo in sub_folder:
                shutil.copy(f'{used}/{itemID}/{photo}', f'{used}')
            shutil.rmtree(f'{used}/{itemID}')
            # Writes new used records to airtable.
            at_dict['fldhMuDWW6xC763vG'] = itemID
            table.create(at_dict)
            
        except:
            continue
      
    
    
    # Add " Trade" to folders for trade-in itemIDs. 
    cfl.create_folder_list(tobeposted, module_dir)
    
    with open('module_records.json', 'r') as x:
        module_dict = json.load(x)

    for itemID in module_dir:
        if itemID in module_dict:
            if module_dict[f'{itemID}']['Condition'] == 'T':
                dir_util.copy_tree(f"{tobeposted}/{itemID}",
                                        f"{tobeposted}/{itemID} Trade")
                shutil.rmtree(f'{tobeposted}/{itemID}')
        else:
            print(f'{itemID} not in module. Please check available qty and add to module.')
            
    # Adds Finder tag to items in tobeposted.
    cfl.create_folder_list(tobeposted, module_dir)
    for file_name in module_dir:
        try:
            md = OSXMetaData(f"{tobeposted}/{file_name}")
            md.tags = [Tag("eBay", FINDER_COLOR_RED)]
        except:
            continue      
        

###########################
start = time.perf_counter()

sorter('/Volumes/ebay/ToBeEdited/tobesorted', '/Volumes/ebay/testtobeposted', '/Volumes/ImageEngine/testusedinbox' )

finish = time.perf_counter()
############################

print(f"completed in {finish - start:0.4f} seconds")


# TODO: working GUI to make this runable by others.
#       Buttons to run the sorters, an exceptions field to skip certain items if they're kicking errors.
