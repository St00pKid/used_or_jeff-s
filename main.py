import json
import create_folder_list as cfl
from distutils import dir_util
import shutil
import time


FOLDER_LIST = []

with open('used_records.json', 'r') as x:
    used_dict = json.load(x)

def sorter():
    for item in FOLDER_LIST:
        if item not in used_dict:
            dir_util.copy_tree(f"sort_me/{item}",
                                    f"tobeposted/{item}")
        
        else:
            dir_util.copy_tree(f"sort_me/{item}",
                                    f"used/{item}")

        shutil.rmtree(f'sort_me/{item}/')

start = time.perf_counter()

cfl.create_folder_list(FOLDER_LIST)
cfl.csv_to_json()
sorter()

finish = time.perf_counter()

print(f"completed in {finish - start:0.4f} seconds")
