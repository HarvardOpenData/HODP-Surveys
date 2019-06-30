# HODP Surveys

## Overview
HODP Surveys is the Harvard College Open Data Project's method of collecting survey data about the Harvard student body. In order to make taking surveys as easy as possible and without bothering those that are not interested in surveys, we use a survey group where students interested in helping with our mission can sign up and receive occasional surveys. They fill out their demographic information one time and all future survey responses will be linked to that initial demographic info. As a result, we are able to make surveys quicker and easier for students to fill out while still enabling sufficient information to conduct analysis. We also take additional steps to preserve student privacy when they answer surveys that are elaborated upon below. This repository holds the basic code for non-automated interaction with the HODP Surveys database, including manual addition of members, retrieval of specific data, and modifications to the database structure.

## Privacy Measures
HODP takes student privacy very seriously in our survey responses. We believe that to obtain a large quantity of genuine responses, students must feel that their survey responses will be properly anonymous. As a result, we have taken a series of measures to ensure the privacy of HODP students.

### Aggregate Data Only
We will never publish individual responses from the survey nor give them to any non-HODP party. We will only publish analysis based on aggregate responses, and we will only publish such analysis if we are confident that the data is properly anonymized such that the respondents cannot be identified.

### Review of Data Requests
Only HODP executive committee members wil have direct access to the database and be able to pull response data. Any HODP members who wish to access some subset of the survey data will be required to submit a request that will be reviewed by the executive committee. The retrieval of all data will be done by automated script so executive committee members will also not have direct access to the raw response data.

### Internal Anonymization
In order to link responses, we use email addresses. However, we also want to make it so that executive committee members cannot accidentally see individual survey responses. So, in our database we do not link individuals via email address, but using a unique hash of their email address so that at first glance any individuals in the database cannot be easily linked to their responses. See below for more specifics of the structure of the surveys database. 

## Database Structure
HODP uses Google Firebase for storage of survey responses. We have two collections in the database: emails and responses.

### Emails Collection
The emails collection has as an id the email of an individual, and no response information is stored in this database. Instead, data such as the last contact, last demographic update, and number of responses are recorded, but nothing about the content of the responses themselves.

### Responses Collection
The responses collection stores the actual responses of an individual. Each top level key should correspond to a response. The ID for each document in the collection is the MD5 hash of the respondent's email. This ensures that respondents and their emails cannot be easily identified. 

## Data Requests
Data requests should be sent in an email to harvardopendataproject@gmail.com. Included in the request should be what analysis you plan to do with the data, as well as what specific data points you need. You must specify what kind of analysis you plan to do with each data point. The HODP executive committee will review the request and respond to you within a week.
