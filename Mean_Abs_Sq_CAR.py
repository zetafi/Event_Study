import csv
import random
from glob import glob
import scipy.stats as st
import os

#print 'data/Trial/CAR/T1_[-2,3)_EstWin-60,-30_trial_all.csv'.find(",", 18)

#print 2*st.norm.cdf(-abs(2.014))

def mean_CAR(filepath):
    startind = filepath.find("[")
    middleind = filepath.find(",", startind)
    endind = filepath.find(")", startind)

    evtWinl = int(filepath[(startind+1):middleind])
    evtWinh = int(filepath[(middleind+1):endind])


    with open(filepath, 'rb') as csvfile:
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

        result = [mean_cars, var_cars, mean_cars / var_cars**0.5, 2*st.norm.cdf(-abs(mean_cars / var_cars**0.5))]
        return result




def all_mean_CAR():
    t1 = "T1_"
    t2 = "TV2_"
    t3 = "TV3_"
    t4 = "TV4_"
    t5 = "T5_"
    t6 = "TV6_"
    t7 = "T7_"
    t8 = "T8_"
    t9 = "TV9_"
    t10 = "TV10_"
    a1 = "A1_"
    a2 = "A2_"
    a3 = "A3_"

    #all_table = [t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, a1, a2, a3]
    all_table = [a1,a2,a3]

    evtWin1 = "[-5,0)"
    evtWin2 = "[-2,0)"
    evtWin3 = "[-2,3)"
    evtWin4 = "[0,2)"

    all_evtWin = [evtWin1, evtWin2, evtWin3, evtWin4]

    estWin = "EstWin-60,-30_"
    extestWin = "EstWin-180,-10_"

    nCAR = "CAR/"
    multCAR = "MFCAR/"

    if not os.path.isdir("Result/"):
        os.mkdir("Result/")

    ### Standard estimation window mean CAR calculation
    print "\n\n\nBEGIN  Standard estimation window mCAR calculation\n\n\n"
    if not os.path.isdir("Result/StandardEstWin/"):
        os.mkdir("Result/StandardEstWin/")

    for t in all_table:
        print "\n\n Start_Standard: " + t + "\n\n"
        type = ""
        if "T" in t:
            type = "Trial/"
        else:
            type = "Appellate/"

        if not os.path.isdir("Result/StandardEstWin/" + t.replace("_", "") + "/"):
            os.mkdir("Result/StandardEstWin/" + t.replace("_", "") + "/")

        with open("Result/StandardEstWin/" + t.replace("_", "") + "/" + "Mean_CAR.csv", "w") as resultfile:
            writer = csv.writer(resultfile)
            writer.writerow(["Event_Window", "Mean_CAR", "Var(MCAR)", "z-stat", "p-value"])
            result = None

            for win in all_evtWin:
                filepath = glob("data/" + type + nCAR + t + win + "_" + estWin + "*.csv")[0]
                result = [win] + mean_CAR(filepath)
                writer.writerow(result)
        print "\n\n Finish_Standard: " + t + "\n\n"
    print "\n\n\nEND  Standard estimation window mCAR calculation\n\n\n"
    ### END Standard estimation window


    ### Extended Window mean CAR calculation
    print "\n\n\nBEGIN  Extended estimation window mCAR calculation\n\n\n"
    if not os.path.isdir("Result/ExtendedEstWin/"):
        os.mkdir("Result/ExtendedEstWin/")

    for t in all_table:
        print "\n\n Start_Ext: " + t + "\n\n"
        type = ""
        if "T" in t:
            type = "Trial/"
        else:
            type = "Appellate/"

        if not os.path.isdir("Result/ExtendedEstWin/" + t.replace("_", "") + "/"):
            os.mkdir("Result/ExtendedEstWin/" + t.replace("_", "") + "/")

        with open("Result/ExtendedEstWin/" + t.replace("_", "") + "/" + "Mean_CAR.csv", "w") as resultfile:
            writer = csv.writer(resultfile)
            writer.writerow(["Event_Window", "Mean_CAR", "Var(MCAR)", "z-stat", "p-value"])
            result = None

            for win in all_evtWin:
                filepath = glob("data/" + type + nCAR + t + win + "_" + extestWin + "*.csv")[0]
                result = [win] + mean_CAR(filepath)
                writer.writerow(result)
                print result
        print "\n\n Finish_Ext: " + t + "\n\n"
    print "\n\n\nEND  Extended estimation window mCAR calculation\n\n\n"
    ### END extended estimation window


    ### Multifactor(ExtEstWin) mean CAR calculation
    print "\n\n\nBEGIN  Multi-Factor mCAR calculation\n\n\n"

    if not os.path.isdir("Result/MultiFactor/"):
        os.mkdir("Result/MultiFactor/")
    for t in all_table:
        print "\n\n Start_Multi: " + t + "\n\n"
        type = ""
        if "T" in t:
            type = "Trial/"
        else:
            type = "Appellate/"

        if not os.path.isdir("Result/MultiFactor/" + t.replace("_", "") + "/"):
            os.mkdir("Result/MultiFactor/" + t.replace("_", "") + "/")

        with open("Result/MultiFactor/" + t.replace("_", "") + "/" + "Mean_CAR.csv", "w") as resultfile:
            writer = csv.writer(resultfile)
            writer.writerow(["Event_Window", "Mean_CAR", "Var(MCAR)", "z-stat", "p-value"])
            result = None

            for win in all_evtWin:
                filepath = glob("data/" + type + multCAR + t + win + "_" + estWin + "*.csv")[0]
                result = [win] + mean_CAR(filepath)
                writer.writerow(result)
                print result
        print "\n\n Finish_Multi: " + t + "\n\n"
    print "\n\n\nEND  Multi-Factor mCAR calculation\n\n\n"
    ### END MultiFactor estimation



#all_mean_CAR()




def mc_car(filepath, type):
    #estWinl, estWinh, evtWinl, evtWinh
    mcrep = 100000


    # startind = filepath.find("[")
    # middleind = filepath.find(",", startind)
    # endind = filepath.find(")", startind)
    #
    # evtWinl = int(filepath[(startind + 1):middleind])
    # evtWinh = int(filepath[(middleind + 1):endind])


    with open(filepath, 'rb') as csvfile:
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
            result = [abs_cars, mc_res[90000], mc_res[95000], mc_res[99000]]
            return result
        elif type == "sq":
            for i in range(0, mcrep):
                sq_car = float(0)
                for sd in sd_cars:
                    sq_car += random.gauss(0, sd)**2
                mc_res.append(sq_car)
            mc_res.sort()
            result = [sq_cars, mc_res[90000], mc_res[95000], mc_res[99000]]
            return result

#print mc_car("data/Trial/CAR/T1_[-5,0)_EstWin-60,-30_trial_all.csv","abs")



def all_abs_sq_CAR(type):
    t1 = "T1_"
    t2 = "TV2_"
    t3 = "TV3_"
    t4 = "TV4_"
    t5 = "T5_"
    t6 = "TV6_"
    t7 = "T7_"
    t8 = "T8_"
    t9 = "TV9_"
    t10 = "TV10_"
    a1 = "A1_"
    a2 = "A2_"
    a3 = "A3_"

    all_table = [t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, a1, a2, a3]

    # evtWin1 = "[-5,0)"
    # evtWin2 = "[-2,0)"
    # evtWin3 = "[-2,3)"
    # evtWin4 = "[0,2)"


    evtWin1 = "[-20,-10)"


    #all_evtWin = [evtWin1, evtWin2, evtWin3, evtWin4]
    all_evtWin = [evtWin1]

    estWin = "EstWin-60,-30_"
    extestWin = "EstWin-180,-10_"

    nCAR = "CAR/"
    multCAR = "MFCAR/"

    if not os.path.isdir("Result/"):
        os.mkdir("Result/")

    ### Standard estimation window abs/sqCAR calculation
    print "\n\n\nBEGIN  Standard estimation window "+type+"CAR calculation\n\n\n"
    if not os.path.isdir("Result/StandardEstWin/"):
        os.mkdir("Result/StandardEstWin/")

    ##TODO appellate error
    ap_table = [a1]
    for t in ap_table:
    #for t in all_table:
        print "\n\n Start_Standard: " + t + "\n\n"
        casetype = ""
        if "T" in t:
            casetype = "Trial/"
        else:
            casetype = "Appellate/"

        if not os.path.isdir("Result/StandardEstWin/" + t.replace("_", "") + "/"):
            os.mkdir("Result/StandardEstWin/" + t.replace("_", "") + "/")

        with open("Result/StandardEstWin/" + t.replace("_", "") + "/" + type + "_CAR.csv", "w") as resultfile:
            writer = csv.writer(resultfile)
            writer.writerow(["Event_Window", type + "_CAR", "90%", "95%", "99%"])
            result = None

            for win in all_evtWin:
                filepath = glob("data/" + casetype + nCAR + t + win + "_" + estWin + "*.csv")[0]
                result = [win] + mc_car(filepath, type)
                writer.writerow(result)
                print result
        print "\n\n Finish_Standard: " + t + "\n\n"
    print "\n\n\nEND  Standard estimation window " + type + "CAR calculation\n\n\n"
    ### END Standard estimation window



    # ### Extended estimation window abs/sqCAR calculation
    # print "\n\n\nBEGIN  Extended estimation window " + type + "CAR calculation\n\n\n"
    # if not os.path.isdir("Result/ExtendedEvtWin/"):
    #     os.mkdir("Result/ExtendedEvtWin/")
    #
    # for t in all_table:
    #     print "\n\n Start_Extended: " + t + "\n\n"
    #     casetype = ""
    #     if "T" in t:
    #         casetype = "Trial/"
    #     else:
    #         casetype = "Appellate/"
    #
    #     if not os.path.isdir("Result/ExtendedEstWin/" + t.replace("_", "") + "/"):
    #         os.mkdir("Result/ExtendedEstWin/" + t.replace("_", "") + "/")
    #
    #     with open("Result/ExtendedEstWin/" + t.replace("_", "") + "/" + type + "_CAR.csv", "w") as resultfile:
    #         writer = csv.writer(resultfile)
    #         writer.writerow(["Event_Window", type + "_CAR", "90%", "95%", "99%"])
    #         result = None
    #
    #         for win in all_evtWin:
    #             filepath = glob("data/" + casetype + nCAR + t + win + "_" + extestWin + "*.csv")[0]
    #             result = [win] + mc_car(filepath, type)
    #             writer.writerow(result)
    #     print "\n\n Finish_Extended: " + t + "\n\n"
    # print "\n\n\nEND  Extended estimation window " + type + "CAR calculation\n\n\n"
    # ### END Extended estimation window


    #
    # ### MultiFactor abs/sqCAR calculation
    # print "\n\n\nBEGIN  MultiFactor " + type + "CAR calculation\n\n\n"
    # if not os.path.isdir("Result/MultiFactor/"):
    #     os.mkdir("Result/MultiFactor/")
    #
    # for t in all_table:
    #     print "\n\n Start_MultiFactor: " + t + "\n\n"
    #     casetype = ""
    #     if "T" in t:
    #         casetype = "Trial/"
    #     else:
    #         casetype = "Appellate/"
    #
    #     if not os.path.isdir("Result/MultiFactor/" + t.replace("_", "") + "/"):
    #         os.mkdir("Result/MultiFactor/" + t.replace("_", "") + "/")
    #
    #     with open("Result/MultiFactor/" + t.replace("_", "") + "/" + type + "_CAR.csv", "w") as resultfile:
    #         writer = csv.writer(resultfile)
    #         writer.writerow(["Event_Window", type + "_CAR", "90%", "95%", "99%"])
    #         result = None
    #
    #         for win in all_evtWin:
    #             filepath = glob("data/" + casetype + multCAR + t + win + "_" + estWin + "*.csv")[0]
    #             result = [win] + mc_car(filepath, type)
    #             writer.writerow(result)
    #             print result
    #     print "\n\n Finish_MultiFactor: " + t + "\n\n"
    # print "\n\n\nEND  MultiFactor " + type + "CAR calculation\n\n\n"
    # ### END Standard estimation window



all_abs_sq_CAR("abs")

#all_abs_sq_CAR("sq")
