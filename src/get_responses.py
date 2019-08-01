import firebase_admin
import csv
from firebase_admin import credentials
from firebase_admin import firestore

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

def respondents_list_to_csv(respondents_list : List[dict], output_filename : str):
    with open(output_filename, "w+") as output_file:
        writer = csv.DictWriter(output_file, fieldnames = respondents_list[0].keys())
        writer.writeheader()
        for respondent_dict in respondents_list:
            writer.writerow(respondent_dict)
        

