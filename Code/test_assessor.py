import json
import os
from get_key import get_client
from Assessor import Assessor, NoJustificationAssessor, ShortMemoryAssessor

def precision(tp,fp,tn,fn,label):
    if tp[label]+fp[label] == 0:
        return 0
    return tp[label]/(tp[label]+fp[label])

def recall(tp,fp,tn,fn,label):
    if tp[label]+fn[label] == 0:
        return 0
    return tp[label]/(tp[label]+fn[label])

def f1(tp,fp,tn,fn,label):
    p = precision(tp,fp,tn,fn,label)
    r = recall(tp,fp,tn,fn,label)
    if p+r == 0:
        return 0
    return (2*p*r)/(p+r)

def macro_average(tp,fp,tn,fn):
    n = len(tp)
    return sum([precision(tp,fp,tn,fn,label) for label in tp])/n

def micro_average(tp,fp,tn,fn):
    tp_sum = sum([tp[label] for label in tp])
    tp_sum = sum([tp[label] for label in tp])
    fp_sum = sum([fp[label] for label in fp])
    if tp_sum+fp_sum == 0:
        return 0
    return tp_sum/(tp_sum+fp_sum)

def weighted_average(tp,fp,tn,fn):
    support = true_positives = {"a":0,"b":0,"c":0,"d":0,"e":0,"f":0,"g":0,"h":0,"i":0,"j":0,"k":0,"l":0,"m":0}
    
    for label in tp:
        support[label] = tp[label]+fn[label]

    if sum([support[label] for label in tp]) == 0:
        return 0
    return sum([support[label]*f1(tp,fp,tn,fn,label) for label in tp])/sum([support[label] for label in tp])

def read_json_file(filename):
    with open(filename, 'r') as f:
        return json.load(f)
    
def compare_assessments(assessments_log,assessments_ref):
    true_positives = {"a":0,"b":0,"c":0,"d":0,"e":0,"f":0,"g":0,"h":0,"i":0,"j":0,"k":0,"l":0,"m":0}
    false_positives = {"a":0,"b":0,"c":0,"d":0,"e":0,"f":0,"g":0,"h":0,"i":0,"j":0,"k":0,"l":0,"m":0}
    true_negatives = {"a":0,"b":0,"c":0,"d":0,"e":0,"f":0,"g":0,"h":0,"i":0,"j":0,"k":0,"l":0,"m":0}
    false_negatives = {"a":0,"b":0,"c":0,"d":0,"e":0,"f":0,"g":0,"h":0,"i":0,"j":0,"k":0,"l":0,"m":0}

    for a_l,a_r in zip(assessments_log,assessments_ref):
        log = set(json.loads(a_l)['selection'])
        ref = set(json.loads(a_r)['selection'])


        for label in ["a","b","c","d","e","f","g","h","i","j","k","l","m"]:
            if label in log and label in ref:
                true_positives[label]+=1
            elif label in log and not (label in ref):
                false_positives[label]+=1
            elif (label not in log) and label in ref:
                false_negatives[label]+=1
            else:
                true_negatives[label]+=1

    return true_positives,false_positives,true_negatives,false_negatives

# TODO: choose which metrics to report + nice data visualisations
# IDEA: different versions of the intent selector can elecit different assessments! so you show that PF leads to more mistakes for ex!
# SHOWS THAT INTENTS WORK! DO IT PURELY DAATA ANALYSIS! + WRITE WRITE WRITE

def generate_assessment_file(assessor,dir,filename,suffix=""):
    assessments = []
    with open(dir + "/logs/" +  filename, 'r') as f:
        data = json.load(f)
    msg_tutor = data["tutor"]
    msg_student = data["student"]
    pb = data["pb"]
    sol = data["sol"]

    print(f'{dir}{suffix}/{filename}')

    for i in range(1,len(msg_tutor)):#SHOULD BE +1!!
        assessment = assessor.assess(pb,sol,msg_student[:i],msg_tutor[:i])
        assessments.append(assessment)
    
    with open(f'{dir}{suffix}/{filename}', 'w') as f:
        json.dump({"assessments":assessments},f,indent=4)
    return 

def testall(dir):
    for filename in os.listdir(dir + "/refs"):
        a = NoJustificationAssessor(get_client(), "myGPT4")
        b = ShortMemoryAssessor(get_client(), "myGPT4")
        c = Assessor(get_client(), "myGPT4")
        if filename.endswith(".json"):
            print("Working on:",filename)
            generate_assessment_file(a,dir,filename,suffix="/NOJUST")
            generate_assessment_file(b,dir,filename,suffix="/SHORT")
            generate_assessment_file(c,dir,filename,suffix="/FULL")
    return



########################################################

## once the assessments are generated ###
def compare_all(folder):
    avgs = []
    for version in ["FULL2","NOJUST2","SHORT"]:
        dir = f"{folder}{version}"

        assessments_log = []
        assessments_ref = []
        c=0
        for filename in os.listdir(dir):
            print(filename)
            #print("c = ",c)
            #a = Assessor(get_client(), "myGPT4")
            #print(dir + '/' + filename)
            #generate_assessment_file(dir + '/' + filename,a,"",c)
            data = read_json_file(dir + '/' + filename)["assessments"]
            print(len(data))
            assessments_log += data
            c+=1

        print("--")
        dir = f"{folder}refs"
        for filename in os.listdir(dir):
            data = read_json_file(dir + '/' + filename)["assessments"]
            print(len(data))
            assessments_ref += data


        tp,fp,tn,fn = compare_assessments(assessments_log,assessments_ref)

        with open(f'{version}_assessor_test.txt','w') as f:
            def printl(s):
                f.write(s + '\n')
                print(s)
            for label in 'abcdefghijklm':
                printl(label)
                printl(f"total: {tp[label]+fp[label]+tn[label]+fn[label]}")
                printl(f"true_positives: {tp[label]}")
                printl(f"false_positives: {fp[label]}")
                printl(f"true_negatives: {tn[label]}")
                printl(f"false_negatives: {fn[label]}")
                printl(f"precision: {precision(tp,fp,tn,fn,label)}")
                printl(f"recall: {recall(tp,fp,tn,fn,label)}")
                printl(f"f1: {f1(tp,fp,tn,fn,label)}")

            printl("")
            printl(f"macro_average: {macro_average(tp,fp,tn,fn)}")
            printl(f"micro_average: {micro_average(tp,fp,tn,fn)}")
            avg = weighted_average(tp,fp,tn,fn)
            avgs.append(avg)
            printl(f"weighted_average: {avg}") # change def of micro_average to get precison, recall or f1 micro averages. 
    print(avgs)



# 1. generate files
testall("../Assessor Datasets/")
# 2. compare files and generate reports
compare_all("../Assessor Datasets/")
