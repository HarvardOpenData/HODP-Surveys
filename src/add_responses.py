import csv
import json
from typing import Callable, List, Dict
from utils.response_mapping import *
from utils import firebasedb, linking
from datetime import datetime

def main():
    pass

def get_mappings_dict(mapping_filename : str) -> Dict[str, EntryMapping]: 
    with open(mapping_filename, "r") as mapping_file:
        mappings_dict = json.load(mapping_file)
        entry_mappings_dict = {}
        print(mappings_dict)
        for key in mappings_dict:
            print(key)
            entry_mappings_dict[key] = EntryMapping(mappings_dict[key])
        return entry_mappings_dict

# takes a json or csv input file with the responses
# returns converted to d
def input_file_to_dicts(input_filename : str, transform : Callable[[dict], dict] = None) -> Dict[str, dict]:
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
        dicts_mapping : dict = {}
        for processed_dict in processed_dicts:
            assert "email" in processed_dict
            email = processed_dict["email"]
            dicts_mapping[email] = processed_dict
        return dicts_mapping

# takes a dict and a set of mappings
# returns a new dict with only the keys where the top levell changed
def filter_unchanged(cur_dict : dict, mappings : Dict[str, EntryMapping]) -> dict:
    paths = [mapping.path for mapping in mappings.values()]
    # unique top levels in the mapping path
    top_levels : List[str] = list(set([path[0] for path in paths]))
    filtered_dict = {}
    for top_level in top_levels:
        if top_level in cur_dict:
            filtered_dict[top_level] = cur_dict[top_level]
    return filtered_dict


# commits the update to Firestore
# update_dict should only include the fields that will actually be updated
def commit_update(email : str, update_dict : dict, db, 
                    increment_response_count = True, monthly_response_id = get_monthly_response_id()):
    hashed_email = linking.hash_email(email)
    emails_ref = db.collection("emails")
    responses_ref = db.collection("responses")
    if increment_response_count:
        month_str = get_monthly_response_id()
        email_doc = emails_ref.document(email)
        email_dict : dict = email_doc.get().to_dict()
        if "monthly_responses" not in email_dict:
            email_dict["monthly_responses"] = {}
        if "total_responses" not in email_dict: 
            email_dict["total_responses"] = 0
        monthly_responses = email_dict["monthly_responses"]
        total_responses = email_dict["total_responses"]
        if monthly_response_id not in monthly_responses:
            monthly_responses[monthly_response_id] = 1
        else:
            monthly_responses[monthly_response_id] += 1
        total_responses += 1
        email_doc.update({
            "monthly_responses" : monthly_responses,
            "tota_responses" : total_responses
        })
    responses_ref.document(hashed_email).update(update_dict)

# gets the id for this month in the monthly responses field
def get_monthly_response_id(date = datetime.now()):
    return "{}_{}".format(date.year, date.month)

def update_template(mappings : Dict[str, dict], db): 
    TEMPLATE_ID = "template"
    responses_ref = db.collection("responses")
    template_ref = responses_ref.document("template")
    template_dict = template_ref.get().to_dict()
    for (key, mapping) in mappings:
        entry = ResponseEntry(mapping.description)
        add_response_entry(entry, mapping, template_dict)
    update_dict = filter_unchanged(template_dict, mappings)
    template_ref.update(update_dict) 

if __name__ == "__main__":
    main()