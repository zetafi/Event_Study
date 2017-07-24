import time
import requests
import re
import datetime
import math
import operator
import csv
import os
import random


#Fun1
################################prices requirer##############################################
## Input: ticker
## Return : True/False

## Dates
bDate = (1970, 1, 1)
startDate = (1998, 1, 1)
endDate = (2017, 5, 30)

def request_prices(ticker):
    try:
        print "try to get price : " + ticker
        r = requests.get('https://finance.yahoo.com/quote/aapl/history')
        time.sleep(5)
        txt = r.text
        cookie = r.cookies['B']
        pattern = re.compile('.*"CrumbStore":\{"crumb":"(?P<crumb>[^"]+)"\}')
        for line in txt.splitlines():
            m = pattern.match(line)
            if m is not None:
                crumb = m.groupdict()['crumb']

        ##solve \u002 situation in the crumb
        #print "before crumb is : " + crumb + "\n"

        ##replaced
        crumb = crumb.replace("\u002F", "/");
        #print "after crumb is : " + crumb + "\n"
        ####

        data = (ticker, int((datetime.datetime(*startDate) - datetime.datetime(*bDate)).total_seconds()),
                int((datetime.datetime(*endDate) - datetime.datetime(*bDate)).total_seconds()), crumb)
        url = "https://query1.finance.yahoo.com/v7/finance/download/{0}?period1={1}&period2={2}&interval=1d&events=history&crumb={3}".format(
            *data)
        data = requests.get(url, cookies={'B': cookie})
        data_file = open("data/prices/" + ticker + ".csv", "w")
        data_file.write(data.text)
        data_file.close()

        with open('data/prices/' + ticker + '.csv', 'rb') as csvfile:
            prices = csv.reader(csvfile)
            header = next(prices)
            if header[0] != "Date":
                print "fail to get the prices"
                return False
        print "got prices : " + ticker
        return True
    except:
        print "Another Attempt for " + ticker
        return False
################################ END prices requirer##############################################



#Fun2
################################Ratio calculator###################################################
## Input: compCode EventDate  EstimationWin start/end
## Output: list of ratio in EstWin if no error.
## Output: return a list of one string of the error information separated by @ if error occurs
def stock_rr(compCode, eDate, begin, end) :

    if not os.path.exists("data/prices/" + compCode + ".csv"):
        done = False
        while not done:
            done = request_prices(compCode)


    #Read estimation window data
    with open('data/prices/' + compCode + '.csv', 'rb') as csvfile :
        prices = csv.reader(csvfile)
        header = next(prices)
        prices = list(prices)


        ## binary search for the index of the event day
        low = 0
        high = len(prices) - 1
        mid = (low + high) / 2
        while (high - low) > 1 :
            mid = (low + high) / 2
            if datetime.datetime.strptime(prices[mid][0], "%Y-%m-%d") <= eDate :
                low = mid
            elif eDate < datetime.datetime.strptime(prices[mid][0], "%Y-%m-%d") :
                high = mid
        mid = low
        ## end binary search , mid as the result index



        ## If the event date is not in the price file return error informatino
        if eDate != datetime.datetime.strptime(prices[mid][0], "%Y-%m-%d"):
            ## stock_rr error information format [ticker, eDate, [Begin, end), error description]
            errorlog = []
            errorlog.append(compCode)
            errorlog.append(eDate.date().isoformat())
            errorlog.append("[" + str(begin) + ", " + str(end) + ")")
            errorlog.append("the Event Date does not exist in its price file")
            print errorlog
            error = "@".join(errorlog)
            return [error]



        # verify enough data for estimation
        if mid + begin < 0 or mid + end > len(prices) :
            errorlog = []
            errorlog.append(compCode)
            errorlog.append(eDate.date().isoformat())
            errorlog.append("[" + str(begin) + ", " + str(end) + ")")
            errorlog.append("Not enough price data for this duration")
            print errorlog
            error = "@".join(errorlog)
            return [error]



        ## retrieve the result estimation window
        estwin_price = []

        ## retrieve the adjusted close prices
        for i in range(begin, end) :
            if prices[mid + i][5] != "null":
                estwin_price.append(float(prices[mid + i][5]))
            else:
                estwin_price.append(0)

        pos0 = [i for i, x in enumerate(estwin_price) if x == 0]

        ## Return error if there are 0 prices in the duration
        if len(pos0) != 0:
            errorlog = []
            errorlog.append(compCode)
            errorlog.append(eDate.date().isoformat())
            errorlog.append("[" + str(begin) + ", " + str(end) + ")")

            errordes = ""
            for i in pos0:
                errordes += "Zero Price error, " + prices[mid + i + begin][0] + " price is : " + prices[mid + i + begin][5] + " | "
            errorlog.append(errordes)
            print errorlog
            error = "@".join(errorlog)
            return [error]

        #retrieve the return rate
        estwin_rr = []
        for i in range(1, len(estwin_price)) :
            estwin_rr.append(math.log(estwin_price[i]/estwin_price[i-1]))
            #  another algorithm : estwin_rr.append( (estwin_price[i] - estwin_price[i-1])/estwin_price[i-1] )


        ## Return error if the prices are constant in the duration
        if sum(estwin_rr)==0:
            errorlog = []
            errorlog.append(compCode)
            errorlog.append(eDate.date().isoformat())
            errorlog.append("[" + str(begin) + ", " + str(end) + ")")
            errorlog.append("Prices are constant in this duration, not useful")
            print errorlog
            error = "@".join(errorlog)
            return [error]

        return estwin_rr

################################END Ratio calculator###################################################

#print stock_rr('MMM', datetime.datetime(2009, 1, 20), -60, -30)

#Fun3
################################Abnormal Return calculator###################################################
## Input: compCode, EventDate, EstWin start/end, EvtWin start/end
## return:[comp name, event date, car, car/sigma] if no error
## return list of length 5 with first one a string "ERROR_CASE"
def abnormalRe(compCode, eDate, estbegin, estend, evtbegin, evtend) :

    #Estimation window rates
    estwin_rr = stock_rr(compCode, eDate, estbegin, estend)

    evtwin_rr = stock_rr(compCode, eDate, evtbegin, evtend)

    #SPY as SP500 rates
    spy_est_rr = stock_rr('SPY', eDate, estbegin, estend)

    spy_evt_rr = stock_rr('SPY', eDate, evtbegin, evtend)

    if len(estwin_rr) == 1 or len(evtwin_rr) == 1 or len(spy_est_rr) == 1 or len(spy_evt_rr) == 1:

        errorinfo = []
        errorinfo.append("ERROR_CASE")

        if len(estwin_rr) == 1:
            errorinfo.append(estwin_rr[0])
        else:
            errorinfo.append("No_problem")

        if len(evtwin_rr) == 1:
            errorinfo.append(evtwin_rr[0])
        else:
            errorinfo.append("No_problem")

        if len(spy_est_rr) == 1:
            errorinfo.append(spy_est_rr[0])
        else:
            errorinfo.append("No_problem")

        if len(spy_est_rr) == 1:
            errorinfo.append(spy_evt_rr[0])
        else:
            errorinfo.append("No_problem")

        return errorinfo

    #CAPM regression with spy_rates and estwin rates
    beta = sum(map(operator.mul, map(lambda i: i-sum(estwin_rr)/len(estwin_rr), estwin_rr), map(lambda i: i-sum(spy_est_rr)/len(spy_est_rr), spy_est_rr))) / sum(map(lambda i: i*i, map(lambda i: i-sum(spy_est_rr)/len(spy_est_rr), spy_est_rr)))
    alpha = sum(estwin_rr)/len(estwin_rr) - beta*sum(spy_est_rr)/len(spy_est_rr)

    #RSE
    res = (sum(map(lambda i:i*i, map(operator.sub, map(lambda i: i-alpha, estwin_rr), map(lambda i:i*beta, spy_est_rr)))) / (len(estwin_rr)-2))**0.5
    #AR
    ab_re = map(operator.sub, evtwin_rr, map(lambda i:i*beta+alpha, spy_evt_rr))
    #CAR/sigma
    ab_re_std = sum(ab_re) / (res * (evtend-evtbegin)**0.5 )

    return [compCode, eDate.date().isoformat(), sum(ab_re), ab_re_std]
################################END_Abnormal Return calculator###################################################

#abnormalRe("")


#Fun4
################################CAR calculator###################################################
## Input: EstWin start/end, EvtWin start/end, filename
## Return:
def car_calculation(estWinl, estWinh, evtWinl, evtWinh, fpath):
    filename = fpath.replace("Trial/", "")
    filename = filename.replace("Appellate/", "")
    tableindex = filename.index("_")
    tblname = filename[:tableindex]
    tblnres = filename[tableindex:]
    direct = ""

    if tblname[0] == "T":
        direct = "Trial/"
    else:
        direct = "Appellate/"

    with open("data/" + fpath + '.csv', 'rb') as csvfile:
        data = csv.reader(csvfile)
        header = next(data)

        if not os.path.isdir("data/Trial/CAR"):
            os.mkdir("data/Trial/CAR")

        with open("data/" + direct + "CAR/" + tblname + "_[" + str(evtWinl) + "," + str(evtWinh) + ")_EstWin" + str(estWinl) + "," + str(estWinh) + tblnres + ".csv", "w") as resultfile:
            writer = csv.writer(resultfile)
            writer.writerow([header[0], header[1], "CAR", "CAR/Sigma"])

            for row in data:
                compCode = row[0]
                eDate = datetime.datetime.strptime(row[1], "%B %d, %Y")

                liste = abnormalRe(compCode, eDate, estWinl, estWinh, evtWinl, evtWinh)
                if liste[0] == "ERROR_CASE":
                    with open("data/" + direct + "CAR/ERROR_FILE_" + tblname + "_[" + str(evtWinl) + "," + str(evtWinh) + ")_EstWin" + str(
                            estWinl) + "," + str(estWinh) + ".csv", "a") as errorfile:
                        errorwriter = csv.writer(errorfile)
                        for i in range(1,5):
                            if liste[i] != "No_problem":
                                #print len(liste[i])
                                errorwriter.writerow(liste[i].split("@"))
                else:
                    print liste
                    writer.writerow(liste)

################################END_CAR calculator###################################################

#car_calculation(-60, -30, -5, 0, "Trial/TV10_trial_valid_bench")




def mc_car(estWinl, estWinh, evtWinl, evtWinh, type):
    mcrep = 100000

    with open('data/result/cases_no_error' + "_EvtW" + str(evtWinl) + "to" + str(evtWinh) + "_EstW" + str(estWinl) + "to" + str(
            estWinh) + '.csv', 'rb') as csvfile:
        cars = csv.reader(csvfile)
        header = next(cars)


        sd_cars = []

        abs_cars = 0
        sq_cars = 0


        # retrieve sigma_i
        for row in cars:
            sd_cars.append(float(row[2]) / float(row[3]))
            abs_cars += abs(float(row[2]))
            sq_cars += float(row[2]) ** 2

        mc_res = []
        # normal distribution generator

        if type == "abs":
            for i in range(0, mcrep):
                abs_car = float(0)
                for sd in sd_cars:
                    abs_car += abs(random.gauss(0, sd))
                mc_res.append(abs_car)
            mc_res.sort()
            print ["abs_cars", "90%", "95%", "99%"]
            print [abs_cars, mc_res[90000], mc_res[95000], mc_res[99000]]
            print "\n"
        elif type == "sq":
            for i in range(0, mcrep):
                sq_car = float(0)
                for sd in sd_cars:
                    sq_car += random.gauss(0, sd)**2
                mc_res.append(sq_car)
            mc_res.sort()
            print ["sq_cars", "90%", "95%", "99%"]
            print [sq_cars, mc_res[90000], mc_res[95000], mc_res[99000]]
            print "\n"





def main_process(estWinl, estWinh, resultfname):
    car_calculation(estWinl, estWinh, resultfname)

    ##for four event window
    evtWinl = -5
    evtWinh = 0



    ############mean car
    with open('data/result/cases_no_error' + "_EvtW" + str(evtWinl) + "to" + str(evtWinh) + "_EstW" + str(estWinl) + "to" + str(
            estWinh) + '.csv', 'rb') as csvfile:
        cars = csv.reader(csvfile)
        header = next(cars)
        cars = list(cars)

        mean_cars = 0
        var_cars = 0

        for row in cars:
            mean_cars += float(row[2])
            var_cars += pow(float(row[2]) / float(row[3]), 2) / (evtWinh - evtWinl)

        mean_cars /= len(cars)
        var_cars /= len(cars) * len(cars)
        print "mean car "
        print "mean car | V(mean car) | z-stat"
        print [mean_cars, var_cars, mean_cars / var_cars**0.5]
        print "\n"


    ########|CAR| and CAR^2
    mc_car(estWinl, estWinh, evtWinl, evtWinh, "abs")
    mc_car(estWinl, estWinh, evtWinl, evtWinh, "sq")




#main_process(-60,-30,-5,0,"trial_consistent_dates")

#main_process(-60,-30,-5,0,"trial_consistent_dates_100th")
