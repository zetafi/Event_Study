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
##input: ticker
##return : True/False

##Dates
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

        # just skip
        # if(crumb.find("\u002F")!=-1):
        #     continue

        ##replaced
        crumb = crumb.replace("\u002F", "/");
        #print "after crumb is : " + crumb + "\n"
        ##final solution
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
##input: compCode EventDate  EstimationWin start/end
##output: list of ratio in EstWin
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
        low = 1
        high = len(prices) - 1
        mid = (low + high) / 2
        while low <= high :
            mid = (low + high) / 2
            if datetime.datetime.strptime(prices[mid][0], "%Y-%m-%d") < eDate :
                low = mid + 1
            elif eDate < datetime.datetime.strptime(prices[mid][0], "%Y-%m-%d") :
                high = mid - 1
            else :
                break
        ## end binary search , mid as the result index

        if eDate != datetime.datetime.strptime(prices[mid][0], "%Y-%m-%d"):
            with open('data/cases_error_log' + '.csv', 'a') as logfile:
                logs = csv.writer(logfile)
                logs.writerow([compCode, eDate.date().isoformat(), "stock_rr_error" , "between: " + str(begin) + " - " + str(end) + ". Event date: " + eDate.date().isoformat() + " does not exist in price file"])
                print "LOG===stkr===" + eDate.date().isoformat() + " for " + compCode + " does not exist in its price file"
            return []



        ## retrieve the result estimation window
        estwin_price = []
        # verify enough data for estimation
        if mid + begin < 1 or mid + end > len(prices) :
            with open('data/cases_error_log' + '.csv', 'a') as logfile:
                logs = csv.writer(logfile)
                logs.writerow([compCode, eDate.date().isoformat(), "stock_rr_error", "between: " + str(begin) + " - " + str(end) + " not enough data"])
                print "LOG===stkr=== not enough data for company " + compCode + " on event :" + eDate.date().isoformat() + " Win: " + str(begin) + " - " + str(end)
            return []
        # end verification


        #retrieve the adjusted close prices
        for i in range(begin-1, end) :
            if prices[mid + i][5] != "null":
                estwin_price.append(float(prices[mid + i][5]))
            else:
                estwin_price.append(0)

        pos0 = [i for i, x in enumerate(estwin_price) if x == 0]

        if len(pos0) != 0:
            for i in pos0:
                with open('data/cases_error_log' + '.csv', 'a') as logfile:
                    logs = csv.writer(logfile)
                    logs.writerow([compCode, eDate.date().isoformat(), "stock_rr_error","between: " + str(begin) + " - " + str(end) + prices[mid + i + begin - 1 ][0] + " price is null"])
                    print "LOG===stkr===" + compCode +" " + eDate.date().isoformat() +" between: " + str(begin) + " - " + str(end) + prices[mid + i + begin - 1 ][0] + " price is null"
            return []

        #retrieve the return rate
        estwin_rr = []
        for i in range(1, len(estwin_price)) :
            estwin_rr.append(math.log(estwin_price[i]/estwin_price[i-1]))
            #estwin_rr.append( (estwin_price[i] - estwin_price[i-1])/estwin_price[i-1] )

        if sum(estwin_rr)==0:
            with open('data/cases_error_log' + '.csv', 'a') as logfile:
                logs = csv.writer(logfile)
                logs.writerow([compCode, eDate.date().isoformat(), "stock_rr_error", "between: " + str(begin) + " - " + str(end) + " price constant changes in the period" ])
                print "LOG===stkr===" + compCode +" " + eDate.date().isoformat() +" between: " + str(begin) + " - " + str(end) + " price constant, not useful"
                return []

        return estwin_rr

################################END Ratio calculator###################################################

#Fun3
################################Abnormal Return calculator###################################################
##input: compCode, EventDate, EstWin start/end, EvtWin start/end
##return:[comp name, event date, car, car/sigma]
def abnormalRe(compCode, eDate, estbegin, estend, evtbegin, evtend) :

    #Estimation window rates
    estwin_rr = stock_rr(compCode, eDate, estbegin, estend)

    evtwin_rr = stock_rr(compCode, eDate, evtbegin, evtend)
    #SPY as SP500 rates
    spy_rr = stock_rr('SPY', eDate, estbegin, estend)

    if len(estwin_rr)==0 or len(evtwin_rr)==0 :
        return ["Error case", compCode, eDate.date().isoformat(), 0, 0]

    #CAPM regression with spy_rates and estwin rates
    beta = sum(map(operator.mul, map(lambda i: i-sum(estwin_rr)/len(estwin_rr), estwin_rr), map(lambda i: i-sum(spy_rr)/len(spy_rr), spy_rr))) / sum(map(lambda i: i*i, map(lambda i: i-sum(spy_rr)/len(spy_rr), spy_rr)))
    alpha = sum(estwin_rr)/len(estwin_rr) - beta*sum(spy_rr)/len(spy_rr)

    #RSE
    res = (sum(map(lambda i:i*i, map(operator.sub, map(lambda i: i-alpha, estwin_rr), map(lambda i:i*beta, spy_rr)))) / (len(estwin_rr)-2))**0.5
    #AR
    ab_re = map(operator.sub, evtwin_rr, map(lambda i:i*beta+alpha, stock_rr('SPY', eDate, evtbegin, evtend)))
    #CAR/sigma
    ab_re_std = sum(ab_re) / (res * (evtend-evtbegin)**0.5 )

    #print (-0.021/-0.85)/pow(5,0.5)
    #print stock_rr('SPY', eDate, evtbegin, evtend)

    return [compCode, eDate.date().isoformat(), sum(ab_re), ab_re_std]
################################END_Abnormal Return calculator###################################################



#Fun4
################################CAR calculator###################################################
##input: EstWin start/end, EvtWin start/end, filename
##return:filename+_EvtW**to**_EstW**to**
def car_calculation(estWinl, estWinh, evtWinl, evtWinh, resultfname):
    with open('data/' + resultfname + '.csv', 'rb') as csvfile:
        data = csv.reader(csvfile)
        header = next(data)

        with open("data/" + resultfname + "_EvtW" + str(evtWinl) + "to" + str(evtWinh) + "_EstW" + str(
                estWinl) + "to" + str(estWinh) + ".csv", "w") as resultfile:
            writer = csv.writer(resultfile)
            writer.writerow([header[0], header[1], "CAR", "CAR/Sigma"])

            for row in data:
                compCode = row[0]
                eDate = datetime.datetime.strptime(row[1], "%B %d, %Y")

                liste = abnormalRe(compCode, eDate, estWinl, estWinh, evtWinl, evtWinh)
                print liste
                writer.writerow(liste)
################################END_CAR calculator###################################################


def clean_error(estWinl, estWinh, evtWinl, evtWinh, resultfname):
    with open('data/' + resultfname + "_EvtW" + str(evtWinl) + "to" + str(evtWinh) + "_EstW" + str(estWinl) + "to" + str(
            estWinh) + '.csv', 'rb') as csvfile:
        cars = csv.reader(csvfile)

        for row in cars:
            if row[0] == "Error case":
                with open("data/result/cases_error" + "_EvtW" + str(evtWinl) + "to" + str(evtWinh) + "_EstW" + str(
                        estWinl) + "to" + str(estWinh) + ".csv", "a") as resultfile:
                    writer = csv.writer(resultfile)
                    writer.writerow(row)
            else:
                with open("data/result/cases_no_error" + "_EvtW" + str(evtWinl) + "to" + str(evtWinh) + "_EstW" + str(
                        estWinl) + "to" + str(estWinh) + ".csv", "a") as resultfile:
                    writer = csv.writer(resultfile)
                    writer.writerow(row)





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





def main_process(estWinl, estWinh, evtWinl, evtWinh, resultfname):
    car_calculation(estWinl, estWinh, evtWinl, evtWinh, resultfname)
    clean_error(estWinl, estWinh, evtWinl, evtWinh, resultfname)

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

main_process(-60,-30,-5,0,"trial_consistent_dates_100th")


#car_calculation(-60, -30, -5, 0, "APP")
#clean_error(-60, -30, -5, 0, "APP")
#main_process(-60,-30,-5,0,"apt_opt_final", "APP")

