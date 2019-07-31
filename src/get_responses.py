import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from utils.response_mapping import *
from utils import firebasedb, linking
from typing import List

def get_response_values(paths : List[str], db) -> List[dict]: 
    responses_ref = db.collection("responses")
    response_docs = responses_ref.stream()
    responses = []
    for doc in response_docs:
        if doc.id == "template":
            continue
        doc_dict = doc.to_dict()
        out_dict = {}
        for path in paths:
            value = get_response_value(path, doc_dict)
            out_dict[path] = value
        if not (None in out_dict.values()):
            responses.append(out_dict)
    return responses



