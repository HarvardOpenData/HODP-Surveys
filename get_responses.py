import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


# key: list of keys to retrive
# database object to use
# TODO: The way of filtering can be improved.
## Should be using document snapshots instead to avoid downloading all data
def get_responses(keys, db):
    result = []
    responses_ref = db.collection(u"responses")
    docs = responses_ref.stream() 
    for doc in docs:
        doc_dict = doc.to_dict()
        new_dict = { k:v for (k, v) in doc_dict.items() if k in keys }
        if len(new_dict.keys()) == len(keys):
            result.append(new_dict)
    return result

