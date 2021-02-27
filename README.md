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

`python main.py --action get_json --form_numbers "form_number1" "form_number2" "form_numberN"`

`python main.py --action download --form_number "Form W-2" --year_range <min_year>-<max_year>`

##### Example:

##### 1-

`python main.py --action get_json --form_numbers "Form W-2" "Form 1095-C" "Publ 1"`

##### 2-
`python main.py --action download --form_number "Form W-2" --year_range 2010-2020`

#### Testing

To run the test you have to run:

` python test_main.py `

This will test the main functions of the project

