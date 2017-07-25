import time
import requests
import re
import datetime
import math
import operator
import csv
import os
import random
from glob import glob
import bisect
import numpy as np



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
            return ["ERROR", error]



        # verify enough data for estimation
        if mid + begin < 0 or mid + end > len(prices) :
            errorlog = []
            errorlog.append(compCode)
            errorlog.append(eDate.date().isoformat())
            errorlog.append("[" + str(begin) + ", " + str(end) + ")")
            errorlog.append("Not enough price data for this duration")
            print errorlog
            error = "@".join(errorlog)
            return ["ERROR", error]


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
            return ["ERROR", error]


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
            return ["ERROR", error]

        #print [prices[mid+begin][0], prices[mid+end][0],begin,end]

        return estwin_rr

################################END Ratio calculator###################################################

#print len(stock_rr('YHOO', datetime.datetime(2010, 04, 29), -60, -30))

def factor_get(eDate, begin, end, type):
    with open('data/factors.csv', 'rb') as csvfile:
        factors = csv.reader(csvfile)
        header = next(factors)
        factors = list(factors)

        if type not in header:
            errorlog = []
            errorlog.append("FACTOR_ERROR")
            errorlog.append(eDate.date().isoformat())
            errorlog.append("[" + str(begin) + ", " + str(end) + ")")
            errorlog.append("type: " + type)
            errorlog.append(" type does not exist!")
            print errorlog
            error = "@".join(errorlog)
            return ["ERROR",error]

        ## binary search for the index of the event day
        low = 0
        high = len(factors) - 1
        mid = (low + high) / 2
        while (high - low) > 1:
            mid = (low + high) / 2
            if datetime.datetime.strptime(factors[mid][0].replace(",",""), "%Y%m%d") <= eDate:
                low = mid
            elif eDate < datetime.datetime.strptime(factors[mid][0].replace(",",""), "%Y%m%d"):
                high = mid
        mid = low
        ## end binary search , mid as the result index
        if eDate != datetime.datetime.strptime(factors[mid][0].replace(",",""), "%Y%m%d"):
            errorlog = []
            errorlog.append("FACTOR_ERROR")
            errorlog.append(eDate.date().isoformat())
            errorlog.append("[" + str(begin) + ", " + str(end) + ")")
            errorlog.append("TYPE: " + type)
            errorlog.append("the Event Date does not exist in the factor file")
            print errorlog
            error = "@".join(errorlog)
            return ["ERROR", error]

        if mid + begin < 0 or mid + end > len(factors) :
            errorlog = []
            errorlog.append("FACTOR_ERROR")
            errorlog.append(eDate.date().isoformat())
            errorlog.append("[" + str(begin) + ", " + str(end) + ")")
            errorlog.append("TYPE: " + type)
            errorlog.append("Not enough factors data for this duration")
            print errorlog
            error = "@".join(errorlog)
            return ["ERROR", error]

        #print [factors[mid+begin][0], factors[mid+end][0], begin, end]

        result_factor = []
        ntype = -1
        for t in range(4):
            if type == header[t]:
                ntype = t

        for i in range(begin+1, end):
            result_factor.append(float(factors[mid+i][ntype]))
        return result_factor


#print factor_get(datetime.datetime(2009, 1, 20), -60, -30, "HML")


#Fun3
################################Abnormal Return calculator###################################################
## Input: compCode, EventDate, EstWin start/end, EvtWin start/end
## return:[comp name, event date, car, car/sigma] if no error
## return list of length 5 with first one a string "ERROR_CASE"
def abnormalRe(compCode, eDate, estbegin, estend, evtbegin, evtend, bs) :

    #Estimation window rates
    estwin_rr = stock_rr(compCode, eDate, estbegin, estend)

    evtwin_rr = stock_rr(compCode, eDate, evtbegin, evtend)

    #SPY as SP500 rates
    spy_est_rr = stock_rr('SPY', eDate, estbegin, estend)

    spy_evt_rr = stock_rr('SPY', eDate, evtbegin, evtend)

    if estwin_rr[0] == "ERROR"  or evtwin_rr[0] == "ERROR" \
            or spy_est_rr[0] == "ERROR"  or spy_evt_rr[0] == "ERROR":

        errorinfo = []
        errorinfo.append("ERROR_CASE")

        if estwin_rr[0] == "ERROR":
            errorinfo.append(estwin_rr[1])
        else:
            errorinfo.append("No_problem")

        if evtwin_rr[0] == "ERROR":
            errorinfo.append(evtwin_rr[1])
        else:
            errorinfo.append("No_problem")

        if spy_est_rr[0] == "ERROR":
            errorinfo.append(spy_est_rr[1])
        else:
            errorinfo.append("No_problem")

        if spy_evt_rr[0] == "ERROR":
            errorinfo.append(spy_evt_rr[1])
        else:
            errorinfo.append("No_problem")

        return errorinfo

    # CAPM regression with spy_rates and estwin rates
    beta = sum(map(operator.mul, map(lambda i: i-sum(estwin_rr)/len(estwin_rr), estwin_rr), map(lambda i: i-sum(spy_est_rr)/len(spy_est_rr), spy_est_rr))) / sum(map(lambda i: i*i, map(lambda i: i-sum(spy_est_rr)/len(spy_est_rr), spy_est_rr)))
    alpha = sum(estwin_rr)/len(estwin_rr) - beta*sum(spy_est_rr)/len(spy_est_rr)

    # RSE
    res = (sum(map(lambda i:i*i, map(operator.sub, map(lambda i: i-alpha, estwin_rr), map(lambda i:i*beta, spy_est_rr)))) / (len(estwin_rr)-2))**0.5
    # AR
    ab_re = map(operator.sub, evtwin_rr, map(lambda i:i*beta+alpha, spy_evt_rr))
    # CAR/sigma
    ab_re_std = sum(ab_re) / (res * (evtend-evtbegin-1)**0.5 )



    # Bootstrap CAR calculation
    ar_est = map(operator.sub, map(lambda i: i - alpha, estwin_rr), map(lambda i: i * beta, spy_est_rr))
    car_mc = []
    pval = -1
    if bs:
        for bs in range(0, 100000):
            car = float(0)
            for count in range(0, evtend - evtbegin - 1):
                car += random.choice(ar_est)
            car_mc.append(car)
        car_mc.sort()

        pval = float(bisect.bisect_left(car_mc, sum(ab_re)))
        pval /= 100000

    return [compCode, eDate.date().isoformat(), sum(ab_re), ab_re_std, pval]
################################END_Abnormal Return calculator###################################################

def abnormal_return_mf(compCode, eDate, estbegin, estend, evtbegin, evtend):
    # Estimation window rates
    estwin_rr = stock_rr(compCode, eDate, estbegin, estend)

    evtwin_rr = stock_rr(compCode, eDate, evtbegin, evtend)

    # Rf   Rm-Rf   SMB    HML
    est_Rf = factor_get(eDate, estbegin, estend, "RF")
    est_Rm_Rf = factor_get(eDate, estbegin, estend, "Mkt-RF")
    est_SMB = factor_get(eDate, estbegin, estend, "SMB")
    est_HML = factor_get(eDate, estbegin, estend, "HML")

    evt_Rf = factor_get(eDate, evtbegin, evtend, "RF")
    evt_Rm_Rf = factor_get(eDate, evtbegin, evtend, "Mkt-RF")
    evt_SMB = factor_get(eDate, evtbegin, evtend, "SMB")
    evt_HML = factor_get(eDate, evtbegin, evtend, "HML")

    if estwin_rr[0] == "ERROR"  or evtwin_rr[0] == "ERROR" \
            or est_Rf[0] == "ERROR" or evt_Rf[0] == "ERROR" \
            or est_Rm_Rf[0] == "ERROR" or evt_Rm_Rf[0] == "ERROR" \
            or est_SMB[0] == "ERROR" or evt_SMB[0] == "ERROR" \
            or est_HML[0] == "ERROR" or evt_HML[0] == "ERROR":

        errorinfo = []
        errorinfo.append("ERROR_CASE")

        if estwin_rr[0] == "ERROR":
            errorinfo.append(estwin_rr[1])
        else:
            errorinfo.append("No_problem")

        if evtwin_rr[0] == "ERROR":
            errorinfo.append(evtwin_rr[1])
        else:
            errorinfo.append("No_problem")

        if est_Rf[0] == "ERROR":
            errorinfo.append(est_Rm_Rf[1])
        else:
            errorinfo.append("No_problem")

        if evt_Rf[0] == "ERROR":
            errorinfo.append(evt_Rm_Rf[1])
        else:
            errorinfo.append("No_problem")
        if est_Rm_Rf[0] == "ERROR":
            errorinfo.append(est_Rm_Rf[1])
        else:
            errorinfo.append("No_problem")

        if evt_Rm_Rf[0] == "ERROR":
            errorinfo.append(evt_Rm_Rf[1])
        else:
            errorinfo.append("No_problem")
        if est_SMB[0] == "ERROR":
            errorinfo.append(est_SMB[1])
        else:
            errorinfo.append("No_problem")

        if evt_SMB[0] == "ERROR":
            errorinfo.append(evt_SMB[1])
        else:
            errorinfo.append("No_problem")
        if est_HML[0] == "ERROR":
            errorinfo.append(est_HML[1])
        else:
            errorinfo.append("No_problem")

        if evt_HML[0] == "ERROR":
            errorinfo.append(evt_HML[1])
        else:
            errorinfo.append("No_problem")

        return errorinfo

    ## Multifactor model
    #print len(estwin_rr)
    #print len(est_Rf)
    #print compCode
    #print eDate
    Y = map(operator.sub, estwin_rr, est_Rf)
    X = [[1]*(estend-estbegin-1), est_Rm_Rf, est_SMB, est_HML]


    Y = np.matrix(Y).getT()
    X = np.matrix(X).getT()


    #print Y
    BETA = (((X.getT().dot(X)).getI()).dot(X.getT())).dot(Y)

    RES = Y - X.dot(BETA)


    # RSE
    SDRES = ((RES.getT().dot(RES))/(len(estwin_rr)-4))[0,0] ** 0.5

    # AR
    AB_RE = np.matrix(evtwin_rr).getT() - np.matrix(evt_Rf).getT() \
            - (np.matrix([[1]*(evtend-evtbegin-1), evt_Rm_Rf, evt_SMB, evt_HML]).getT()).dot(BETA)

    # CAR
    CAR = AB_RE.sum()
    # CAR/sigma
    AB_RE_STD = CAR / (SDRES * ((evtend - evtbegin-1) ** 0.5))

    return [compCode, eDate.date().isoformat(), CAR, AB_RE_STD]




#Fun4
################################CAR calculator###################################################
## Input: EstWin start/end, EvtWin start/end, filename
## Return:
def car_calculator(estWinl, estWinh, evtWinl, evtWinh, fpath, bs = False, mf = False):
    filename = fpath.replace("data/Trial/", "")
    filename = filename.replace("data/Appellate/", "")
    tableindex = filename.index("_")
    tblname = filename[:tableindex]
    tblnres = filename[tableindex:]
    direct = ""

    count = 0

    if tblname[0] == "T":
        direct = "Trial/"
    else:
        direct = "Appellate/"

    with open(fpath, 'rb') as csvfile:
        data = csv.reader(csvfile)
        header = next(data)

        if mf:
            if not os.path.isdir("data/Trial/MFCAR"):
                os.mkdir("data/Trial/MFCAR")
            with open("data/" + direct + "MFCAR/" + tblname + "_[" + str(evtWinl) + "," + str(evtWinh) + ")_EstWin" + str(
                    estWinl) + "," + str(estWinh) + tblnres, "w") as resultfile:
                writer = csv.writer(resultfile)
                writer.writerow([header[0], header[1], "MFCAR", "MFCAR/Sigma"])

                for row in data:
                    compCode = row[0]
                    eDate = datetime.datetime.strptime(row[1], "%B %d, %Y")

                    liste = abnormal_return_mf(compCode, eDate, estWinl, estWinh, evtWinl, evtWinh)
                    if liste[0] == "ERROR_CASE":
                        with open("data/" + direct + "MFCAR/ERROR_FILE_" + tblname + "_[" + str(evtWinl) + "," + str(
                                evtWinh) + ")_EstWin" + str(
                                estWinl) + "," + str(estWinh) + ".csv", "a") as errorfile:
                            errorwriter = csv.writer(errorfile)
                            for i in range(1, len(liste)):
                                if liste[i] != "No_problem":
                                    #print liste[i]
                                    errorwriter.writerow(liste[i].split("@"))
                    else:
                        count += 1
                        print liste
                        writer.writerow(liste)
            print ["MFCAR File:" + tblname, count]
        else:
            if not os.path.isdir("data/Trial/CAR"):
                os.mkdir("data/Trial/CAR")

            with open("data/" + direct + "CAR/" + tblname + "_[" + str(evtWinl) + "," + str(evtWinh) + ")_EstWin" + str(
                    estWinl) + "," + str(estWinh) + tblnres, "w") as resultfile:
                writer = csv.writer(resultfile)
                writer.writerow([header[0], header[1], "CAR", "CAR/Sigma", "Bootsratp p-value"])

                for row in data:
                    compCode = row[0]
                    eDate = datetime.datetime.strptime(row[1], "%B %d, %Y")

                    liste = abnormalRe(compCode, eDate, estWinl, estWinh, evtWinl, evtWinh, bs)
                    if liste[0] == "ERROR_CASE":
                        with open("data/" + direct + "CAR/ERROR_FILE_" + tblname + "_[" + str(evtWinl) + "," + str(
                                evtWinh) + ")_EstWin" + str(
                                estWinl) + "," + str(estWinh) + ".csv", "a") as errorfile:
                            errorwriter = csv.writer(errorfile)
                            for i in range(1, len(liste)):
                                if liste[i] != "No_problem":
                                    # print liste[i]
                                    errorwriter.writerow(liste[i].split("@"))
                    else:
                        count += 1
                        print liste
                        writer.writerow(liste)
            print "\n\n\n\n\n\n"
            print ["MFCAR File:" + tblname, count]
            print "\n\n\n\n\n\n"


################################END_CAR calculator###################################################

#car_calculator(-60, -30, -5, 0, glob('data/Trial/T1_*.csv')[0])
#print os.path.isfile(glob('data/Trial/TV2_*.csv')[0])



def CAR_total():
    estWinl = -60
    estWinh = -30
    extestWinl = -180
    extestWinh = -10
    evtWin1l = -5
    evtWin1h = 0
    evtWin2l = -2
    evtWin2h = 0
    evtWin3l = -2
    evtWin3h = 3
    evtWin4l = 0
    evtWin4h = 2

    t1path = glob('data/Trial/T1_*.csv')[0]
    t2path = glob('data/Trial/TV2_*.csv')[0]
    t3path = glob('data/Trial/TV3_*.csv')[0]
    t4path = glob('data/Trial/TV4_*.csv')[0]
    t5path = glob('data/Trial/T5_*.csv')[0]
    t6path = glob('data/Trial/TV6_*.csv')[0]
    t7path = glob('data/Trial/T7_*.csv')[0]
    t8path = glob('data/Trial/T8_*.csv')[0]
    t9path = glob('data/Trial/TV9_*.csv')[0]
    t10path = glob('data/Trial/TV10_*.csv')[0]

    a1path = glob('data/Appellate/A1_*.csv')[0]
    a2path = glob('data/Appellate/A2_*.csv')[0]
    a3path = glob('data/Appellate/A3_*.csv')[0]

    paths = [t1path, t2path, t3path, t4path, t5path, t6path, t7path, t8path, t9path, t10path, a1path, a2path, a3path]

    # ## normal estimation windows
    # for path in paths:
    #     car_calculator(estWinl, estWinh, evtWin1l, evtWin1h, path)
    #     car_calculator(estWinl, estWinh, evtWin2l, evtWin2h, path)
    #     car_calculator(estWinl, estWinh, evtWin3l, evtWin3h, path)
    #     car_calculator(estWinl, estWinh, evtWin4l, evtWin4h, path)
    #
    # ## extended estimation windows && Bootstrap CAR for extended windows
    # for path in paths:
    #     car_calculator(extestWinl, extestWinh, evtWin1l, evtWin1h, path, True)
    #     car_calculator(extestWinl, extestWinh, evtWin2l, evtWin2h, path, True)
    #     car_calculator(extestWinl, extestWinh, evtWin3l, evtWin3h, path, True)
    #     car_calculator(extestWinl, extestWinh, evtWin4l, evtWin4h, path, True)


    done = [t1path]

    ## Multifactor Model
    for path in paths:

        if path in done:
            pass
        else:
            car_calculator(estWinl, estWinh, evtWin1l, evtWin1h, path, True, True)

        car_calculator(estWinl, estWinh, evtWin2l, evtWin2h, path, True, True)
        car_calculator(estWinl, estWinh, evtWin3l, evtWin3h, path, True, True)
        car_calculator(estWinl, estWinh, evtWin4l, evtWin4h, path, True, True)


CAR_total()


#car_calculator(-60, -30, -2, 0, glob('data/Trial/T1_*.csv')[0], True, True)

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
    #car_calculation(estWinl, estWinh, resultfname)

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
