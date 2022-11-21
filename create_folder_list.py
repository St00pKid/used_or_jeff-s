from os import listdir
from csv import DictReader, reader, writer
from json import dumps


def create_folder_list(src_location , folder_list):
    """Create folder list from condition folders. 
    Takes argument for the source location and writes to a list variable that is passed to it."""
    
    for f in listdir(src_location):
        # Skips hidden files
        if not f.startswith("."):
            # Add folders to folder_list
            folder_list.append(f)
            folder_list.sort()
            
            
def csv_to_json():
    """Create dictionary with itemID as key and condition as value. Formats json file with itemID as the key and dictionary as the value."""
    # Open and write ebay module csv file to a dictionary list
    json_array = []
    with open('Non-Photographed Sweetwater Used Gear.csv', 'r') as ref, open('used_records.json', 'r') as used_records:
        data_list = DictReader(ref)
        print(data_list)
        for row in data_list:
            if row not in used_records:
                json_array.append(row)
    
    # Loop through list and write the itemID value to key for each object and set value to object to create a dictionary of dictionaries
    formatted_dict = {}
    for i in json_array:
        itemid = i['ItemID']
        formatted_dict[itemid] = i
    
    # Write the formatted dictionary to json file.
    with open('used_recorjim rds.json', 'a') as jsonfile:
        json_string = dumps(formatted_dict,indent=4)
        jsonfile.write(json_string)

def create_new_list():
    """Reads CSV file and appends entries that are not empty to new list. Writes to new csv called trimmed_file.csv"""
    # Not currently used for testing purposes. Will allow the script to trim and combine multiple files into one.
    # create_file_list()
    temp_list = []
    new_list = []

    with open("Untitled.csv", 'r', newline='') as csv_file:
        csv_list = list(reader(csv_file))
        for row in csv_list:
            if not row[0] == '':
                temp_list.append(row)
    
    for row in temp_list:
        if not row[3] == '':
            new_list.append(row)
    
    HEADER_FM = ['itemid', 'ebay_id', 'instock_qty', 'warehouse_qty', 'ebay_team_qty', 'newitemreceiveddate', 
             'last_upload_date', 'ebay_status', 'last_markedforebay']
    
    with open('trimmed_file.csv', 'w') as trimmed_file:
        csv_writer = writer(trimmed_file)
        csv_writer.writerow(HEADER_FM)
        csv_writer.writerows(new_list)
