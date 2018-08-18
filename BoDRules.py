# -*- coding: utf-8 -*-
import writereadFile,rulesGet,reBoDpattern
import json,pickle
import numpy as np
import math
from collections import Counter
def newRulesFirst(rules11,rules22):
    # re_newrules  = rules22
    newrules = []
    newrules.extend(rules11)
    newrules.extend(rules22)
    r = list(set(newrules))

    keyr = {}
    for i in r:
        rulestring = i[0]
        if rulestring in keyr.keys():
            if i[1]>keyr[rulestring][0]:
                keyr[rulestring][0] = i[1]
                keyr[rulestring][1] = i[2]
        else:
            keyr[rulestring] =  [i[1],i[2]]
    newr = []
    for key in keyr:
        newr.append((key,keyr[key][0],keyr[key][1]))


    re_newrules = []
    flitlist = ['subjplace_datebirth' ,'subjplace_publicdate','subjplace_gender','subjplace_dateofdeath',
            'objplace_datebirth' ,'objplace_publicdate','objplace_gender','objplace_dateofdeath','subjplace_citizenship',
               'objplace_citizenship','subjplace_placeofinterment','objplace_placeofinterment','objplace_inception','subjplace_inception']

    allDicts ={}
    for rulelist in newr:
        rule = rulelist[0]
        split_i = rule.split('_')
        attrrule = split_i[0]+'_'+split_i[1]
        if attrrule in allDicts.keys():
            allDicts[attrrule].append(rulelist)
        else:
            allDicts[attrrule] = [rulelist]

    for key in allDicts.keys():
        i_rules = set(allDicts[key])
        if len(i_rules)>1 and key in flitlist:
            # print rules11
            # print rules22
            for ii in i_rules:
                if ii in rules22:
                    re_newrules.append(ii)
        else:
            re_newrules.extend(i_rules)
    # print re_newrules
    # print '--------------'
    re_newrules = list(set(re_newrules))

    return re_newrules
#非继承
def newRulesSecond(r1,r2):
    r = []
    r.extend(r1)
    r.extend(r2)
    r = set(r)
    keyr = {}
    for i in r:
        rulestring = i[0]
        if rulestring in keyr.keys():
            if i[1]>keyr[rulestring][0]:
                keyr[rulestring][0] = i[1]
                keyr[rulestring][1] = i[2]
        else:
            keyr[rulestring] =  [i[1],i[2]]
    newr = []
    for key in keyr:
        newr.append((key,keyr[key][0],keyr[key][1]))
    return newr

def dealSupport(predictset_ignore,sents):
    newpredictset_ignore = []
    for i in range(len(predictset_ignore)):
        item = predictset_ignore[i]
        index = int(item[0].split('_')[-1])
        marchDegre = sents[index][1]
        #求乘积
        # newpredictset_ignore.append((item[0],math.log(item[1]) + math.log(marchDegre),item[2]))
        #求和
        newpredictset_ignore.append((item[0], item[1] + marchDegre, item[2]))
    return newpredictset_ignore


def printperf1(wikidata,rules,rules1_2,reSentmatchDict):

    allpredictset_ignore = []
    allpredictset_fault = []
    if isinstance(reSentmatchDict,list):
        transactions = rulesGet.sentValue(wikidata,reSentmatchDict)
        predictset_ignore, predictset_fault = ruleval(transactions, rules,rules1_2)
        allpredictset_ignore.extend(predictset_ignore)
        allpredictset_fault.extend(predictset_fault)
    else:
        for key in reSentmatchDict:
            sents = reSentmatchDict[key]
            if type(key) == tuple:
            # if len(key) > 1:
                rule_1 = rules[key[0]][key[1]]
                rule_2 = rules1_2[key[0]][key[1]]
            else:
                rule_1 = rules[key]
                rule_2 = rules1_2[key]
            transactions = rulesGet.sentValue(wikidata,sents)
            predictset_ignore,predictset_fault = ruleval(transactions, rule_1,rule_2)
            n_predictset_ignore = dealSupport(predictset_ignore,sents)
            n_predictset_fault = dealSupport(predictset_fault,sents)
            allpredictset_ignore.extend(n_predictset_ignore)
            allpredictset_fault.extend(n_predictset_fault)

    # print allpredictset[0]
    return allpredictset_ignore,allpredictset_fault

def ruleval(transactions, rule_1,rule_2):
    attrvaluedict = {}  #包含 sub_attr_value的句子id
    attrdict = {}       #包含 sub_attr的句子，如果有多个value，只存一次，这里都存句子的id
    attrcounter = Counter()  #统计每个属性在transacion里出现多少次，那些在rule后件的属性利用这个作为真实集数目
    for idx, trans in enumerate(transactions):
        for item in trans:
            if item not in attrvaluedict:
                attrvaluedict[item] = set()
            attrvaluedict[item].add(idx)
            attr = item[0:item.rindex("_")]
            if attr not in attrdict:
                attrdict[attr] = set()
            attrdict[attr].add(idx)
            attrcounter.update([attr])
    predictset = {}
    for rule1 in rule_1:
        attrvalue = rule1[0]
        # attr = attrvalue[:attrvalue.rindex("_")]
        for idx, trans in enumerate(transactions):
            predictset[attrvalue+"_"+str(idx)] = rule1[1]#1阶规则全部预测
    for rule2 in rule_2:
        condition = rule2[0][0]
        consiquence = rule2[0][1]
        # attr = consiquence[0:consiquence.rindex("_")]
        for idx, trans in enumerate(transactions):
            if condition in trans:
                if consiquence + "_" + str(idx) in predictset.keys():
                    if rule2[1]>predictset[consiquence + "_" + str(idx)]:
                        predictset[consiquence + "_" + str(idx)] = rule2[1]
                else:
                    predictset[consiquence + "_" + str(idx)] = rule2[1]

    re_predictset_ignore = []
    re_predictset_fault = []


    for pred in predictset:
        items = pred.split("_")
        attr = items[0]+"_"+items[1]
        attrvalue = attr+"_"+items[2]
        sid = int(items[3])
        if attr in attrdict.keys():
            if sid in attrdict[attr]:
                if attrvalue in attrvaluedict.keys():
                    if sid in attrvaluedict[attrvalue]:
                        re_predictset_ignore.append((pred,predictset[pred],1))
                        re_predictset_fault.append((pred,predictset[pred],1))
                    else:
                        re_predictset_ignore.append((pred, predictset[pred], 0))
                        re_predictset_fault.append((pred, predictset[pred], 0))
                else:
                    re_predictset_ignore.append((pred, predictset[pred], 0))
                    re_predictset_fault.append((pred, predictset[pred], 0))
            else:
                # print pred
                re_predictset_fault.append((pred, predictset[pred], 0))
        else:
            re_predictset_fault.append((pred, predictset[pred], 0))

    return re_predictset_ignore,re_predictset_fault  # precision = tp/(tp+fp), recall = tp/(tp+fn)

def rePreAndNum(allpredictsets):
    radios = np.linspace(0.02, 1.02, num=50, endpoint=False, retstep=False, dtype=None)
    sort_allpredictsets_lvl2 = sorted(allpredictsets, key=lambda dict: dict[1], reverse=True)
    pre_radios = []
    tri_radios = []

    for radio in radios:
        triNum = int(radio * len(sort_allpredictsets_lvl2))
        tri_radios.append(triNum)
        tp = [i for i in sort_allpredictsets_lvl2[:triNum] if i[2] == 1]
        pre = 0
        if triNum>0:
            pre = len(tp) * 1.0 / triNum
        pre_radios.append('%.3f' % pre)
    return pre_radios,tri_radios




if __name__=='__main__':
    #song,'spouse','mother','film','father','child','filmCastmember','songPerformer'
    #八个关系
    attrlist=['song','spouse','mother','film','father','child','filmCastmember','songPerformer']
    # attrlist = ['song']
    url1 = 'outdatas_baseline'
    print(url1)
    allpredictsets_lvl2_ignore = []
    allpredictsets_lvl3_ignore = []
    allpredictsets_lvl2_fault = []
    allpredictsets_lvl3_fault = []

    allrelBoD = {}
    alltestsent = []
    allroot = {}
    allroot_2 = {}
    for attr_i in range(len(attrlist)):
        attr = attrlist[attr_i]
        print(attr)
        wikiDatas = writereadFile.readWikidatas('/home/ren/remote/ruleMining2/wikidatas/' + attr + '_wikidata.csv')
        trains = writereadFile.readContent('/home/ren/remote/ruleMining2/outdatas_baseline/train_' + attr + '.csv')
        templateDictsRoot = {}
        #返回规则前件
        templateRoot = reBoDpattern.reTemplate(trains)
        allrelBoD[attr_i] = templateRoot
        templateDictsRoot[0] = templateRoot
        # print templateDictsRoot
        #返回规则后件
        rulesRootlist = rulesGet.lzx_SCsearch_conf_filt(wikiDatas, trains)
        rulesRoot = rulesRootlist[0]
        allroot[attr_i] = rulesRoot
        numbrRoot = len(rulesRoot)

        rulesRoot_2 = rulesRootlist[1]
        allroot_2[attr_i] = rulesRoot_2
        numbrRoot_2 = len(rulesRoot_2)

        rules1 = {}
        rules2 = {}
        numbr1 = 0
        numbr2 = 0

        rules1_2 = {}
        rules2_2= {}

        templateDicts1 = {}
        templateDicts2 = {}

        numbr1_2 = 0
        numbr2_2 = 0

        #KMeans403  outdatas

        clusDict1 = json.load(open(url1+'/cluster_'+attr+'.json'))
        clusDict2 = json.load(open(url1+'/second_'+attr+'.json'))
        #层次聚类的规则 为了得到更细粒度的规则
        for i in clusDict1.keys():
            r1_rulesList = rulesGet.lzx_SCsearch_conf_filt(wikiDatas, clusDict1[i][:int(0.8*len(clusDict1[i]))])
            r1 = r1_rulesList[0]
            rules1[i] = newRulesFirst(rulesRoot,r1)
            numbr1 = numbr1+len(rules1[i])
            rules2[i] = {}
            r1_2 = r1_rulesList[1]
            rules1_2[i] = newRulesSecond(rulesRoot_2, r1_2)
            numbr1_2 = numbr1_2+len(rules1_2[i])
            rules2_2[i] = {}

            templateDicts1[i] = reBoDpattern.reTemplate(clusDict1[i][:int(0.8*len(clusDict1[i]))])
            templateDicts2[i] = {}
            clus2_i = clusDict2[i]

            for j in clus2_i.keys():
                if clus2_i[j] == clusDict1[i]:
                    new_rules2 = rules1[i]
                    new_rules2_2 = rules1_2[i]
                    templateDicts2[i][j] = templateDicts1[i]
                else:
                    r2_rulesList = rulesGet.lzx_SCsearch_conf_filt(wikiDatas, clus2_i[j][:int(0.8*len(clus2_i[j]))])
                    r2 = r2_rulesList[0]
                    new_rules2 = newRulesFirst(rules1[i], r2)

                    r2_2 = r2_rulesList[1]
                    new_rules2_2 = newRulesSecond(rules1_2[i], r2_2)

                    templateDicts2[i][j] = reBoDpattern.reTemplate(clus2_i[j][:int(0.8*len(clus2_i[j]))])
                numbr2 = numbr2+len(new_rules2)
                rules2[i][j] = new_rules2
                numbr2_2 = numbr2_2 +len(new_rules2_2)
                rules2_2[i][j] = new_rules2_2

        tests_sent = writereadFile.readContent('outdatas_baseline/test_' + attr + '.csv')
        alltestsent.extend(tests_sent)
        reSentmatchListRoot,reSentmatchDict1,reSentmatchDict2 = \
            reBoDpattern.reSentsMarch_march\
                (tests_sent,templateDictsRoot,templateDicts1, templateDicts2)

        # printperf1(wikiDatas,rulesRoot,reSentmatchListRoot)
        print('--------1----------')
        print(numbrRoot, numbr1, numbr2)
        predictset_ignore_lvl2, predictset_faultlvl2 = printperf1(wikiDatas,rules1,rules1_2,reSentmatchDict1)
        print('# triple facts',len(predictset_ignore_lvl2),len(predictset_faultlvl2))
        allpredictsets_lvl2_ignore.extend(predictset_ignore_lvl2)
        allpredictsets_lvl2_fault.extend(predictset_faultlvl2)

        print('--------2----------')
        print(numbrRoot_2, numbr1_2, numbr2_2)
        predictset_ignore_lvl3, predictset_faultlvl3 = printperf1(wikiDatas,rules2,rules2_2,reSentmatchDict2)
        print('# triple facts', len(predictset_ignore_lvl3), len(predictset_faultlvl3))
        allpredictsets_lvl3_ignore.extend(predictset_ignore_lvl3)
        allpredictsets_lvl3_fault.extend(predictset_faultlvl3)

    print('--------root----------')
    sentmarch_all = {}
    for sent in alltestsent:
        sent = reBoDpattern.delNum(sent)
        ks = 0
        ko = 0
        for word in sent.split(' '):
            if (ks + ko) == 2:
                break
            if 'subjplace' in word:
                subjPlace = word
                ks = 1
            if 'objplace' in word:
                objPlace = word
                ko = 1
        marchvalue0, marchIndex0 = reBoDpattern.reModel(sent, allrelBoD, subjPlace, objPlace)
        if marchvalue0 > 0:
            if marchIndex0 not in sentmarch_all.keys():
                sentmarch_all[marchIndex0] = [(sent,marchvalue0)]
            else:
                sentmarch_all[marchIndex0].append((sent,marchvalue0))
    #三元组预测 准确率计算
    allwikiDatas = writereadFile.readWikidatas('/home/ren/remote/ruleMining2/wikidatas/all_wikidatas.csv')
    predictset_ignore_lvl1, predictset_fault_lvl1 = printperf1(allwikiDatas, allroot, allroot_2, sentmarch_all)
    print('# 1---all triple facts', len(predictset_ignore_lvl1), len(predictset_fault_lvl1))
    lvl1_pre_ignore, lvl1_num_ignore = rePreAndNum(predictset_ignore_lvl1)
    lvl1_pre_fault, lvl1_num_fault = rePreAndNum(predictset_fault_lvl1)

    print('# 2---all triple facts', len(allpredictsets_lvl2_ignore), len(allpredictsets_lvl2_fault))
    lvl2_pre_ignore ,lvl2_num_ignore = rePreAndNum(allpredictsets_lvl2_ignore)
    lvl3_pre_ignore ,lvl3_num_ignore = rePreAndNum(allpredictsets_lvl3_ignore)

    print('# 3---all triple facts', len(allpredictsets_lvl3_ignore), len(allpredictsets_lvl3_fault))
    lvl2_pre_fault, lvl2_num_fault = rePreAndNum(allpredictsets_lvl2_fault)
    lvl3_pre_fault, lvl3_num_fault= rePreAndNum(allpredictsets_lvl3_fault)
    print('end')
    write1 = open('plotAll/' + url1 + '_all_bod_march_add' + '.pkl', 'wb')
    pickle.dump([lvl1_pre_ignore, lvl1_num_ignore,lvl1_pre_fault, lvl1_num_fault,
                 lvl2_pre_ignore,lvl2_num_ignore,lvl2_pre_fault, lvl2_num_fault,
                 lvl3_pre_ignore,lvl3_num_ignore,lvl3_pre_fault, lvl3_num_fault], write1)