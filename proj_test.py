import csv
import datetime
import sys

# with open('test/A1_old.csv', 'rb') as csvfile:
#     test = csv.reader(csvfile)
#     header = next(test)
#
#     for row in test:
#         print row

## new 768    653/655    origin 8/44
# with open('test/A1_new.csv', 'rb') as csvfile:
#     test = csv.reader(csvfile)
#     header = next(test)
#     test = list(test)
#
#     ##  old 655
#    ## with open('test/A1_old.csv', 'rb') as csvfile2:
#
#     ##origin 44
#     with open('test/APP_origin.csv', 'rb') as csvfile2:
#         test2 = csv.reader(csvfile2)
#         header = next(test2)
#
#         count = 0
#
#         for row in test2:
#             for ind in range(len(test)):
#                 if row[0] == test[ind][0] and datetime.datetime.strptime(row[1], "%b %d,%Y").date().isoformat() == test[ind][1]:
#                     print row
#                     # print "\n"
#                     # print row
#                     # print test[ind]
#                     # print "\n"
#        #print count

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




#datetime.datetime.strptime(row[1], "%B %d, %Y").date().isoformat()


# ## Trial
# with open('data/Trial/trial_origin' + '.csv', 'rb') as csvfile:
#     data = csv.reader(csvfile)
#     header = next(data)
#
#     count = 0


    ##  41 items in trial_old

    # with open('data/Trial/T1_trial_all' + '.csv', 'rb') as csvfile2:
    #     data_new = csv.reader(csvfile2)
    #     header = next(data_new)
    #     data_new = list(data_new)
    #
    #
    #
    #
    #     for old in data:
    #         found = False
    #         for ind in range(len(data_new)):
    #             if data_new[ind][0] == old[0] and datetime.datetime.strptime(data_new[ind][1], "%B %d, %Y").date().isoformat() == datetime.datetime.strptime(old[1], "%b %d,%Y").date().isoformat():
    #                 found = True
    #
    #         if not found:
    #             print old
            ## 1641/1653 for week2 and T1
            ## T1 and paper t origin. 30/41






    #print count




## 1061 items
## 735 non dup
##
# with open('data/Trial/all_complete_trial' + '.csv', 'rb') as csvfile:
#     csv.field_size_limit(sys.maxsize)
#     data = csv.reader(csvfile)
#     header = next(data)
#
#     casen = []
#
#     for row in data:
#         casen.append(row[2])
#
#     newcasen = set(casen)
#
#     #file4_w2
#     ###5264
#     ##4013
#     ##93 in common
#
#
#
#     ### step7_file
#     ##1045
#     ##734
#     ## common 731
#     with open('data/Trial/step7_file' + '.csv', 'rb') as csvfile2:
#         data2 = csv.reader(csvfile2)
#         header = next(data2)
#
#         casen2 = []
#
#         for row in data2:
#             casen2.append(row[2])
#
#         print "old file"
#         print len(casen2)
#         newcasen2 = set(casen2)
#         print len(newcasen2)
#
#         #compare
#         print "compare"
#         count = 0
#         for item in newcasen2:
#             if item in newcasen:
#                 count += 1
#         print "common:"
#        print count
