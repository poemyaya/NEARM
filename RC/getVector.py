# -*- coding: utf-8 -*-
import re
import numpy as np
from scipy.stats import multivariate_normal

#----------计算规则向量-----------#
def resenAttr(sent,wikiDatas):
    clusterFreq=[]
    type = []
    sent = sent.split(" ")
    ks=0
    ko=0
    for word in sent:
        if (ks+ko) == 2:
            break
        if 'subjplace' in word:
            subjPlace = word
            subjPlace = subjPlace.split('_')
            if subjPlace[1] in wikiDatas:
                values = wikiDatas[subjPlace[1]]
                for value in values:
                    clusterFreq.append(subjPlace[0]+'_'+value)
                    type.append(subjPlace[0]+'_'+value.split('_')[0])
            ks=1
        if 'objplace' in word:
            objPlace = word
            objPlace = objPlace.split('_')
            if objPlace[1] in wikiDatas:
                values = wikiDatas[objPlace[1]]
                for value in values:
                    clusterFreq.append(objPlace[0]+'_'+value)
                    type.append(objPlace[0]+'_'+value.split('_')[0])
            ko=1
    return clusterFreq,type

def reVectorSetRules(sen,rule,wikiDatas):

    resenAttrlist = resenAttr(sen,wikiDatas)
    senAttr = resenAttrlist[0]
    type = resenAttrlist[1]
    rule_vect = []
    for i in range(len(rule)):
        rulesplit = rule[i].split('_')
        ruletype = rulesplit[0]+'_'+rulesplit[1]

        if rule[i] in senAttr:
            rule_vect.extend([1,0,0])
        elif ruletype in type and rule[i] not in senAttr:
            rule_vect.extend([0,1,0])
        else:
            rule_vect.extend([0,0,1])
    return rule_vect

#----------计算单词向量-----------#

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

def reWordIndex(sent):
    sent = delNum(sent)
    sent = re.sub('[’!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~]+', '', sent)
    sent = sent.replace('  ', ' ')
    sent = sent.split(" ")
    ks = 0
    ko = 0
    for word in sent:
        if (ks + ko) == 2:
            break
        if 'subjplace' in word:
            subjPlace = word
            ks = 1
        if 'objplace' in word:
            objPlace = word
            ko = 1
    sindex = sent.index(subjPlace)
    oindex = sent.index(objPlace)

    # 防止一个单词出现多次，这里没有用字典
    wordIndex = []
    for i in range(len(sent)):
        wo = sent[i]
        if len(wo) != 0 and 'subjplace' not in wo and 'objplace' not in wo:
            wordIndex.append((wo, [i - sindex, i - oindex]))

    return wordIndex

def matrixSO_9(loc_s, loc_o):
    reMatrix = []
    locS = [loc_s - 0.5, loc_s + 0.5]
    locO = [loc_o - 0.5, loc_o + 0.5]

    reMatrix.append([locS[0], locO[0]])
    reMatrix.append([locS[0], locO[1]])
    reMatrix.append([locS[1], locO[0]])
    reMatrix.append([locS[1], locO[1]])

    reMatrix.append([loc_s, locO[0]])
    reMatrix.append([loc_s, locO[1]])
    reMatrix.append([locS[0], loc_o])
    reMatrix.append([locS[1], loc_o])

    reMatrix.append([loc_s, loc_o])

    return reMatrix

def func(x,meanlist,covlist):
    return multivariate_normal.pdf(x, mean=meanlist, cov=covlist)

def tryFunc(x,locList,meanlist,covlist):
    res = 0
    try:
        res = func(x,meanlist,covlist)
    except:
        randomList0 = np.random.normal(0, 0.1, len(locList[0]))
        tr_x = locList[0] + randomList0
        # randomList1 = [random.random() for i in range(len(locList[0]))]
        randomList1 = np.random.normal(0, 0.1, len(locList[0]))
        tr_y = locList[1] + randomList1
        cov = np.cov(np.vstack((tr_x, tr_y)))
        res = tryFunc(x,locList,meanlist,cov)
    return res

def getwordvector(wordIndex, template):
    sims = {}
    for wordlist in wordIndex:
        word = wordlist[0]
        if word in template.keys():
            loc_s = wordlist[1][0]
            loc_o = wordlist[1][1]
            reMatrix = matrixSO_9(loc_s, loc_o)

            locList = template[word][0]
            meanlist = template[word][1]
            covlist = template[word][2]


            y0 = tryFunc(reMatrix[0],locList,meanlist,covlist)
            y1 = tryFunc(reMatrix[1],locList,meanlist,covlist)
            y2 = tryFunc(reMatrix[2],locList,meanlist,covlist)
            y3 = tryFunc(reMatrix[3],locList,meanlist,covlist)
            y4 = tryFunc(reMatrix[4],locList,meanlist,covlist)
            y5 = tryFunc(reMatrix[5], locList, meanlist, covlist)
            y6 = tryFunc(reMatrix[6], locList, meanlist, covlist)
            y7 = tryFunc(reMatrix[7], locList, meanlist, covlist)
            y8 = tryFunc(reMatrix[8], locList, meanlist, covlist)


            # y = ((y0+y1+y2+y3)*0.15+y4*0.4) * template[word][-1]
            y = ((y0 + y1 + y2 + y3 + y4 + y5 + y6 + y7) * 0.1 + y8 * 0.2) * template[word][-1]
            if y>1:
                y = 1
            sims[word] = y

    bodwords = np.array(list(template.keys()))
    bodwords = bodwords[np.argsort(bodwords)]
    vec = np.zeros(len(bodwords))
    for idx, bodword in enumerate(bodwords):
        if bodword in sims:
            vec[idx] = sims[bodword]
    return vec

def reVectorWords(sent,templates):
    word_vects = []
    wordIndex = reWordIndex(sent)
    for template in templates:
        if len(template)==0:
            continue
        word_vects.extend(getwordvector(wordIndex, template))
    return word_vects