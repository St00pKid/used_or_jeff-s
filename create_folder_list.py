from os import listdir
from csv import DictReader, reader, writer
import json

def create_folder_list(src_location , folder_list):
    """Create folder list from condition folders. Used to skip hidden files.
    Takes argument for the source location and writes to a list variable that is passed to it."""
    
    for f in listdir(src_location):
        # Skips hidden files
        if not f.startswith("."):
            # Add folders to folder_list
            folder_list.append(f)
            folder_list.sort()
            
            
def csv_to_json(src_file, output_JSON):
    """Create dictionary with itemID as key and condition as value. Formats json file with itemID as the key and dictionary as the value."""
    # Open and write ebay module csv file to a dictionary list


    formatted_dict = {}
    for i in json_array:
        j = i['ItemID']
        j = j.lower()
        # Set itemID as dictionary key for each item. If consignment or non-inventory the ebay module number is used as the itemID
        if j == 'consignitem':
            itemid = i['eBayModuleID']
            formatted_dict[itemid] = i
            i['Condition'] = 'Z'
        else:    
            itemid = i['ItemID']
            formatted_dict[itemid] = i
            
    # Write the formatted dictionary to json file. Overwrites existing file. Overwriting removes the need to purge old records.
    with open(output_JSON, 'w') as jsonfile:
        json_string = json.dumps(formatted_dict,indent=4)
        jsonfile.write(json_string)

def create_json(src_file, trimmed_file, header, output_JSON):
    """Reads FileMaker export CSV file and appends entries that are not empty to new list. Writes to new csv called trimmed_file.csv
    First arguement needs to be a csv from filemaker to be formatted correctly. Second arg is the trimmed csv file (usually 'trimmed_file.csv) and will be formatted to json.
    Third arguement is for the csv header. For simplicity it needs to be fed to the function.
    """
    temp_list = []

    with open(f'{src_file}', 'r+', newline='') as csv_file:
        csv_list = list(reader(csv_file))
        for row in csv_list:
            if not row[0] == '' or row[2] == '':
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
        # Set itemID as dictionary key for each item. If consignment or non-inventory the ebay module number is used as the itemID
        if j == 'consignitem':
            itemid = i['eBayModuleID']
            formatted_dict[itemid] = i
            i['Condition'] = 'Z'
        else:    
            itemid = i['ItemID']
            formatted_dict[itemid] = i
            
    # Write the formatted dictionary to json file. Overwrites existing file. Overwriting removes the need to purge old records.
    with open(output_JSON, 'w') as jsonfile:
        json_string = json.dumps(formatted_dict,indent=4)
        jsonfile.write(json_string)
