import csv
import sys
import re
import os.path

import datetime



# ALL APPELLATE DATA
## Extract items with a court abbreviation that is "CAFC" and has a terminated date.
## COL2 is "Court Abbreviation". COL26 is "Date Terminated
## File saved in data/Appellate/appellate_all.csv   Total : 1567 items
def all_appellate_data():
    # filings are too long, add this line to avoid error when reading the csv
    csv.field_size_limit(sys.maxsize)

    with open('data/step9_file.csv', 'rb') as csvfile:
        fulldata = csv.reader(csvfile)
        header = fulldata.next()

        count = 0

        # put the result file in to "data/Trial" directory
        if not os.path.isdir("data/Appellate"):
            os.mkdir("data/Appellate")

        with open("data/Appellate/appellate_all.csv", 'w') as resultfile:
            writer = csv.writer(resultfile)
            writer.writerow(header)

            for row in fulldata:
                if row[1] == "CAFC":
                    if row[25] != "":
                        count += 1
                        writer.writerow(row)

        print ["All appellate data : ", count]




def exploring_ap():
    # filings are too long, add this line to avoid error when reading the csv
    csv.field_size_limit(sys.maxsize)

    with open('data/Appellate/appellate_all.csv', 'rb') as csvfile:
        apdata = csv.reader(csvfile)
        header = apdata.next()

        count = 0
        nonopn = []


        countt = 0

        for row in apdata:
            # tdate = datetime.datetime.strptime(row[25], "%m/%d/%Y").date().strftime("%B %d, %Y")
            #
            # fdates = re.split("[\'\"],\su[\'\"]", row[27])
            # fdates[0] = fdates[0].replace("[u\'", "")
            # fdates[-1] = fdates[-1].replace("\']", "")
            #
            filings = re.split("[\'\"],\su[\'\"]", row[28])
            filings[0] = filings[0].replace("[u\'", "")
            filings[-1] = filings[-1].replace("\']", "")

            if "OPINION and JUDGMENT filed" not in row[28]:
                cond = ("terminated" in row[28]) or ("dismissed" in row[28]) \
                       or ("terminate" in row[28]) or ("dismiss" in row[28]) \
                       or ("Miscellaneous" in row[28]) or ("terminating" in row[28])
                nonopn.append(row[26] + "@" + str(len(filings)) + "@" + str(cond))

        nonopn = set(nonopn)

        res = []
        for url in nonopn:
            res.append(url.split("@"))
        ress = sorted(res, key=lambda url:int(url[1]))

        for url in ress:
            if url[2] == "False":
                print url


            # evtfilings = ""
            # for ind in range(len(filings)):
            #     if fdates[ind] == tdate:
            #         evtfilings += filings[ind] + "\n"
            # print row[26]
            # print tdate
            # print evtfilings
            # print " "


exploring_ap()