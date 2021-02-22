# Baires Dev - IRS Programming Exercise
####
This script is used to get taxes data from the url https://apps.irs.gov/app/picklist/list/priorFormPublication.html
format a json response with the command get_json and download the pdfs with the download command
####
Python version: Python 3.8.5
####

#### To clone the repository run:
`git clone https://github.com/DanLivassan/irs_programming.git`


#### To install the dependencies you have to run the command:
`pip install -r requirements.txt`


#### To run the script call the commands as bellow:

`python main.py get_json "<form_number>"`


`python main.py download "<form_number>" <min_year>-<max_year>`

##### Example:

##### 1-
`python main.py get_json "Form W-2"`

*if you want the response printed out in a file*

`python main.py get_json "Form W-2" > response.json`

##### 2-
`python main.py download "Form W-2" 2015-2020`


