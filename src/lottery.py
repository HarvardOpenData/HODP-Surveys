from get_responses import conduct_lottery  

from utils import firebasedb

if __name__ == "__main__":
    firebasedb.init_survey_firebase()
    db = firebasedb.get_survey_firestore_client()
    results = conduct_lottery(db, 1, month = "2019_09")
    print(results)