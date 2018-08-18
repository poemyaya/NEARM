 # -*- coding: utf-8 -*-
import nltk
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
from numpy import array

def readContent(url):
    read = open(url)
    lines = read.readlines()
    data=[]
    for line in lines:
        line = line.rstrip("\r\n")
        line = line.rstrip("\n")
        line = line.strip()
        data.append(line)
    return data

#---------------------------------

def reGetdictname(url):
    read = open(url)
    lines = read.readlines()
    dictname = {}
    for line in lines:
        line = line.rstrip("\r\n")
        line = line.rstrip("\n")
        line = line.strip()
        l = line.split("\t")
        id = l[0]
        name = l[1]
        dictname[id] = name
    return dictname

def getRawTrain(attr,type):
    alldatas = []
    # for i in range(len(attrs)):
    #     attr = attrs[i]
    dictsubjname = reGetdictname('/home/ren/data/remote/ruleEval/'+attr+'/subjInfo.csv')
    dictobjname = reGetdictname('/home/ren/data/remote/ruleEval/'+attr+'/objInfo.csv')
    datas = readContent('/home/ydm/ren/remote/ruleMining2/outdatas_baseline/'+type+'_'+attr+'.csv')
    for pladata in datas:
        ealldata = []
        pladataword = pladata.split(' ')
        ks=0
        ko=0
        for word in pladataword:
            if (ks+ko) == 2:
                break
            if 'subjplace' in word:
                subjPlace = word
                ks=1
            if 'objplace' in word:
                objPlace = word
                ko=1

        subname = dictsubjname[subjPlace.split("_")[1]]
        objname = dictobjname[objPlace.split("_")[1]]

        ealldata.append(subname)
        ealldata.append(objname)
        ealldata.append(pladata)
        ealldata.append(subjPlace)
        ealldata.append(objPlace)
        alldatas.append(ealldata)
    return alldatas


