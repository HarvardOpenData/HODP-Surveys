from get_responses import conduct_lottery  

from utils import firebasedb
import sys

if __name__ == "__main__":
    recipients = 1
    month = None
    if len(sys.argv) > 1:
        recipients = int(sys.argv[1])
    if len(sys.argv) > 2:
        month = sys.argv[2]
    firebasedb.init_survey_firebase()
    db = firebasedb.get_survey_firestore_client()
    results = conduct_lottery(db, recipients, month = month)
    print(results)