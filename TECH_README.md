# Technical README
This is the README for HODP members to learn how to use the survey group infrastructure, including how to retrieve and add responses for the survey group.

## Overview
The survey group is our way of storing and linking responses across time by respondents while still maintaining a reasonable level of anonymity. This offers us a couple of advantages. The first is that we do not need to ask for demographic information in every survey, which reduces the number of questions on our surveys. The second is that we can do cross-time comparisons, so for example, we can examine how people's opinions shifted before and after a presidential debate. The data is stored in Google's Firebase firestore, and the code to retrieve and save the data is provided in this repository.

## Data Storage
The data is stored in firebase in two separate collections. The first is the `emails` collection and the second is the `responses` collection. The `emails` collection contains the identifiable information for the respondent, and does not contain information that we would consider private. This includes (obviously) their email address so that we can send emails, whether they have filled out demographic information, and how many they have had (so we can lottery gift cards). The `responses` collection is more anonymized, and contains the actual response data. The keys in this case are the md5 hashes of the respondent's email address. This is a one way hash so that we can add information given a respondent's email address, but it is not easy to retrieve an email address given a response document. While this is not 100% irreversibly anonymous, it allows us to inspect responses and check for bugs while still maintaining the anonymity of users.

### Authenticating to Database
To manage the database locally, you will need to obtain a credentials file from Google Cloud. Only authorized HODP members will have this access. The instructions for how to download the credential file are on the [Firestore Python Quickstart](https://firebase.google.com/docs/firestore/quickstart#initialize). Once the credentials files are downloaded, they should be placed in the `src` folder, and renamed as `survey_creds.json`. **IMPORTANT NOTE**: Make sure these credentials are _NEVER_ committed to the git repository and are always ignored in the `.gitignore`. 

The code for accessing the firebase is then provided in `src/utils/firebasedb.py`.

### Response format
In order to make the data storage for responses reasonable, we use a pseudo-folder structure that is described by paths. Note that this is _not_ the same as the path description that Firestore enables by default. Instead, we might store responses to a survey as follows:
```
"EMAIL_HASH" : {
    "demographics" : {
        ...
    },
    "politics" : {
        "2020_election" : {
            "party" : {
                "value" : "Democrat",
                "date" : "1/1/2020, 1:00 PM UTC"
            }
        }
    }
}
```
We would then associate a "path" with the party response as follows: `politics/2020_election/party`. The code for parsing a path and converting into nested dictionaries is provided in `src/utils/response_mapping.py`. We store the responses like this so that it is easy to organize responses.

Another key thing to notice is that we do not just store the raw response ("Democrat"), we also store the date where the response came from. This enables us to filter for recent responses, or to verify that someone provided a response after a particular date.

### Template document
In the responses collection, there is a document with key "template." This document keeps track of all possible paths, so that it is easy to quickly check which options we would have for retrieving data based on a path. This has all of the paths for surveys that have ever been added, and contains descriptions for each of the response values. 

## Adding Responses
To add responses, we need two things: a csv/json of all the responses, and a mapping json file to associate values in the dataset with a particular path.

### Mapping files
Because response values are stored as paths, we need a way to convert the keys in the dataset to a path to store. To do so, we define a json mapping file. This is represented in code by a an `EntryMapping` found in `src/utils/response_mapping.py`. 

The mapping file should define a JSON object. The **keys** of the JSON file should be the key in the dataset. For a csv, this would be the column header of the particular data points for an individual. The value associated with each key should be a JSON object with the following properties.
* `path` - this is the corresponding path in the firestore dictionary where this particular response should be placed.
* `description` - a brief description of what this response data point actually is for the future
* `type` - this is one of: `"value"`, `"list"`, `"json"`. This indicates how the response should be stored. If it is `"value"`, the raw response will be stored. If it is `"json"`, the text of the response will be parsed to a JSON object and then stored. If it is `"list"`, then a `separator` will need to be defined and the code will convert the response raw value to a list of values. This is an optional field and the default value is `"value"`. 
* `separator` - this is only required for `"list"` type mappings. The anticipated value for the input is something like, `item1,item2,item3`, but we don't want to store the raw string, so we instead use the `separator`, which in this case would be `","`, to separate the raw response into three separate strings, and store it as a list of those strings. 
* `mode` - this is one of: `"REPLACE"`, `"APPEND"`. This defines what should happen if we are adding a value and the path already exists. `"REPLACE"` says that we should replace the current value. `"APPEND"` says that we should add onto the existing value and convert it to a list. 

Here is an example of a mapping file for an advising survey that was sent out:

```
{ 
    "Q1" : {
        "path" : "advising/advisor_frequency",
        "description" : "The frequency that the respondent meets with their academic advisor",
        "mode" : "replace"
    },
    "Q2A" : {
        "path" : "advising/advisor_is_tutor",
        "description" : "Whether the respondent's advisor is also their tutor",
        "mode" : "replace"
    },
    "Q2B" : { 
        "path" : "advising/tutor_frequency",
        "description" : "The frequency that the respondent meets with their tutor",
        "mode" : "replace"
    },
    "Q3" : {
        "path" : "advising/tutor_subject_similarity",
        "description" : "The similarity of the respondent's tutors academic area to the respondent's academic area",
        "mode" : "replace"
    },
    "Q4" : {
        "path" : "advising/house_support_frequency",
        "description" : "The frequency that the respondent meets with house support staff",
        "mode" : "replace"
    },
    "Q5" : {
        "path" : "advising/advising_helpfulness",
        "description" : "How helpful the respondent thinks Harvard advising is",
        "mode" : "replace"
    }
}
```
### Code
The code for actually adding the responses is in `src/add_responses.py`. This can either be included as a library in another python file or it can be used to directly add code through the command line. Typically everything is run from inside the `src` directory. The command to run it is:
```
python3 add_responses.py mapping_file.json data_file.csv
```
Once the command is run, it will generate two files. The first is `respondents_backup.json`, which is a simple json backup of the original respondents backup file. The second is `updates.json`, this is a list of the updates that will be sent up. The `updates.json` file should be validated manually to make sure everything looks right. Then after typing `confirm` the updates will be pushed. 

