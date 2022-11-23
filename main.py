import json
import create_folder_list as cfl
from distutils import dir_util
import shutil
import time



with open('used_records.json', 'r') as x:
    used_dict = json.load(x)

def sorter():
    sort_dir = []
    used_dir = []
    cfl.create_folder_list('sort_me', sort_dir)
    for item in sort_dir:
        if item not in used_dict:
            dir_util.copy_tree(f"sort_me/{item}",
                                    f"tobeposted/{item}")
        
        elif used_dict[f'{item}']['ebay_id'] == '' or used_dict[f'{item}']['ebay_status'] == "Shipped":
            dir_util.copy_tree(f"sort_me/{item}",
                                    f"used/{item}")
        else:
            print(f'oops! {item} is throwing an error.')
        shutil.rmtree(f'sort_me/{item}/')
    
    cfl.create_folder_list('used', used_dir)
    for item in used_dir:
        sub_folder = []
        cfl.create_folder_list(f'used/{item}', sub_folder)
        for photo in sub_folder:
            shutil.move(f'used/{item}/{photo}', 'used')
        shutil.rmtree(f'used/{item}')

###########################
start = time.perf_counter()

cfl.create_new_list('Untitled.csv', 'trimmed_file.csv')
sorter()

finish = time.perf_counter()
############################

print(f"completed in {finish - start:0.4f} seconds")
