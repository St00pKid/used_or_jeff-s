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
    print(sort_dir)
    for item in sort_dir:
        if item not in used_dict:
            dir_util.copy_tree(f"sort_me/{item}",
                                    f"tobeposted/{item}")
        
        else:
            dir_util.copy_tree(f"sort_me/{item}",
                                    f"used/{item}")

        shutil.rmtree(f'sort_me/{item}/')
    
    cfl.create_folder_list('used', used_dir)
    for item in used_dir:
        shutil.move(item, 'used') # TODO: this is broken at the moment.
        

###########################
start = time.perf_counter()

# cfl.csv_to_json()
sorter()


finish = time.perf_counter()
############################

print(f"completed in {finish - start:0.4f} seconds")
