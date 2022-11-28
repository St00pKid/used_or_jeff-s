import json
import create_folder_list as cfl
from distutils import dir_util
import shutil
import time


with open('used_records.json', 'r') as x:
    used_dict = json.load(x)

def sorter(sort_me, tobeposted, used):
    """Sorts folders in first argument to second arguement or third argument based on if they are in the used_records.json. 
    used_records.json needs to be in the same folder as this file. Arguments for paths are used make it easier to change where the script is pointing.
    
    All used items in inventory are in used_records.json. Sorter looks to see if the items has an assigned ebay_id or if it has a ebay status of shipped. 
    If True the folder with photos is moved to whatever folder is assigned to the used argument. If False the are moved to the tobeposted argument.
    After folders are moved the individual image files in the used item folders are moved from their folders to the used directory and the original folders
    are deleted."""
    
    folder_list = []
    used_dir = []
    
    # Sort the folders from source dir to either used or tobeposted locations.
    # Original folders are deleted from sort_me after they're moved.
    cfl.create_folder_list(sort_me, folder_list)
    for itemID in folder_list:
        if itemID not in used_dict:
            dir_util.copy_tree(f"{sort_me}/{itemID}",
                                    f"{tobeposted}/{itemID}")
            shutil.rmtree(f'{sort_me}/{itemID}/')
        
        elif used_dict[f'{itemID}']['ebay_id'] == '' or used_dict[f'{itemID}']['ebay_status'] == "Shipped":
            dir_util.copy_tree(f"{sort_me}/{itemID}",
                                    f"{used}/{itemID}")
            shutil.rmtree(f'{sort_me}/{itemID}/')
            
        else:
            dir_util.copy_tree(f"{sort_me}/{itemID}",
                                    f"{tobeposted}/{itemID}")
            shutil.rmtree(f'{sort_me}/{itemID}/')
        
    
    # After the folders are sorted the individual photo files for used items are pulled from itemID folders and placed into used
    # Then empty folder is deleted. 
    cfl.create_folder_list(used, used_dir)
    
    
    for itemID in used_dir:
        print(f'{itemID}')
        sub_folder = []
        cfl.create_folder_list(f'{used}/{itemID}', sub_folder)
        for photo in sub_folder:
            shutil.copy(f'{used}/{itemID}/{photo}', f'{used}')
        shutil.rmtree(f'{used}/{itemID}')


###########################
start = time.perf_counter()

cfl.create_new_list('Untitled.csv', 'trimmed_file.csv') # Update data set
sorter('/Volumes/ebay/ToBeEdited/tobesorted', '/Volumes/ebay/testtobeposted', '/Volumes/ImageEngine/testusedinbox' )

finish = time.perf_counter()
############################

print(f"completed in {finish - start:0.4f} seconds")

