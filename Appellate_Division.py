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
        result = []

        keyword = "The judgment or decision is: "

        for row in apdata:
            tdate = datetime.datetime.strptime(row[25], "%m/%d/%Y").date().strftime("%B %-d, %Y")

            fdates = re.split("[\'\"],\su[\'\"]", row[27])
            fdates[0] = fdates[0].replace("[u\'", "")
            fdates[-1] = fdates[-1].replace("\']", "")

            filings = re.split("[\'\"],\su[\'\"]", row[28])
            filings[0] = filings[0].replace("[u\'", "")
            filings[-1] = filings[-1].replace("\']", "")



            # if "OPINION and JUDGMENT filed" in row[28]:
            #     for ind in range(len(filings)):
            #         filings[ind] = filings[ind].replace("The j decision is:", "The judgment or decision is:")
            #
            #         cond = ("OPINION and JUDGMENT filed" in filings[ind]) \
            #                and ("The judgment or decision is:" in filings[ind]) \
            #                and not ("This entry was made in error" in filings[ind])
            #
            #         if cond:
            #             count += 1
            #             judgement = filings[ind]
            #             findindex = judgement.find(keyword)
            #             resbegin = findindex + len(keyword)
            #             resend = judgement.find(".", resbegin, resbegin + 240)
            #             judgresult = judgement[int(resbegin):int(resend)]
            #
            #
            #
            #
            #             ##dates fdates[ind]
            #             # if tdate != fdates[ind]:
            #             #     print row[26]
            #             #     print judgresult
            #             #     print [tdate, fdates[ind]]
            #             #print judgement
            #             result.append(judgresult)



            if "OPINION and JUDGMENT filed" not in row[28]:
            #else:
                evtfilings = ""
                for ind in range(len(filings)):
                    if fdates[ind] == tdate:
                        evtfilings += filings[ind] + " | "

                cond = ("ORDER" in evtfilings) and (
                ("affirm" in evtfilings) or ("AFFIRM" in evtfilings) or ("Affirm" in evtfilings)
                or ("vacat" in evtfilings) or ("VACAT" in evtfilings) or ("Vacat" in evtfilings)
                or ("reverse" in evtfilings) or ("Reverse" in evtfilings) or (
                    "REVERSE" in evtfilings)
                or ("remand" in evtfilings) or ("Remand" in evtfilings) or ("REMAND" in evtfilings)) \
                       and not (("dismiss" in evtfilings) or ("terminat" in evtfilings))


                if cond :

                    ###dates  terminated date


                    #if "affirm" in evtfilings:
                    count += 1
                    evtfilings2 = ""
                    num = 0
                    for ind in range(len(fdates)):
                        if "ORDER" in filings[ind]:
                            num += 1
                            evtfilings2 += filings[ind] + " | "
                    print row[26]
                    print evtfilings2
                    print num

        print count















exploring_ap()