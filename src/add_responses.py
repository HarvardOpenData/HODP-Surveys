import csv
import json
from typing import Callable, List
from utils.response_mapping import *
from utils import firebasedb
from utils import linking

def get_mappings_dict(mapping_filename : str) -> dict: 
    with open(mapping_filename, "r") as mapping_file:
        mappings_dict = json.load(mapping_file)
        entry_mappings_dict = {}
        print(mappings_dict)
        for key in mappings_dict:
            print(key)
            entry_mappings_dict[key] = EntryMapping(mappings_dict[key])
        return entry_mappings_dict

def input_file_to_dict(input_filename : str, transform : Callable[[dict], dict] = None) -> List[dict]:
    with open(input_filename, "r") as input_file:
        raw_dicts : list = []
        if input_filename.endswith(".json"):
            raw_dicts : list = json.load(input_file)
        elif input_filename.endswith(".csv"):
            reader = csv.DictReader(input_file)
            for row in reader:
                raw_dicts.append(row)
        processed_dicts : List[dict] = None
        if transform is not None: 
            processed_dicts : List[dict] = [transform(raw_dict) for raw_dict in raw_dicts]
        else:
            processed_dicts : List[dict] = raw_dicts
        return processed_dicts