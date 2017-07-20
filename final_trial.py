import csv
import sys
import re

def get_trial_data():
    csv.field_size_limit(sys.maxsize)
    with open('data/step9_file.csv', 'rb') as csvfile:
        fulldata = csv.reader(csvfile)
        header = fulldata.next()

        with open("data/trial.csv", 'w') as trfile:
            write = csv.writer(trfile)
            write.writerow(header)

            for row in fulldata:
                if row[36] != "":
                    write.writerow(row)


def trial_consist():
    csv.field_size_limit(sys.maxsize)
    with open('data/trial.csv', 'rb') as csvfile:
        trdata = csv.reader(csvfile)
        header = trdata.next()

        count = 0

        with open("data/trial_consistent.csv", 'w') as trfile:
            write = csv.writer(trfile)
            write.writerow(header)

            for row in trdata:
                nbf = int(float(row[20]))
                numfdate = len(re.split("[\'\"],\su[\'\"]", row[27]))
                numfdes = len(re.split("[\'\"],\su[\'\"]", row[28]))

                if nbf == numfdate and numfdate == numfdes:
                    count += 1
                    write.writerow(row)
        print count


        # for row in trdata:
        #     if len(row[20]) > 6 or row[20] == "":
        #         print [row[26], row[20], row[27], row[28]]


def trial_consist_rem_consist():
    csv.field_size_limit(sys.maxsize)
    with open('data/trial_consistent.csv', 'rb') as csvfile:
        trdata = csv.reader(csvfile)
        header = trdata.next()

        count = 0



        for row in trdata:
            types = row[35].split("\', u\'")
            types[0] = types[0].replace("[u\'", "")
            types[-1] = types[-1].replace("\']", "")

            amounts = row[36].split("\', u\'")
            amounts[0] = amounts[0].replace("[u\'", "")
            amounts[-1] = amounts[-1].replace("\']", "")

            dates = row[37].split("\', u\'")
            dates[0] = dates[0].replace("[u\'", "")
            dates[-1] = dates[-1].replace("\']", "")

            if not (len(types) == len(amounts) and len(amounts) == len(dates)):
                print [len(types), len(amounts), len(dates)]




def trial_consist_datas():
    csv.field_size_limit(sys.maxsize)
    with open('data/trial_consistent.csv', 'rb') as csvfile:
        trdata = csv.reader(csvfile)
        header = trdata.next()

        count = 0

        results = []

        for row in trdata:
            types = row[35].split("\', u\'")
            types[0] = types[0].replace("[u\'", "")
            types[-1] = types[-1].replace("\']", "")

            amounts = row[36].split("\', u\'")
            amounts[0] = amounts[0].replace("[u\'", "")
            amounts[-1] = amounts[-1].replace("\']", "")

            dates = row[37].split("\', u\'")
            dates[0] = dates[0].replace("[u\'", "")
            dates[-1] = dates[-1].replace("\']", "")

            for i in range(0, len(types)):
                if amounts[i] != "N/A":
                    amounts[i] = amounts[i].replace("$", "")
                    amounts[i] = amounts[i].replace(",", "")
                    amounts[i] = int(float(amounts[i]))
                    if amounts[i]>100000:
                        results.append(row[8] + "|" + dates[i])

            # for date in dates:
            #     results.append(row[8] + "|" + date)

        finres = set(results)


        with open("data/trial_consistent_dates_100th.csv", 'w') as trfile:
            writer = csv.writer(trfile)
            writer.writerow(["CompCode", "Dates"])

            for ele in finres:
                writer.writerow(ele.split("|"))



def trial_inconsistent():
    csv.field_size_limit(sys.maxsize)
    with open('data/trial_inconsistent.csv', 'rb') as csvfile:
        trdata = csv.reader(csvfile)
        header = trdata.next()

        for row in trdata:

            print row[26]
            types = row[35].split("\', u\'")
            types[0] = types[0].replace("[u\'", "")
            types[-1] = types[-1].replace("\']", "")

            amounts = row[36].split("\', u\'")
            amounts[0] = amounts[0].replace("[u\'", "")
            amounts[-1] = amounts[-1].replace("\']", "")

            rdates = row[37].split("\', u\'")
            rdates[0] = rdates[0].replace("[u\'", "")
            rdates[-1] = rdates[-1].replace("\']", "")

            fdates = re.split("[\'\"],\su[\'\"]", row[27])
            filings = re.split("[\'\"],\su[\'\"]", row[28])

            fdates[0] = fdates[0].replace("[u\'", "")
            fdates[-1] = fdates[-1].replace("\']", "")

            filings[0] = filings[0].replace("[u\'", "")
            filings[-1] = filings[-1].replace("\']", "")

            for i in range(0, len(rdates)):
                print [types[i], amounts[i], rdates[i]]
                for j in range(0, len(fdates)):
                    if fdates[j] == rdates[i]:
                        print "      " + filings[j]

            print " "



trial_inconsistent()