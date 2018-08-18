# -*- coding: utf-8 -*-
import writereadFile,rulesGet
from gensim.models import TfidfModel
from gensim.corpora import Dictionary
from gensim import similarities
import numpy as np
from collections import Counter
import time,json
import pickle
#非继承
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
            keyr[rulestring] = [i[1],i[2]]
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
def reRulesDict(wikiDatas,attrlist):
    preurl = '/home/ren/remote/ruleMining2/'
    # attrlist = ['spouse', 'song', 'mother', 'film', 'father', 'child', 'filmCastmember', 'songPerformer']
    #attrlist = ['mother']
    rulesDcit = {}
    rulesDcit2 = {}
    rulesDcit3 = {}
    for attr_i in range(len(attrlist)):
        attr = attrlist[attr_i]
        datas = writereadFile.readContent(preurl + 'outdatas_baseline/train_' + attr + '.csv')
        rulesRootlist = rulesGet.lzx_SCsearch_conf_filt(wikiDatas, datas) #放了一阶规则和二阶规则
        rulesDcit[attr_i] = rulesRootlist
        rulesDcit2[attr_i] = {}
        rulesDcit3[attr_i] = {}
        clusDict2 = json.load(open(preurl + 'outdatas_baseline/cluster_' + attr + '.json'))
        clusDict3 = json.load(open(preurl + 'outdatas_baseline/second_' + attr + '.json'))
        for j in clusDict2.keys():
            r2_rulesList = rulesGet.lzx_SCsearch_conf_filt(wikiDatas, clusDict2[j])
            r2 = r2_rulesList[0]
            newr2 = newRulesFirst(rulesRootlist[0], r2)
            r2_2 = r2_rulesList[1]
            newr2_2 = newRulesSecond(rulesRootlist[1],r2_2)
            rulesDcit2[attr_i][j] = [newr2,newr2_2]

            rulesDcit3[attr_i][j] = {}
            clus3_j = clusDict3[j]
            for k in clus3_j.keys():
                if clus3_j[k] == clusDict2[j]:
                    new_rules3 = newr2
                    new_rules3_2 = newr2_2
                else:
                    r3_rulesList = rulesGet.lzx_SCsearch_conf_filt(wikiDatas, clus3_j[k])
                    r3 = r3_rulesList[0]
                    new_rules3 = newRulesFirst(newr2,r3)
                    r3_2 = r3_rulesList[1]
                    new_rules3_2 = newRulesSecond(newr2_2,r3_2)
                rulesDcit3[attr_i][j][k] = [new_rules3,new_rules3_2]


    return rulesDcit,rulesDcit2,rulesDcit3

def reBOWModelist(alldatas):
    # attrlist = ['spouse', 'song', 'mother', 'film', 'father', 'child', 'filmCastmember', 'songPerformer']
    # alldatas = []
    # num_features = 0
    # preurl = '/home/ren/remote/ruleMining/'
    # for attr_i in range(len(attrlist)):
    #     attr = attrlist[attr_i]
    #     datas = writereadFile.readContent(preurl + 'outdatas/train_' + attr + '.csv')
    #     dataset = []
    #     for data in datas:
    #         dataset.extend(data.split(' '))
    #     if len(dataset)>num_features:
    #         num_features = len(dataset)
    #     alldatas.append(dataset)
    dictionary = Dictionary(alldatas)
    corpus = [dictionary.doc2bow(text) for text in alldatas]
    tfidf_model = TfidfModel(corpus)
    similarity = similarities.Similarity('Similarity-tfidf-index', corpus, num_features=len(dictionary))
    return dictionary,tfidf_model,similarity


def reBOWModel2(attrlist):
    preurl = '/home/ren/remote/ruleMining2/'
    # attrlist = ['spouse', 'song', 'mother', 'film', 'father', 'child', 'filmCastmember', 'songPerformer']
    #attrlist = ['mother']
    model1,model2,model3 = [],{},{}
    alldatas1,alldatas2,alldatas3 = [],{},{}
    for attr_i in range(len(attrlist)):
        attr = attrlist[attr_i]
        datas = writereadFile.readContent(preurl + 'outdatas_baseline/train_' + attr + '.csv')
        dataset = []
        for data in datas:
            dataset.extend(data.split(' '))
        alldatas1.append(dataset)

        clusDict2 = json.load(open(preurl + 'outdatas_baseline/cluster_' + attr + '.json'))
        clusDict3 = json.load(open(preurl + 'outdatas_baseline/second_' + attr + '.json'))

        # alldata2List = []
        alldatas2[attr_i] = []
        alldatas3[attr_i] = {}
        clusDict2keys = list(clusDict2.keys())
        clusDict2keys.sort()
        for j in clusDict2keys:
            dataset2 = []
            for data_2 in clusDict2[j]:
                dataset2.extend(data_2.split(' '))
            # alldata2List.append(dataset2)
            alldatas2[attr_i].append(dataset2)
            # alldata3List = []
            alldatas3[attr_i][j] = []
            clus3_j = clusDict3[j]
            clus3_jkeys = list(clus3_j.keys())
            clus3_jkeys.sort()
            for k in clus3_jkeys:
                # print(attr_i,j,k)
                dataset3 = []
                for data_3 in clus3_j[k]:
                    dataset3.extend(data_3.split(' '))
                # alldata3List.append(dataset3)
                alldatas3[attr_i][j].append(dataset3)
    # print(len(alldatas1))
    # for p in alldatas2:
    #     print(p,len(alldatas2[p]))
    # for q in alldatas3:
    #     for o in alldatas3[q]:
    #         print(q,o,len(alldatas3[q][o]))

    model1 = reBOWModelist(alldatas1)
    for key2 in alldatas2:
        model2[key2] = reBOWModelist(alldatas2[key2])
        model3[key2] = {}
        for key3 in alldatas3[key2].keys():
            model3[key2][key3] = reBOWModelist(alldatas3[key2][key3])
    return model1,model2,model3

def testSents(testSent,model):
    dictionary, tfidf_model, similarity = model[0],model[1],model[2]
    testSent = testSent.split(' ')
    test_corpus_1 = dictionary.doc2bow(testSent)
    test_corpus_tfidf_1 = tfidf_model[test_corpus_1]
    sim = similarity[test_corpus_tfidf_1]
    sim = np.array(sim)
    return np.argmax(sim),sim.max()

def testMarch_BOW(attrlist):
    preurl = '/home/ren/remote/ruleMining2/'
    # attrlist = ['spouse', 'song', 'mother', 'film', 'father', 'child', 'filmCastmember', 'songPerformer']
    #attrlist = ['mother']
    testmarchDcit = {}
    testmarchDcit2 = {}
    testmarchDcit3 = {}
    model1, model2, model3 = reBOWModel2(attrlist)
    # for i in range(len(attrlist)):
    #     testmarchDcit[i] = []
    #     testmarchDcit2[i] = {}
    #     testmarchDcit3[i] = {}

    for attr_i in range(len(attrlist)):
        attr = attrlist[attr_i]
        datas = writereadFile.readContent(preurl + 'outdatas_baseline/test_' + attr + '.csv')
        for testSent in datas:
            marchindex,sim1 = testSents(testSent,model1)
            if sim1>0:
                if marchindex not in testmarchDcit:
                    testmarchDcit[marchindex] = []
                testmarchDcit[marchindex].append(testSent)
            model2Test = model2[marchindex]
            model3Test = model3[marchindex]
            marchindex2,sim2 = testSents(testSent, model2Test)
            marchindex3,sim3 = testSents(testSent, model3Test[str(marchindex2)])
            if (marchindex,marchindex2) not in testmarchDcit2:
                testmarchDcit2[(marchindex,marchindex2)] = []
            if sim2>0:
                testmarchDcit2[(marchindex,marchindex2)].append(testSent)
            if (marchindex,marchindex2,marchindex3) not in testmarchDcit3:
                testmarchDcit3[(marchindex,marchindex2,marchindex3)] = []
            if sim3>0:
                testmarchDcit3[(marchindex,marchindex2,marchindex3)].append(testSent)
    return testmarchDcit,testmarchDcit2,testmarchDcit3

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

def reResult(wikiDatas,rulesdcits,testmarchdcits,lvl):
    allpredictset_ignore = []
    allpredictset_fault = []
    for key in testmarchdcits.keys():
        # print(key)
        sents = testmarchdcits[key]
        if len(sents) == 0:
            continue
        if lvl == 1:
            triplefactslist = rulesdcits[key]
        elif lvl == 2:
            triplefactslist = rulesdcits[key[0]][str(key[1])]
        elif lvl == 3:
            triplefactslist = rulesdcits[key[0]][str(key[1])][str(key[2])]
        transactions = rulesGet.sentValue(wikiDatas, sents)
        predictset_ignore, predictset_fault = ruleval(transactions, triplefactslist[0], triplefactslist[1])
        allpredictset_ignore.extend(predictset_ignore)
        allpredictset_fault.extend(predictset_fault)
    return allpredictset_ignore, allpredictset_fault

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
    url1 = 'outdatas_baseline'
    attrlist = ['spouse', 'song', 'mother', 'film', 'father', 'child', 'filmCastmember', 'songPerformer']
    # attrlist = ['mother']
    print('loading--------',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    testmarchDcit, testmarchDcit2, testmarchDcit3 = testMarch_BOW(attrlist)
    allwikiDatas = writereadFile.readWikidatas('/home/ren/remote/ruleMining2/wikidatas/all_wikidatas.csv')
    rulesDcits, rulesDcit2, rulesDcit3 = reRulesDict(allwikiDatas, attrlist)
    # print(rulesDcits.keys())
    # for i in rulesDcit2:
    #     for j in rulesDcit2:
    #         print(i,j)
    # for i in rulesDcit3:
    #     for j in rulesDcit3[i]:
    #         for k in rulesDcit3[i][j]:
    #             print(i,j,k)
    print('load data over',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    predictset_ignore_lvl1, predictset_fault_lvl1 = reResult(allwikiDatas, rulesDcits,testmarchDcit,1)
    predictset_ignore_lvl2, predictset_fault_lvl2 = reResult(allwikiDatas, rulesDcit2, testmarchDcit2, 2)
    predictset_ignore_lvl3, predictset_fault_lvl3 = reResult(allwikiDatas, rulesDcit3, testmarchDcit3, 3)
    print('end',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    lvl1_pre_ignore, lvl1_num_ignore = rePreAndNum(predictset_ignore_lvl1)
    lvl1_pre_fault, lvl1_num_fault = rePreAndNum(predictset_fault_lvl1)

    lvl2_pre_ignore, lvl2_num_ignore = rePreAndNum(predictset_ignore_lvl2)
    lvl2_pre_fault, lvl2_num_fault = rePreAndNum(predictset_fault_lvl2)

    lvl3_pre_ignore, lvl3_num_ignore = rePreAndNum(predictset_ignore_lvl3)
    lvl3_pre_fault, lvl3_num_fault = rePreAndNum(predictset_fault_lvl3)


    print('end')
    write1 = open('plotAll/' + url1 + '_all_bow' + '.pkl', 'wb')
    pickle.dump([lvl1_pre_ignore, lvl1_num_ignore,lvl1_pre_fault, lvl1_num_fault,
                 lvl2_pre_ignore,lvl2_num_ignore,lvl2_pre_fault, lvl2_num_fault,
                 lvl3_pre_ignore,lvl3_num_ignore,lvl3_pre_fault, lvl3_num_fault], write1)
