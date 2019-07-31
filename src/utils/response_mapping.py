from typing import List
from datetime import datetime
import json

###### MAPPING VALIDATION INFO ######
MODE_APPEND = "append"
MODE_REPLACE = "replace"
TYPE_VAL = "value"
TYPE_LIST = "list"
TYPE_JSON = "json"
valid_types = [TYPE_VAL, TYPE_LIST, TYPE_JSON]
valid_modes = [MODE_APPEND, MODE_REPLACE]
allowed_fields = ["path", "description", "mode", "type", "separator"]
required_fields = ["path", "description", "mode"]
protected_prefixes : List[str] = ["demographics"]
###### END MAPPING VALIDATION INFO ######


class ResponseEntry:
    def __init__(self, value, date : datetime = datetime.now()):
        self.value = value
        self.date = date
    def get_as_dict(self):
        return {
            "value" : self.value,
            "date" : self.date
        }

class EntryMapping:
    def __init__(self, dict_mapping : dict, is_update = False):
        if not is_update: 
            validate_mapping(dict_mapping)
            self.path = parse_path(dict_mapping["path"])
        else:
            self.path = dict_mapping["path"]
        self.description = dict_mapping["description"]
        self.mode = dict_mapping["mode"]
        if "separator" in dict_mapping:
            self.separator = dict_mapping["separator"]
        else:
            self.separator = None
        if "type" not in dict_mapping:
            self.type = TYPE_VAL
        else:
            self.type = dict_mapping["type"]


    def as_dict(self):
        return {
            "path" : self.path,
            "description" : self.description,
            "mode" : self.mode,
            "separator" : self.separator,
            "type" : self.type
        }
    
    def get_updated(self, update_dict : dict):
        cur_dict = self.as_dict()
        for (key, value) in update_dict.items():
            cur_dict[key] = value
        return EntryMapping(cur_dict, is_update = True)
    
    # converts a response entry to the correct type
    def convert_entry(self, entry : ResponseEntry):
        if self.type == TYPE_VAL:
            return entry
        elif self.type == TYPE_LIST:
            separator : str = self.separator
            assert type(entry.value) == str 
            value : str = entry.value
            return ResponseEntry(value.split(separator), entry.date)
        elif self.type == TYPE_JSON:
            assert type(entry.value) == str 
            parsed_json = json.loads(entry.value)
            return ResponseEntry(parsed_json, entry.date)
        else:
            raise Exception("Type is invalid. Should have been checked!")

def validate_mapping(mapping : dict):
    for field in required_fields: 
        assert field in mapping, "{} is a required field but is missing.".format(field)
    assert mapping["mode"] in valid_modes, "{} is not a valid mode".format(mapping["mode"])
    validate_path(mapping["path"])
    if "type" in mapping:
        assert mapping["type"] in valid_types, "{} is not a valid type".format(mapping["type"])
        if mapping["type"] == TYPE_LIST:
            assert("separator" in mapping)

def validate_path(path : str):
    for prefix in protected_prefixes:
        assert not path.startswith(prefix), "{} is a protected path!".format(path)

def parse_path(path : str):
    return path.split("/")

def add_response_entry(entry : ResponseEntry, mapping : EntryMapping, cur_dict : dict):
    path = mapping.path
    if len(path) == 1:
        key = path[0]
        converted_entry = mapping.convert_entry(entry)
        if key in cur_dict:
            if mapping.mode == MODE_REPLACE:
                cur_dict[key] = converted_entry.get_as_dict()
            elif mapping.mode == MODE_APPEND:
                if type(cur_dict[key]) == list:
                    cur_value : list = cur_dict[key]
                    cur_value.append(converted_entry.get_as_dict())
                else:
                    cur_arr : list = [cur_dict[key]]
                    cur_arr.append(converted_entry.get_as_dict())
                    cur_dict[key] = cur_arr
        else:
            cur_dict[key] = converted_entry.get_as_dict()
    else: 
        key = path[0]
        new_path = path[1:]
        new_mapping = mapping.get_updated({ "path" : new_path })
        if key in cur_dict:
            assert(type(cur_dict[key]) == dict)
            next_dict = cur_dict[key]
            add_response_entry(entry, new_mapping, next_dict)
        else:
            cur_dict[key] = {}
            next_dict = cur_dict[key]
            add_response_entry(entry, new_mapping, next_dict)

def get_response_entry(path : str, cur_dict : dict) -> dict:
    path_arr = path.split("/")
    if len(path_arr) == 1:
        key = path_arr[0]
        if key in cur_dict:
            return cur_dict[key]
        else:
            return None
    else:
        key = path_arr[0]
        new_path = "/".join(path_arr[1:])
        if key in cur_dict:
            new_dict = cur_dict[key]
            assert type(new_dict) == dict, "invalid path ending with {}".format(path)
            return get_response_entry(new_path, new_dict)
        else:
            return None

def get_response_value(path : str, cur_dict : dict):
    entry = get_response_entry(path, cur_dict)
    if entry is not None and "value" in entry:
        return entry["value"]
    else:
        return entry


