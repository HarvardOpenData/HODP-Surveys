import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from utils import firebasedb
from datetime import datetime, timedelta

def main():
    firebasedb.init_survey_firebase()
    db = firebasedb.get_survey_firestore_client()
    today = datetime.now().date()
    signups_today, total_signups = count_signups_after_date(db, today)
    print("Sign ups today: {}".format(signups_today))
    print("Total signups: {}".format(total_signups))

def count_signups_after_date(db, date): 
    emails_ref = db.collection("emails")
    docs = emails_ref.where("has_demographics", "==", True).stream()
    count = 0
    total_count = 0
    for doc in docs:
        doc_dict = doc.to_dict()
        if ("date_created" in doc_dict and doc_dict["date_created"].date() >= date):
            count += 1
        total_count += 1
    return (count, total_count)

if __name__ == "__main__":
    main()

