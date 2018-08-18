# -*- coding: utf-8 -*-
import json,re,math
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

#二维高斯
def reTemplate(data,num):
    _templateitem=[]
    totalWords = 0
    # 每个簇
    wordDict = {}
    for da in data:
        da = delNum(da)
        da = re.sub('[’!"#$%&\'()*+,-./:;<=>?[\\]^`{|}~]+','',da)
        da = da.replace('  ',' ')
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

        if (ks+ko)<2:
            continue
        try:
            sindex = da.index(subjPlace)
            oindex = da.index(objPlace)

            for i in range(len(da)):
                wo = da[i]
                if len(wo)!=0 and 'subjplace' not in wo and 'objplace' not in wo:
                    totalWords += 1
                    loc_s = i-sindex
                    loc_o = i-oindex
                    if wo in wordDict:
                        wordDict[wo][0].append(loc_s)
                        wordDict[wo][1].append(loc_o)
                    else:
                        wordDict[wo]=[[loc_s],[loc_o]]
        except:
            print(da)
    #templateitem [word,[mu1,mu2],cov,fre]
    for setList in wordDict.keys():
        templateitem=[]
        tr_x = wordDict[setList][0]
        tr_y = wordDict[setList][1]
        freqWord = len(tr_x)*1.0/totalWords
        if len(tr_x) < 3:
            templateitem.append(setList)
            # templateitem.append(tr_x)
            templateitem.append('!!!')
            templateitem.append(freqWord)
        else:
            u_x = np.mean(tr_x)
            u_y = np.mean(tr_y)
            cov = np.cov(np.vstack((tr_x, tr_y)))
            # if sig < 0.000000001:
            #     templateitem.append(setList)
            #     templateitem.append(tr)
            #     templateitem.append('!!!')
            #     templateitem.append(freqWord)
            # else:
            templateitem.append(setList)
            templateitem.append([tr_x,tr_y])
            templateitem.append([u_x,u_y])
            templateitem.append(cov)
            templateitem.append(freqWord)
        _templateitem.append(templateitem)

    data = []

    for pp in _templateitem:
        if '!!!' not in pp:
            data.append(pp)
    b = sorted(data, key=lambda x: x[-1], reverse=True)
    clus = []
    if num>0:
        if len(b)>num:
            clus.extend(b[:num])
        else:
            clus = b
    else:
        clus = b
    clus_dict={}
    for wordList in clus:
        if '!!!' not in wordList:
            #[locs,loco],[mu1,mu2],cov,freq
            word = wordList[0]
            clus_dict[word] = [wordList[1]] #
            clus_dict[word].append(wordList[2]) #
            clus_dict[word].append(wordList[3]) #
            clus_dict[word].append(wordList[4])  #
    return clus_dict

def templateH(allTemplate,num):
    wordDict = {}
    #clusters是一个字典，wordDict收集单词在每个类簇的频率
    for index in allTemplate.keys():
        clusterDict = allTemplate[index]
        for word in clusterDict.keys():
            if word in wordDict:
                wordDict[word].append(clusterDict[word][-1])
            else:
                wordDict[word] = [clusterDict[word][-1]]
    # wordH计算单词的熵
    wordH = {}
    for wo in wordDict:
        h_wo = -sum([i * math.log(i, 2) for i in wordDict[wo]])
        wordH[wo] = math.exp(-h_wo)

    #更换模板中单词的概率，并归一化
    normSumClus = {}
    for clus in allTemplate:
        normSum  = 0
        for w in allTemplate[clus]:
            newF = allTemplate[clus][w][-1] * wordH[w]
            allTemplate[clus][w][-1] = newF
            normSum = normSum + newF
        normSumClus[clus] = normSum

    for cl in allTemplate:
        normsum = normSumClus[cl]
        for w1 in allTemplate[cl]:
            allTemplate[cl][w1][-1] = allTemplate[cl][w1][-1] / normsum

    clusFlit = {}
    for key in allTemplate.keys():
        clusFlit[key] = {}
        b = sorted(allTemplate[key].items(), key=lambda x: x[1][-1], reverse=True)
        if len(b)>num:
            b = b[:num]
        for item in b:
            clusFlit[key][item[0]] = item[1]
    return clusFlit

def getTemplate(attrlist):
    alltemplateLists = []
    for attr_i in range(len(attrlist)):
        attr = attrlist[attr_i]
        clusDict1 = json.load(open('/home/ren/remote/ruleMining/'+'BoD426'+'/cluster_'+attr+'.json'))
        templatedicts = {}
        for i in clusDict1.keys():
            clusChoose = clusDict1[i][:int(0.8*len(clusDict1[i]))]
            templatedicts[i] = reTemplate(clusChoose,0)
        newTemplateDict = templateH(templatedicts,20)
        _template = []
        for key in newTemplateDict.keys():
            _template.append(newTemplateDict[key])
        alltemplateLists.extend(_template)
    return alltemplateLists

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


def getTemplate_nyt(attrlist):
    trainUrl = '/home/ren/remote/classfi502/nyt/nyt/outdatas/'
    templatedicts = {}
    for key in attrlist.keys():
        label = attrlist[key]
        datas = readContent(trainUrl+key+'.txt')
        templatedicts[label] = reTemplate(datas, 0)
    newTemplateDict = templateH(templatedicts, 40)
    retemplate = []
    for key in newTemplateDict.keys():
        retemplate.append(newTemplateDict[key])
    return retemplate

