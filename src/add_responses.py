import csv
import json
from utils.response_mapping import *
from utils import firebasedb
from utils import linking
def main():
    raise NotImplementedError()

def get_mappings_dict(mapping_filename : str) -> dict: 
    with open(mapping_filename, "r") as mapping_file:
        mappings_dict = json.load(mapping_file)
        entry_mappings_dict = {}
        print(mappings_dict)
        for key in mappings_dict:
            print(key)
            entry_mappings_dict[key] = EntryMapping(mappings_dict[key])
        return entry_mappings_dict
if __name__ == "__main__":
    main()