import csv
import json
import sys
from typing import Callable, List, Dict
from utils.response_mapping import *
from utils import firebasedb, linking
from datetime import datetime

def main():
    assert(len(sys.argv) >= 3)
    firebasedb.init_survey_firebase()
    db = firebasedb.get_survey_firestore_client()
    mapping_filename = sys.argv[1]
    input_filename = sys.argv[2]

    mappings_dict = get_mappings_dict(mapping_filename)
    inputs_dict = input_file_to_dicts(input_filename)
    respondents_dict = get_respondents_map(inputs_dict, db)

    with open("respondents_backup.json", "w+") as backup_file:
        backup_dict = {}
        for (key, value) in respondents_dict.items():
            backup_dict[linking.hash_email(key)] = value
        json.dump(backup_dict, backup_file)
        
    updates_dict = add_all_responses(mappings_dict, inputs_dict, respondents_dict)

    with open("updates.json", "w+") as updates_file:
        json.dump(updates_dict, updates_file)
    
    print("The update json has been placed in updates.json. Please check this to validate that the update is correct")

    user_confirmation = ""
    while user_confirmation != "confirm":
        user_confirmation = input("Type 'confirm' to finalize updates")
    
    commit_all_updates(updates_dict, db, verbose = True)

    

def add_all_responses(mappings_dict : Dict[str, EntryMapping],
                        inputs_dict : Dict[str, dict], respondents_map : Dict[str, dict]):
    filtered_dicts = {}
    for input_dict in inputs_dict.values():
        email = input_dict["email"]
        add_to_respondent(email, input_dict, respondents_map, mappings_dict)
        filtered_dicts[email] = filter_unchanged(respondents_map[email], mappings_dict)
    return filtered_dicts

def get_mappings_dict(mapping_filename : str) -> Dict[str, EntryMapping]: 
    with open(mapping_filename, "r") as mapping_file:
        mappings_dict = json.load(mapping_file)
        entry_mappings_dict = {}
        for key in mappings_dict:
            entry_mappings_dict[key] = EntryMapping(mappings_dict[key])
        return entry_mappings_dict

# takes a json or csv input file with the responses
# returns converted to dict
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
        input_dict : dict = {}
        for processed_dict in processed_dicts:
            assert "email" in processed_dict
            email = processed_dict["email"]
            input_dict[email] = processed_dict
        return input_dict

def get_respondents_map(input_dicts : Dict[str, dict], db) -> Dict[str, dict]:
    responses_ref = db.collection("responses")
    respondents_map = {}
    
    for email in input_dicts.keys():
        hashed_email = linking.hash_email(email)
        doc = responses_ref.document(hashed_email).get()
        doc_dict = doc.to_dict()
        respondents_map[email] = doc_dict
    return respondents_map

def add_to_respondent(email : str, input_dict : Dict[str, dict], respondents_map : Dict[str, dict], mappings_dict : Dict[str, dict]):
    cur_dict = respondents_map[email]
    for mapping_name in mappings_dict:
        if mapping_name in input_dict:
            mapping = mappings_dict[mapping_name]
            input_value = input_dict[mapping_name]
            entry = ResponseEntry(input_value)
            add_response_entry(entry, mapping, cur_dict)

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

# gets the id for this month in the monthly responses field
def get_monthly_response_id(date = datetime.now()):
    return "{}_{}".format(date.year, date.month)

def commit_all_updates(updates_dict : Dict[str, dict], db, increment_response_count = True, verbose = False):
    for (key, value) in updates_dict.items():
        commit_update(key, value, db, increment_response_count)
        if verbose:
            print("updated {}".format(key))

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
            "total_responses" : total_responses
        })
    responses_ref.document(hashed_email).update(update_dict)

def update_template(mappings : Dict[str, dict], db): 
    TEMPLATE_ID = "template"
    responses_ref = db.collection("responses")
    template_ref = responses_ref.document("template")
    template_dict = template_ref.get().to_dict()
    for (key, mapping) in mappings.items():
        entry = ResponseEntry(mapping.description)
        add_response_entry(entry, mapping, template_dict)
    update_dict = filter_unchanged(template_dict, mappings)
    template_ref.update(update_dict) 

if __name__ == "__main__":
    main()