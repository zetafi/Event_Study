import csv
import sys
import re
import os.path

# ALL TRIAL DATA
## Extract items with a non null remedy value. COL37 is "remedies_amount".
## All items that has a remedy value are trial court cases
## File saved in data/Trial/all_complete_trial.csv   Total : 1061 items
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
            writer = csv.writer(resultfile)
            writer.writerow(header)

            for row in fulldata:
                if row[36] != "":
                    count += 1
                    writer.writerow(row)

            print ["All full trial data : ", count]


# T1 is the target table of all trial cases available.
## COL9 is "Stock_Ticker". COL38 is "remedies_date"
## The result file is in "data/Trial/T1_trial_all.csv"   Total: 1788 items
def T1_trial_all():
    # filings are too long, add this line to avoid error when reading the csv
    csv.field_size_limit(sys.maxsize)

    with open('data/Trial/all_complete_trial.csv', 'rb') as csvfile:
        fulltrdata = csv.reader(csvfile)
        header = fulltrdata.next()

        result = []

        for row in fulltrdata:
            dates = row[37].split("\', u\'")
            dates[0] = dates[0].replace("[u\'", "")
            dates[-1] = dates[-1].replace("\']", "")

            for date in dates:
                # combine ticker and date to a single string for convenience of comparison
                result.append(row[8] + "@" + date)

        # turn a list into set to eliminate duplication
        result = set(result)

        with open("data/Trial/T1_trial_all.csv", 'w') as resultfile:
            writer = csv.writer(resultfile)
            writer.writerow(["Stock_Ticker", "Decision_Date"])

            for elem in result:
                writer.writerow(elem.split("@"))
        print ["Trial calculable items : ", len(result)]



# ALL Beneficiary consistent data
## Extract all the items in "data/Trial/all_complete_trial.csv" that the company name is in Beneficiary or Against in the its remedies.
### result in "data/Trial/trial_bene_agnst_valid.csv"   510 valid cases    1402 valid remedy items
def trial_beneficiary_valid():
    # filings are too long, add this line to avoid error when reading the csv
    csv.field_size_limit(sys.maxsize)

    with open('data/Trial/all_complete_trial.csv', 'rb') as csvfile:
        fulltrdata = csv.reader(csvfile)
        header = fulltrdata.next()

        with open("data/Trial/trial_bene_agnst_valid.csv", 'w') as resultfile:
            writer = csv.writer(resultfile)
            writer.writerow(header)

            count = 0
            totalval = []

            for row in fulltrdata:
                ## the content is seperated by ', u' or ", u' or ', u" or ", u"
                benes = re.split("[\'\"],\su[\'\"]", row[34])
                ## remove the extra char from the first one and the last one
                benes[0] = benes[0].replace("[u\'", "")
                benes[-1] = benes[-1].replace("\']", "")

                nonbenes = re.split("[\'\"],\su[\'\"]", row[33])
                nonbenes[0] = nonbenes[0].replace("[u\'", "")
                nonbenes[-1] = nonbenes[-1].replace("\']", "")

                types = re.split("[\'\"],\su[\'\"]", row[35])
                types[0] = types[0].replace("[u\'", "")
                types[-1] = types[-1].replace("\']", "")

                amounts = row[36].split("\', u\'")
                amounts[0] = amounts[0].replace("[u\'", "")
                amounts[-1] = amounts[-1].replace("\']", "")

                dates = row[37].split("\', u\'")
                dates[0] = dates[0].replace("[u\'", "")
                dates[-1] = dates[-1].replace("\']", "")


                valitem = []
                for i in range(0, len(dates)):
                    if benes[i] == row[9] or nonbenes[i] == row[9]:
                        valitem.append(i)

                if len(valitem) == 0:
                    continue

                count += 1
                totalval.append(len(valitem))

                val_nonbenes = []
                val_benes = []
                val_types = []
                val_amounts = []
                val_dates = []

                for i in valitem:
                    val_nonbenes.append(nonbenes[i])
                    val_benes.append(benes[i])
                    val_types.append(types[i])
                    val_amounts.append(amounts[i])
                    val_dates.append(dates[i])

                row[33] = "@".join(val_nonbenes)
                row[34] = "@".join(val_benes)
                row[35] = "@".join(val_types)
                row[36] = "@".join(val_amounts)
                row[37] = "@".join(val_dates)

                writer.writerow(row)
            print ["Trial valid cases : ", count]
            print ["Trial valid remedy items : ", sum(totalval)]


# TV2&TV3&TV4
## TV2 is the target table of all company with benefit.TV3 is the target table of all company without benefit and only the one that match the item name would be considered.
## TV4 is the combination of TV2 and TV3
## COL9 is "Stock_Ticker". COL10 is "Company_Name" COL34 is "remedies_against". COL35 is "remedies_beneficiary". COL38 is "remedies_date"
## 472 items for beneficiary     305 items for non-beneficiary    763 items in total
def TV2_TV3_TV4_trial_benefit():
    # filings are too long, add this line to avoid error when reading the csv
    csv.field_size_limit(sys.maxsize)


    with open('data/Trial/trial_bene_agnst_valid.csv', 'rb') as csvfile:
        benetrdata = csv.reader(csvfile)
        header = benetrdata.next()

        resultbene = []
        resultnonbene = []

        for row in benetrdata:
            ## the content is seperated by "@"
            benes = row[34].split("@")
            nonbenes = row[33].split("@")
            dates = row[37].split("@")

            for i in range(0, len(dates)):
                if benes[i] == row[9]:
                    # combine ticker and date to a single string for convenience of comparison
                    resultbene.append(row[8] + "@" + dates[i])
                if nonbenes[i] == row[9]:
                    # combine ticker and date to a single string for convenience of comparison
                    resultnonbene.append(row[8] + "@" + dates[i])

        resultall = resultbene + resultnonbene

        # turn a list into set to eliminate duplication
        resultbene = set(resultbene)
        resultnonbene = set(resultnonbene)
        resultall = set(resultall)

        with open("data/Trial/TV2_trial_beneficiary.csv", 'w') as resultfile1:
            writer = csv.writer(resultfile1)
            writer.writerow(["Stock_Ticker", "Decision_Date"])

            for elem in resultbene:
                writer.writerow(elem.split("@"))

        with open("data/Trial/TV3_trial_non_beneficiary.csv", 'w') as resultfile2:
            writer = csv.writer(resultfile2)
            writer.writerow(["Stock_Ticker", "Decision_Date"])

            for elem in resultnonbene:
                writer.writerow(elem.split("@"))

        with open("data/Trial/TV4_trial_bene&nonbene.csv", 'w') as resultfile3:
            writer = csv.writer(resultfile3)
            writer.writerow(["Stock_Ticker", "Decision_Date"])

            for elem in resultall:
                writer.writerow(elem.split("@"))

        print ["Beneficiary cases : " , len(resultbene)]
        print ["Non-beneficiary cases : ", len(resultnonbene)]
        print ["Beneficiray + Non-beneficiary cases : ", len(resultall)]


# T5 is the table of all trial cases that remedy amount is greater than $100,000
## COL9 is "Stock_Ticker". COL37 is "remedies_amount" COL38 is "remedies_date"
## The result file is in "data/Trial/T5_trial_rem_100th.csv"   Total: 890 items
def T5_trial_100th():
    # filings are too long, add this line to avoid error when reading the csv
    csv.field_size_limit(sys.maxsize)

    with open('data/Trial/all_complete_trial.csv', 'rb') as csvfile:
        fulltrdata = csv.reader(csvfile)
        header = fulltrdata.next()

        result = []

        for row in fulltrdata:
            amounts = row[36].split("\', u\'")
            amounts[0] = amounts[0].replace("[u\'", "")
            amounts[-1] = amounts[-1].replace("\']", "")

            dates = row[37].split("\', u\'")
            dates[0] = dates[0].replace("[u\'", "")
            dates[-1] = dates[-1].replace("\']", "")

            for i in range(0, len(dates)):
                if amounts[i] != "N/A":
                    amounts[i] = amounts[i].replace("$", "")
                    amounts[i] = amounts[i].replace(",", "")
                    amounts[i] = int(float(amounts[i]))
                    if amounts[i] > 100000:
                        result.append(row[8] + "@" + dates[i])

        result = set(result)

        with open("data/Trial/T5_trial_rem_100th.csv", 'w') as resultfile:
            writer = csv.writer(resultfile)
            writer.writerow(["Stock_Ticker", "Decision_Date"])

            for elem in result:
                writer.writerow(elem.split("@"))

        print ["Trial remedy amount > $100,000 : ",len(result)]


# TV6 is the table of all benefit valid trial cases that remedy amount is greater than $100,000
## COL9 is "Stock_Ticker". COL10 is "Company_Name" COL34 is "remedies_against". COL35 is "remedies_beneficiary". COL37 is "remedies_amount". COL38 is "remedies_date"
## The result file is in "data/Trial/TV6_trial_valid_rem_100th.csv"   Total: 348 items
def TV6_trial_valid_100th():
    #filings are too long, add this line to avoid error when reading the csv
    csv.field_size_limit(sys.maxsize)

    with open('data/Trial/trial_bene_agnst_valid.csv', 'rb') as csvfile:
        benetrdata = csv.reader(csvfile)
        header = benetrdata.next()

        result = []
        for row in benetrdata:
            amounts = row[36].split("@")
            dates = row[37].split("@")

            for i in range(0, len(dates)):
                if amounts[i] != "N/A":
                    amounts[i] = amounts[i].replace("$", "")
                    amounts[i] = amounts[i].replace(",", "")
                    amounts[i] = int(float(amounts[i]))
                    if amounts[i] > 100000:
                        result.append(row[8] + "@" + dates[i])


        result = set(result)

        with open("data/Trial/TV6_trial_valid_rem_100th.csv", 'w') as resultfile:
            writer = csv.writer(resultfile)
            writer.writerow(["Stock_Ticker", "Decision_Date"])

            for elem in result:
                writer.writerow(elem.split("@"))

        print ["Trial valid remedy amount > $100,000 : ", len(result)]


# T7&T8 T7/T8 is the table of all trial cases that the remedy is decided by the jury/bench.
## COL9 is "Stock_Ticker". COL27 is "case url". COL28 is "filing_dates". COL29 is "filing_descriptions". COL38 is "remedies_date"
## The result file is in "data/Trial/T7_trial_jury.csv"   Total: 208(237) items
## The result file is in "data/Trial/T8_trial_bench.csv"   Total: 1411(1551) items
def T7_T8_trial_jury_bench():
    csv.field_size_limit(sys.maxsize)

    with open('data/Trial/all_complete_trial.csv', 'rb') as csvfile:
        fulltrdata = csv.reader(csvfile)
        header = fulltrdata.next()

        juryresult = []
        benchresult = []



        ######## exception cases
        url = "https://www.docketnavigator.com/detail/summary/case/"
        ids = ["13906", "4738", "4116", "29907", "31069", "33239"]
        urls = []
        for id in ids:
            urls.append(url+id)

        exceptjury = []
        exceptbench = []

        ## jury case 4738
        exceptjury += ["HPQ@October 5, 2010", "INTC@October 5, 2010", "IBM@October 5, 2010"]

        ## jury case 4116
        exceptjury += ["BXS@March 26, 2010", "BBT@March 26, 2010", "CFG@March 26, 2010",
                       "CMA@March 26, 2010", "CFR@March 26, 2010", "FDC@March 26, 2010",
                       "KEY@March 26, 2010", "MTB@March 26, 2010", "STI@March 26, 2010",
                       "USB@March 26, 2010", "WFC@March 26, 2010","ZION@March 26, 2010"]

        ## jury case 29907
        exceptjury += ["AAPL@November 21, 2013", "INTC@November 21, 2013", "IBM@November 21, 2013", "PHG@November 21, 2013",
                       "MSFT@November 21, 2013", "NOK@November 21, 2013"]

        ## jury case 33239
        exceptjury += ["AAPL@May 2, 2014", "AAPL@May 5, 2014", "INTC@May 2, 2014", "INTC@May 5, 2014",
                       "IBM@May 2, 2014", "IBM@May 5, 2014", "MSFT@May 2, 2014", "MSFT@May 5, 2014"]



        ## bench case 13906
        exceptbench += ["MU@May 8, 2013", "MU@March 21, 2012", "MU@January 11, 2012", "MU@March 8, 2010", "MU@March 10, 2009"]
        exceptbench += ["NVDA@May 8, 2013", "NVDA@March 21, 2012", "NVDA@January 11, 2012", "NVDA@March 8, 2010", "NVDA@March 10, 2009"]
        exceptbench += ["RMBS@May 8, 2013", "RMBS@March 21, 2012", "RMBS@January 11, 2012", "RMBS@March 8, 2010", "RMBS@March 10, 2009"]

        ## bench case 4738
        exceptbench += ["HPQ@November 7, 2013", "INTC@November 7, 2013", "IBM@November 7, 2013"]

        ## bench case 4116
        exceptbench += ["BXS@August 2, 2011", "BXS@August 3, 2011", "BXS@September 27, 2010", "BXS@September 11, 2009"]
        exceptbench += ["BAC@August 2, 2011", "BAC@August 3, 2011", "BAC@September 27, 2010", "BAC@March 26, 2010", "BAC@September 11, 2009"]
        exceptbench += ["BBT@August 2, 2011", "BXS@August 3, 2011", "BBT@September 27, 2010", "BBT@September 11, 2009"]
        exceptbench += ["CFG@August 2, 2011", "CFG@August 3, 2011", "CFG@September 27, 2010", "CFG@September 11, 2009"]
        exceptbench += ["CMA@August 2, 2011", "CMA@August 3, 2011", "CMA@September 27, 2010", "BXS@September 11, 2009"]
        exceptbench += ["CFR@August 2, 2011", "CFR@August 3, 2011", "CFR@September 27, 2010", "CFR@September 11, 2009"]
        exceptbench += ["FDC@August 2, 2011", "FDC@August 3, 2011", "FDC@September 27, 2010", "FDC@September 11, 2009"]
        exceptbench += ["KEY@August 2, 2011", "KEY@August 3, 2011", "KEY@September 27, 2010", "KEY@September 11, 2009"]
        exceptbench += ["MTB@August 2, 2011", "MTB@August 3, 2011", "MTB@September 27, 2010", "MTB@September 11, 2009"]
        exceptbench += ["STI@August 2, 2011", "STI@August 3, 2011", "STI@September 27, 2010", "STI@September 11, 2009"]
        exceptbench += ["USB@August 2, 2011", "USB@August 3, 2011", "USB@September 27, 2010", "USB@September 11, 2009"]
        exceptbench += ["WFC@August 2, 2011", "WFC@August 3, 2011", "WFC@September 27, 2010", "WFC@September 11, 2009"]
        exceptbench += ["ZION@August 2, 2011", "ZION@August 3, 2011", "ZION@September 27, 2010", "ZION@September 11, 2009"]

        ## bench case 29907
        exceptbench += ["AAPL@September 18, 2015", "AAPL@September 19, 2014", "AAPL@June 20, 2014", "AAPL@March 6, 2014"]
        exceptbench += ["AAPL@March 1, 2013", "AAPL@November 7, 2012", "AAPL@August 24, 2012", "AAPL@June 26, 2012"]
        exceptbench += ["INTC@September 18, 2015", "INTC@September 19, 2014", "INTC@June 20, 2014", "INTC@March 6, 2014"]
        exceptbench += ["INTC@March 1, 2013", "INTC@November 7, 2012", "INTC@August 24, 2012", "INTC@June 26, 2012"]
        exceptbench += ["IBM@September 18, 2015", "IBM@September 19, 2014", "IBM@June 20, 2014", "IBM@March 6, 2014"]
        exceptbench += ["IBM@March 1, 2013", "IBM@November 7, 2012", "IBM@August 24, 2012", "IBM@June 26, 2012"]
        exceptbench += ["PHGL@September 18, 2015", "PHG@September 19, 2014", "PHG@June 20, 2014", "PHG@March 6, 2014"]
        exceptbench += ["PHG@March 1, 2013", "PHG@November 7, 2012", "PHG@August 24, 2012", "PHG@June 26, 2012"]
        exceptbench += ["MSFT@September 18, 2015", "MSFT@September 19, 2014", "MSFT@June 20, 2014", "MSFT@March 6, 2014"]
        exceptbench += ["MSFT@March 1, 2013", "MSFT@November 7, 2012", "MSFT@August 24, 2012", "MSFT@June 26, 2012"]
        exceptbench += ["NOK@September 18, 2015", "NOK@September 19, 2014", "NOK@June 20, 2014", "NOK@March 6, 2014"]
        exceptbench += ["NOK@March 1, 2013", "NOK@November 7, 2012", "NOK@August 24, 2012", "NOK@June 26, 2012"]

        ## bench case 31069
        exceptbench += ["AMPH@May 9, 2016", "AMPH@October 28, 2011", "AMPH@October 21, 2011", "AMPH@October 7, 2011"]
        exceptbench += ["MNTA@May 9, 2016", "MNTA@October 28, 2011", "MNTA@October 21, 2011", "MNTA@October 7, 2011"]

        ## bench case 33239
        exceptbench += ["AAPL@June 23, 2017", "AAPL@January 18, 2016", "AAPL@August 20, 2015", "AAPL@November 25, 2014"]
        exceptbench += ["INTC@June 23, 2017", "INTC@January 18, 2016", "INTC@August 20, 2015", "INTC@November 25, 2014"]
        exceptbench += ["IBM@June 23, 2017", "IBM@January 18, 2016", "IBM@August 20, 2015", "IBM@November 25, 2014"]
        exceptbench += ["MSFT@June 23, 2017", "MSFT@January 18, 2016", "MSFT@August 20, 2015", "MSFT@November 25, 2014"]
        ######## exception cases



        for row in fulltrdata:
            if row[26] in urls:
                continue

            fdates = re.split("[\'\"],\su[\'\"]", row[27])
            fdates[0] = fdates[0].replace("[u\'", "")
            fdates[-1] = fdates[-1].replace("\']", "")

            filings = re.split("[\'\"],\su[\'\"]", row[28])
            filings[0] = filings[0].replace("[u\'", "")
            filings[-1] = filings[-1].replace("\']", "")

            rdates = row[37].split("\', u\'")
            rdates[0] = rdates[0].replace("[u\'", "")
            rdates[-1] = rdates[-1].replace("\']", "")

            for remi in range(len(rdates)):
                evtfilings = ""
                for f_ind in range(len(filings)):
                    if fdates[f_ind] == rdates[remi]:
                        evtfilings += filings[f_ind] + " | "

                cond = ("JURY VERDICT" in evtfilings) or ("JURY'S VERDICT" in evtfilings) \
                       or ("JUDGMENT BY JURY" in evtfilings) or ("JURY Verdict" in evtfilings) \
                       or ("Jury polled" in evtfilings) or ("JURY SPECIAL VERDICT" in evtfilings) \
                       or ("VERDICT OF THE JURY" in evtfilings) or ("(JURY) VERDICT" in evtfilings) \
                       or ("Jury Trial Proceedings" in evtfilings) or ("Jury Verdict -" in evtfilings) \
                       or ("Jury returns verdict" in evtfilings) or ("Jury's Special Verdict" in evtfilings) \
                       or ("Jury Notes" in evtfilings) or ("Judgment on the Jury's Verdict" in evtfilings)

                if cond:
                    juryresult.append(row[8] + "@" + rdates[remi])
                else:
                    benchresult.append(row[8] + "@" + rdates[remi])


        ## add exception cases
        juryresult += exceptjury
        benchresult += exceptbench


        juryresult = set(juryresult)
        benchresult = set(benchresult)

        with open("data/Trial/T7_trial_jury.csv", 'w') as resultfile1:
            writer = csv.writer(resultfile1)
            writer.writerow(["Stock_Ticker", "Decision_Date"])

            for elem in juryresult:
                writer.writerow(elem.split("@"))

        with open("data/Trial/T8_trial_bench.csv", 'w') as resultfile2:
            writer = csv.writer(resultfile2)
            writer.writerow(["Stock_Ticker", "Decision_Date"])

            for elem in benchresult:
                writer.writerow(elem.split("@"))

        print ["Trial jury decisions : ", len(juryresult)]
        print ["Trial bench decisions : ", len(benchresult)]




# TV9&TV10 TV9/TV10 is the table of all benefit valid trial cases that the remedy is decided by the jury/bench.
## COL9 is "Stock_Ticker". COL27 is "case url". COL28 is "filing_dates". COL29 is "filing_descriptions". COL38 is "remedies_date"
## The result file is in "data/Trial/TV9_trial_valid_jury.csv"   Total: 100(104) items
## The result file is in "data/Trial/TV10_trial_valid_bench.csv"   Total: 635(668) items
def TV9_TV10_trial_valid_jury():
    # filings are too long, add this line to avoid error when reading the csv
    csv.field_size_limit(sys.maxsize)

    with open('data/Trial/trial_bene_agnst_valid.csv', 'rb') as csvfile:
        benetrdata = csv.reader(csvfile)
        header = benetrdata.next()

        juryresult = []
        benchresult = []


        ######## exception
        url = "https://www.docketnavigator.com/detail/summary/case/"
        ids = ["13906", "29907", "31069", "33239"]
        urls = []
        for id in ids:
            urls.append(url + id)

        exceptjury = []
        exceptbench = []

        ## jury case 29907
        exceptjury += ["AAPL@November 21, 2013", "NOK@November 21, 2013"]

        ## jury case 33239
        exceptjury += ["AAPL@May 2, 2014", "AAPL@May 5, 2014"]


        ### bench case 13906
        exceptbench += ["RMBS@May 8, 2013", "RMBS@March 21, 2012", "RMBS@January 11, 2012", "RMBS@March 8, 2010", "RMBS@March 10, 2009"]

        ### bench case 29907
        exceptbench += ["AAPL@September 18, 2015", "AAPL@September 19, 2014", "AAPL@June 20, 2014", "AAPL@March 6, 2014"]
        exceptbench += ["AAPL@March 1, 2013", "AAPL@November 7, 2012", "AAPL@August 24, 2012", "AAPL@June 26, 2012"]
        exceptbench += ["NOK@September 18, 2015", "NOK@September 19, 2014", "NOK@June 20, 2014", "NOK@March 6, 2014"]
        exceptbench += ["NOK@March 1, 2013", "NOK@November 7, 2012", "NOK@August 24, 2012", "NOK@June 26, 2012"]

        ## bench case 31069
        exceptbench += ["AMPH@May 9, 2016", "AMPH@October 28, 2011", "AMPH@October 21, 2011", "AMPH@October 7, 2011"]
        exceptbench += ["MNTA@May 9, 2016", "MNTA@October 28, 2011", "MNTA@October 21, 2011", "MNTA@October 7, 2011"]

        ## bench case 33239
        exceptbench += ["AAPL@June 23, 2017", "AAPL@January 18, 2016", "AAPL@August 20, 2015", "AAPL@November 25, 2014"]
        ######## exception

        for row in benetrdata:
            if row[26] in urls:
                continue

            fdates = re.split("[\'\"],\su[\'\"]", row[27])
            fdates[0] = fdates[0].replace("[u\'", "")
            fdates[-1] = fdates[-1].replace("\']", "")

            filings = re.split("[\'\"],\su[\'\"]", row[28])
            filings[0] = filings[0].replace("[u\'", "")
            filings[-1] = filings[-1].replace("\']", "")

            rdates = row[37].split("@")



            for remi in range(len(rdates)):
                evtfilings = ""
                for f_ind in range(len(filings)):
                    if fdates[f_ind] == rdates[remi]:
                        evtfilings += filings[f_ind] + " | "

                cond = ("JURY VERDICT" in evtfilings) or ("JURY'S VERDICT" in evtfilings) \
                       or ("JUDGMENT BY JURY" in evtfilings) or ("JURY Verdict" in evtfilings) \
                       or ("Jury polled" in evtfilings) or ("JURY SPECIAL VERDICT" in evtfilings) \
                       or ("VERDICT OF THE JURY" in evtfilings) or ("(JURY) VERDICT" in evtfilings) \
                       or ("Jury Trial Proceedings" in evtfilings) or ("Jury Verdict -" in evtfilings) \
                       or ("Jury returns verdict" in evtfilings) or ("Jury's Special Verdict" in evtfilings) \
                       or ("Jury Note" in evtfilings) or ("Judgment on the Jury's Verdict" in evtfilings)

                if cond:
                    juryresult.append(row[8] + "@" + rdates[remi])
                else:
                    benchresult.append(row[8] + "@" + rdates[remi])

        juryresult += exceptjury
        benchresult += exceptbench

        juryresult = set(juryresult)
        benchresult = set(benchresult)


        with open("data/Trial/TV9_trial_valid_jury.csv", 'w') as resultfile1:
            writer = csv.writer(resultfile1)
            writer.writerow(["Stock_Ticker", "Decision_Date"])

            for elem in juryresult:
                writer.writerow(elem.split("@"))

        with open("data/Trial/TV10_trial_valid_bench.csv", 'w') as resultfile2:
            writer = csv.writer(resultfile2)
            writer.writerow(["Stock_Ticker", "Decision_Date"])

            for elem in benchresult:
                writer.writerow(elem.split("@"))

        print ["Trial valid jury decisions : ", len(juryresult)]
        print ["Trial valid bench decisions : ", len(benchresult)]


def main_trial():
    all_complete_trial_data()
    T1_trial_all()
    trial_beneficiary_valid()
    TV2_TV3_TV4_trial_benefit()
    T5_trial_100th()
    TV6_trial_valid_100th()
    T7_T8_trial_jury_bench()
    TV9_TV10_trial_valid_jury()
