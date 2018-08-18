# -*- coding: utf-8 -*-
import re
import math
import numpy as np
def delNum(sent):
    number = re.findall(r'(\w*[0-9]+\w*)', sent)
    for num in number:
        if num != '' and 'subjplace' not in num and 'objplace' not in num:
            if ' '+num in sent:
                sent = sent.replace(' '+num, ' numberplaceholder')
            elif num+' ' in sent:
                sent = sent.replace(num+' ', 'numberplaceholder ')
    sent = sent.strip()
    return sent

def reTemplate(data):
    _templateitem=[]
    totalWords = 0
    # 每个簇
    wordDict = {}
    for da in data:
        da = delNum(da)
        da = re.sub('[’!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~]+','',da)
        da = da.split(" ")
        ks=0
        ko=0
        for word in da:
            if (ks+ko) == 2:
                break
            if 'subjplace' in word:
                subjPlace = word
                ks=1
            if 'objplace' in word:
                objPlace = word
                ko=1
        sindex = da.index(subjPlace)
        oindex = da.index(objPlace)
        dis = (sindex-oindex)*1.0/-2
        for i in range(len(da)):
            wo = da[i]
            if len(wo)!=0 and  'subjplace' not in wo and 'objplace' not in wo:
                totalWords += 1
                loc = (i - sindex)*1.0/dis-1
                if wo in wordDict:
                    wordDict[wo].append(loc)
                else:
                    wordDict[wo]=[loc]
    #templateitem [word,[loc],mu,sig,fre]
    for setList in wordDict.keys():
        templateitem=[]
        tr = np.array(wordDict[setList])
        freqWord = len(tr)*1.0/totalWords
        if len(tr) < 3:
            templateitem.append(setList)
            templateitem.append(tr)
            templateitem.append('!!!')
            templateitem.append(freqWord)
        else:
            u = np.mean(tr)
            sig = math.sqrt(np.var(tr))
            if sig < 0.000000001:
                templateitem.append(setList)
                templateitem.append(tr)
                templateitem.append('!!!')
                templateitem.append(freqWord)
            else:
                templateitem.append(setList)
                templateitem.append(tr)
                templateitem.append(u)
                templateitem.append(sig)
                templateitem.append(freqWord)
        _templateitem.append(templateitem)

    data = []
    clus = []
    for pp in _templateitem:
        if '!!!' not in pp:
            data.append(pp)
    b = sorted(data, key=lambda x: x[-1], reverse=True)
    # clus = b
    if len(b)>20:
        clus.extend(b[:20])
    else:
        clus.extend(b)
    clus_dict={}
    for word in range(len(clus)):
        if '!!!' not in clus[word]:
            # clus_dict.setdefault(clus[word][0], []).append(word)
            clus_dict[clus[word][0]] = [clus[word][1]]# location list
            clus_dict[clus[word][0]] .append(clus[word][2])#mu
            clus_dict[clus[word][0]] .append(clus[word][3])#sigma
            clus_dict[clus[word][0]] .append(clus[word][4])#freq
    return clus_dict



def chooseWordSegment(sent,subjPlace, objPlace):
    s = re.sub('[’!"#$%&\'()*+,-./:;<=>?@[\\]^`{|}~]+','',sent)
    s = s.replace('  ',' ')
    ls = s.split(' ')
    sindex = ls.index(subjPlace)
    oindex = ls.index(objPlace)
    dis = (sindex-oindex)*1.0/-2
    head = 0
    tail = 0
    if sindex<oindex:
        head = sindex -3
        if head<0:
            head = 0
        tail = oindex + 3
        if tail>len(ls)-1:
            tail = len(ls)-1
    else:
        head = sindex + 3
        if head > len(ls)-1:
            head = len(ls)-1
        tail = oindex - 3
        if tail < 0:
            tail = 0
    if head>tail:
        indexlits = [i for i in range(tail,head+1)]
    else:
        indexlits = [i for i in range(head,tail+1)]
    indexsWord = [(j - sindex)*1.0/dis-1 for j in indexlits]
    cutSen = [ls[i] for i in indexlits]
    return cutSen,indexsWord

def getSimilarity(words, locs, bod):
    sim = 0
    for idx, word in enumerate(words):
        if word not in bod:
            continue
        loc = locs[idx]
        unit = 0.5 / len(words)
        locb = loc - unit
        loce = loc + unit
        mean = bod[word][1]
        std = bod[word][2]
        sim += bod[word][3] * (normcdf(mean,std,loce) - normcdf(mean,std,locb))
    return sim

def normcdf(mean, std, x):
    return (1.0 + math.erf(((x-mean)/std) / math.sqrt(2.0))) / 2.0

def reModel(sent,template_20,subjPlace,objPlace):
    marchDe = {}
    for i_cluster in template_20.keys():
        cluster = template_20[i_cluster]
        cutSen,indexsWord = chooseWordSegment(sent,subjPlace,objPlace)
        marchDe[i_cluster] = getSimilarity(cutSen, indexsWord, cluster)

    sortmarchDe = sorted(marchDe.items(),key=lambda dict:dict[1],reverse=True)
    marchvalue,marchIndex = sortmarchDe[0][1],sortmarchDe[0][0]

    return marchvalue,marchIndex

def reSentsMarch(sentslist,templateroot,template1,template2):
    reSentmatchListRoot = []
    reSentmatchDict1 = {}
    reSentmatchDict2 = {}
    for sent in sentslist:
        sent = delNum(sent)
        ks=0
        ko=0
        for word in sent.split(' '):
            if (ks+ko) == 2:
                break
            if 'subjplace' in word:
                subjPlace = word
                ks=1
            if 'objplace' in word:
                objPlace = word
                ko=1
        marchvalueROOT,marchIndeROOT = reModel(sent,templateroot,subjPlace, objPlace)
        if marchvalueROOT > 0:
            reSentmatchListRoot.append(sent)
        marchvalue1, marchIndex1 = reModel(sent, template1, subjPlace, objPlace)
        if marchvalue1 > 0:
            if marchIndex1 not in reSentmatchDict1.keys():
                reSentmatchDict1[marchIndex1] = [sent]
            else:
                reSentmatchDict1[marchIndex1].append(sent)

        allmarch2 = []
        for key in template2.keys():
            sencondT = template2[key]
            marchvalue_2, marchIndex_2 = reModel(sent, sencondT, subjPlace, objPlace)
            allmarch2.append((marchvalue_2, key,marchIndex_2))
        sortAllmarch2 = sorted(allmarch2,key=lambda dict:dict[0],reverse=True)
        marchvalue2, marchIndex_1,marchIndex2 = sortAllmarch2[0][0],sortAllmarch2[0][1],sortAllmarch2[0][2]
        if marchvalue2 > 0:
            if (marchIndex_1, marchIndex2) not in reSentmatchDict2.keys():
                reSentmatchDict2[(marchIndex_1, marchIndex2)] = [sent]
            else:
                reSentmatchDict2[(marchIndex_1, marchIndex2)].append(sent)
    return reSentmatchListRoot,reSentmatchDict1,reSentmatchDict2

def reSentsMarch_march(sentslist,templateroot,template1,template2):
    reSentmatchListRoot = []
    reSentmatchDict1 = {}
    reSentmatchDict2 = {}
    for sent in sentslist:
        sent = delNum(sent)
        ks=0
        ko=0
        for word in sent.split(' '):
            if (ks+ko) == 2:
                break
            if 'subjplace' in word:
                subjPlace = word
                ks=1
            if 'objplace' in word:
                objPlace = word
                ko=1
        marchvalueROOT,marchIndeROOT = reModel(sent,templateroot,subjPlace, objPlace)
        if marchvalueROOT > 0:
            reSentmatchListRoot.append((sent,marchvalueROOT))
        marchvalue1, marchIndex1 = reModel(sent, template1, subjPlace, objPlace)
        if marchvalue1 > 0:
            if marchIndex1 not in reSentmatchDict1.keys():
                reSentmatchDict1[marchIndex1] = [(sent,marchvalue1)]
            else:
                reSentmatchDict1[marchIndex1].append((sent,marchvalue1))

        allmarch2 = []
        for key in template2.keys():
            sencondT = template2[key]
            marchvalue_2, marchIndex_2 = reModel(sent, sencondT, subjPlace, objPlace)
            allmarch2.append((marchvalue_2, key,marchIndex_2))
        sortAllmarch2 = sorted(allmarch2,key=lambda dict:dict[0],reverse=True)
        marchvalue2, marchIndex_1,marchIndex2 = sortAllmarch2[0][0],sortAllmarch2[0][1],sortAllmarch2[0][2]
        if marchvalue2 > 0:
            if (marchIndex_1, marchIndex2) not in reSentmatchDict2.keys():
                reSentmatchDict2[(marchIndex_1, marchIndex2)] = [(sent,marchvalue2)]
            else:
                reSentmatchDict2[(marchIndex_1, marchIndex2)].append((sent,marchvalue2))
    return reSentmatchListRoot,reSentmatchDict1,reSentmatchDict2