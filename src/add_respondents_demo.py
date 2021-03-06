import csv
import sys
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import datetime
from utils.linking import hash_email
from utils import firebasedb

# Adds respondents from a csv when they have demographic info

def new_user():
    return {
        u"has_demographics" : True,
        u"monthly_responses" : {},
        u"total_responses" : 0,
        u"date_created" : datetime.datetime.now(),
        u"last_demographic_update" : datetime.datetime.now()
    }

def get_or_none(d, k):
    if k in d and len(d[k].strip()) > 0:
        return d[k].strip()
    else: 
        return None

def main():
    if len(sys.argv) < 2:
        print("Import csv required")
        exit(0)

    file_name = sys.argv[1]
    with open(file_name, "r") as f:
        reader = csv.DictReader(f)
        respondents = list(reader)

    firebasedb.init_survey_firebase()

    db = firebasedb.get_survey_firestore_client()

    emails_ref = db.collection(u"emails")
    responses_ref = db.collection(u"responses")
    for respondent in respondents:
        if "email" not in respondent and "@college.harvard.edu" in respondent["email"].strip():
            continue
        email = respondent["email"].strip().lower()
        email_hash = hash_email(email) 
        email_ref = emails_ref.document(email)
        email_doc = email_ref.get()
        if not email_doc.exists:
            email_ref.set(new_user())
        else:
            email_ref.update({
                u"has_demographics" : True
            })  
        concentration = get_or_none(respondent, "concentration")
        ethnicity = get_or_none(respondent, "ethnicity")
        update_dict = {
            u"demographics" : {
                u"gender" : get_or_none(respondent, "gender"),
                u"year" : get_or_none(respondent, "year"),
                u"freshman_dorm" : get_or_none(respondent, "freshman_dorm"),
                u"house" : get_or_none(respondent, "house"),
                u"concentration" : [x.strip() for x in concentration.split()] if concentration is not None else None,
                u"ethnicity" : [x.strip() for x in ethnicity.split(",")] if ethnicity is not None else None
            }
        }

        response_ref = responses_ref.document(email_hash)
        response_doc = response_ref.get()
        if not response_doc.exists:
            response_ref.set(update_dict)
        else:
            response_ref.update(update_dict)
        print("Added ", email)

    
if __name__ == "__main__":
    main()