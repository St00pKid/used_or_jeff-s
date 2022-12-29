from os import listdir
from csv import DictReader, reader, writer
import json

def create_folder_list(src_location , folder_list):
    """Like listdir but filters out hidden files"""
    for f in listdir(src_location):
        # Skips hidden files
        if not f.startswith("."):
            # Add folders to folder_list
            folder_list.append(f)
            folder_list.sort()
    return folder_list

def create_json(src_file, trimmed_file, header, output_JSON):
    temp_list = []

    with open(f'{src_file}', 'r+', newline='') as csv_file:
        csv_list = list(reader(csv_file))
        for row in csv_list:
            if row[0] != '' and len(row[0]) > 1:
                temp_list.append(row)
        csv_file.seek(0)
        csv_writer = writer(csv_file)
        csv_writer.writerow(header)
        csv_writer.writerows(temp_list)
        
    json_array = []
    with open(f'{trimmed_file}', 'r') as ref, open(output_JSON, 'w+') as used_records:
        data_list = DictReader(ref)
        for row in data_list:
            if row not in used_records:
                json_array.append(row)    
                
    formatted_dict = {}
    for i in json_array:
        j = i['ItemID']
        j = j.lower()
        # Set itemID as dictionary key for each item. 
        # If consignment or non-inventory the ebay module number is used as the itemID
        if j == 'consignitem':
            itemid = i['eBayModuleID']
            formatted_dict[itemid] = i
            i['Condition'] = 'Z'
        else:    
            itemid = i['ItemID']
            formatted_dict[itemid] = i
            
    # Write the formatted dictionary to json file. Overwrites existing file. 
    # Overwriting removes the need to purge old records.
    with open(output_JSON, 'w') as jsonfile:
        json_string = json.dumps(formatted_dict,indent=4)
        jsonfile.write(json_string)
