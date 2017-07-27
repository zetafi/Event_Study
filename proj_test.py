import csv
import datetime

# with open('test/A1_old.csv', 'rb') as csvfile:
#     test = csv.reader(csvfile)
#     header = next(test)
#
#     for row in test:
#         print row


with open('test/A1_new.csv', 'rb') as csvfile:
    test = csv.reader(csvfile)
    header = next(test)


    with open('test/A1_old.csv', 'rb') as csvfile2:
        test2 = csv.reader(csvfile2)
        header = next(test2)
        oldresult = list(test2)

        count = 0

        for row in test:
            for nrow in oldresult:
                if row[0] == nrow[0] and row[1] == nrow[1]:
                    count += 1
                    print "\n"
                    print row
                    print nrow
                    print "\n"

        print count

        # tmpresult = []
        # for row in test:
        #     tmpresult.append(row[0] + "@" + row[1])
        # print len(tmpresult)
        # print len(set(tmpresult))


        # for row in test:
        #     row[1] = datetime.datetime.strptime(row[1], "%B %d, %Y").date().isoformat()
        #     if row in oldresult:
        #         print row
        #         count += 1
        # print count


