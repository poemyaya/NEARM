# -*- coding: utf-8 -*-
import json
import numpy as np
import re
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



def getRawTrain(attrs,type):
    alldatas = []
    for i in range(len(attrs)):
        attr = attrs[i]
        dictsubjname = reGetdictname('/home/ren/remote/ruleEval/'+attr+'/subjInfo.csv')
        dictobjname = reGetdictname('/home/ren/remote/ruleEval/'+attr+'/objInfo.csv')
        datas = readContent('/home/ren/remote/ruleMining/outdatas/'+type+'_'+attr+'.csv')
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
            ealldata.append(i)
            alldatas.append(ealldata)
    return alldatas

#-----------------------------

def readvec(url):
    dictworvec = {}
    read = open(url)
    lines = read.readlines()
    for line in lines:
        words = line.strip().split(' ')
        key = words[0]
        vec = words[1:]
        wordvec = []
        wordvec.extend([float(x) for x in vec])
        dictworvec[key] = wordvec
    return dictworvec

def reGetvec2(setsubobj,dicmodel):
    dictvec={}
    allnow=[]
    mark=-1
    for s in setsubobj:
        # print s
        # if s!='Janghwa-wanghu':
        #     continue
        # print '--',s
        wors = s.split(' ')
        if len(wors)>1:
            allnow_=[]
            dictword={}
            for word in wors:
                if word in dicmodel.keys():
                    dictword[word] = dicmodel[word]
                    allnow_.append(dictword[word])
                else:
                    newword = re.findall('[a-zA-Z]+',word)
                    if len(newword)==0:
                        dictword[word] = 'NAN'
                    else:
                        nw=[]
                        ks=0
                        for w in newword:
                            if w not in dicmodel.keys():
                                x=''
                                for i in newword:
                                    x=x+i
                                if x in dicmodel.keys():
                                    dictword[word] = dicmodel[x]
                                    allnow_.append(dictword[word])
                                else:
                                    x=x.lower()
                                    if x in dicmodel.keys():
                                        dictword[word] = dicmodel[x]
                                        allnow_.append(dictword[word])
                                    else:
                                        dictword[word] = dicmodel[x[0]]
                                        allnow_.append(dictword[word])
                                break
                            else:
                                ks+=1
                                nw.append(dicmodel[w])
                        if ks>0:
                            dictword[word] = np.mean(nw,axis=0).tolist()
                            allnow_.append(dictword[word])
            for k,v in dictword.items():
                if type(v)==list:
                    mark=1
                    break
                mark=0
            if mark == 1:
                for k,v in dictword.items():
                    if v=='NAN':
                        dictword[k] = np.mean(allnow_,axis=0).tolist()
                dictvec[s] = np.mean(allnow_, axis=0).tolist()
                allnow.append(dictvec[s])
            else:
                dictvec[s] = 'NULL'
        else:
            if s in dicmodel.keys():
                dictvec[s] = dicmodel[s]
                allnow.append(dictvec[s])
            else:
                news = re.findall('[a-zA-Z]+',s)
                # print '--',news
                if len(news)==0:
                    dictvec[s] = 'NULL'
                else:
                    nws=[]
                    kss=0
                    for w in news:
                        if w not in dicmodel.keys():
                            x=''
                            for i in news:
                                x=x+i
                            if x not in dicmodel.keys():
                                continue
                            dictvec[s] = dicmodel[x]
                            allnow.append(dictvec[s])
                            break
                        else:
                            kss+=1
                            nws.append(dicmodel[w])
                    if kss>0:
                        dictvec[s] = np.mean(nws,axis=0).tolist()
                        allnow.append(dictvec[s])
                    else:
                        dictvec[s] = 'NULL'
    return dictvec,allnow

def dictsubjobjvec(datas):
    vecurl = '/home/yangxi/project/vectors_word2vec_RLSW_131.txt'
    dicmodel = readvec(vecurl)
    allentity=[]
    for data in datas:
        subj = data[0]
        obj = data[1]
        allentity.append(subj)
        allentity.append(obj)

    setAllentity = list(set(allentity))
    if '' in setAllentity:
        setAllentity.remove('')
    dictentity,allnowentity = reGetvec2(setAllentity,dicmodel)

    entitynotin=0

    for k,v in dictentity.items():
        if v=='NULL':
            entitynotin += 1
            dictentity[k] = np.mean(allnowentity, axis=0).tolist()

    # print('%d subjects not all in word2vec,the number of subjects is %d.')%(entitynotin,len(setAllentity))
    return dictentity


if __name__=='__main__':
    attrs = ['spouse','song','mother','film','father','child','filmCastmember','songPerformer']
    rawtrain = getRawTrain(attrs, 'train')
    dictTrain = dictsubjobjvec(rawtrain)
    json.dump(dictTrain,open('dictsWords/dicttrain.json','w+'))
    rawtest = getRawTrain(attrs, 'test')
    dictTest = dictsubjobjvec(rawtest)
    json.dump(dictTest,open('dictsWords/dicttest.json','w+'))
