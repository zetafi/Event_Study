import csv

with open('test.csv', 'rb') as csvfile:
    test = csv.reader(csvfile)
    header = next(test)

    count = 0

    ltest = list(test)


    length = []
    for i in range(len(ltest)):
        #print '-1]' in ltest[i]
        if len(ltest[i]) == 5 and ltest[i][4] == ' -1]':
            #print "ltest " + str(i)
            a1 = ltest[i-1]
            a2 = ltest[i-2]
            a3 = ltest[i-3]
            a4 = ltest[i-4]
            if a1 != a3 or a2 != a4:
                print [i, ltest[i], a1, a2, a3, a4]


    print "Done!"