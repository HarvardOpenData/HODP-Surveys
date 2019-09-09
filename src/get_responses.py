import firebase_admin
import csv
from firebase_admin import credentials
from firebase_admin import firestore
import json
import random

from utils.response_mapping import *
from utils import firebasedb, linking
from typing import List

def get_response_values(paths : List[str], db, optional_paths = [], verbose = False) -> List[dict]: 
    responses_ref = db.collection("responses")
    response_docs = responses_ref.stream()
    responses = []
    for doc in response_docs:
        if doc.id == "template":
            continue
        doc_dict = doc.to_dict()
        out_dict = {}
        should_add = True
        for path in paths:
            value = get_response_value(path, doc_dict)
            if value is not None:
                out_dict[path] = value
            elif path not in optional_paths:
                should_add = False
        if should_add:
            responses.append(out_dict)
            if verbose:
                print("retrieved {} responses".format(len(responses)))
    return responses

def get_emails_with_paths(paths : List[str], db, optional_paths = [], verbose = True) -> List[dict]:
    responses_ref = db.collection("responses")
    emails_ref = db.collection("emails")
    email_docs =  emails_ref.where("has_demographics", "==", True).stream()
    respondents_list = []
    for email_doc in email_docs:
        email = email_doc.id
        hashed_email = linking.hash_email(email)
        response_doc = responses_ref.document(hashed_email).get()
        response_dict = response_doc.to_dict()
        out_dict = { "email" : email }
        should_add = True
        for path in paths:
           if should_add:
                value = get_response_value(path, response_dict)
                if value is not None:
                    out_dict[path] = value
                else:
                    should_add = False
        if should_add:
            respondents_list.append(out_dict)
            if verbose:
                print("retrieved {} emails".format(len(out_dict)))
    return respondents_list


def respondents_list_to_json(respondents_list : List[dict], output_filename : str, fieldnames = None):
    with open(output_filename, "w+") as output_file:
        json.dump(respondents_list, output_file, indent = 4)

def respondents_list_to_csv(respondents_list : List[dict], output_filename : str, fieldnames = None):
    with open(output_filename, "w+") as output_file:
        if fieldnames is None:
            fieldnames = respondents_list[0].keys()
        writer = csv.DictWriter(output_file, fieldnames = fieldnames)
        writer.writeheader()
        for respondent_dict in respondents_list:
            writer.writerow(respondent_dict)

def conduct_lottery(db : firestore.firestore.Client, count = 1, month = None, 
                        allow_repeats = False, default_entries = 1) -> List[str]:
    emails_ref = db.collection("emails")
    emails_docs = emails_ref.stream()
    entries : List[str] = []

    for doc in emails_docs:
        entries.extend([doc.id] * default_entries)
        if month is not None:
            doc_dict : dict = doc.to_dict()
            monthly_responses = doc_dict.get(month, 0)
            entries.extend([doc.id] * monthly_responses)
    
    winners = []
    
    for _ in range(count):
        winner = random.choice(entries)
        if not allow_repeats:
            entries = [entry for entry in entries if entry != winner]
        winners.append(winner)

    return winners


def get_all_paths(cur_dict : dict):
    paths = []
    for key, value in cur_dict.items():
        if type(value) is dict and not ("value" in value and "date" in value):
            sub_paths = get_all_paths(value)
            paths.extend([key + "/" + sub_path for sub_path in sub_paths])
        else:
            paths.append(key)
    return paths
        
def get_all_template_paths(db : firestore.firestore.Client):
    template_dict = db.collection("responses").document(document_id="template").get().to_dict()
    return get_all_paths(template_dict)
