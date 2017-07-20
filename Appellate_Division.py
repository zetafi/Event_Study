import csv
import sys
import re
import os.path



# ALL APPELLATE DATA
## Extract items with a court abbreviation that is "CAFC". COL2 is "Court Abbreviation".
## All items that has a remedy value are trial court cases
## File saved in data/trial_all.csv   Total : 1061 items
def all_complete_trial_data():
    # filings are too long, add this line to avoid error when reading the csv
    csv.field_size_limit(sys.maxsize)

    with open('data/step9_file.csv', 'rb') as csvfile:
        fulldata = csv.reader(csvfile)
        header = fulldata.next()

        count = 0

        # put the result file in to "data/Trial" directory
        if not os.path.isdir("data/Trial"):
            os.mkdir("data/Trial")

        with open("data/Trial/all_complete_trial.csv", 'w') as resultfile: