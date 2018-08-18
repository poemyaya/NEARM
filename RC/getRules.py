# -*- coding: utf-8 -*-
import rulesGet
import json
def readWikidatas(url):
    lines = open(url).readlines()
    wikidatas = {}
    for line in lines:
        line = line.strip()
        line = line.split('\t')
        if line[0] in wikidatas:
            for i in line[1:]:
                wikidatas[line[0]].append(i)
        else:
            wikidatas[line[0]] = line[1:]
    return wikidatas

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

def newRulesFirst(rules11,rules22):
    newrules = []
    newrules.extend(rules11)
    newrules.extend(rules22)
    newrules = list(set(newrules))
    re_newrules = []
    flitlist = ['subjplace_datebirth' ,'subjplace_publicdate','subjplace_gender','subjplace_dateofdeath',
            'objplace_datebirth' ,'objplace_publicdate','objplace_gender','objplace_dateofdeath','subjplace_citizenship',
               'objplace_citizenship','subjplace_placeofinterment','objplace_placeofinterment','objplace_inception','subjplace_inception']

    allDicts ={}
    for rule in newrules:
        split_i = rule.split('_')
        attrrule = split_i[0]+'_'+split_i[1]
        if attrrule in allDicts.keys():
            allDicts[attrrule].append(rule)
        else:
            allDicts[attrrule] = [rule]

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


def reRulesLevel(attrlist):
    allRules1 = []
    allRules2 = []
    allRules3 = []
    for attr_i in range(len(attrlist)):
        attr = attrlist[attr_i]
        wikiDatas = readWikidatas('/home/ren/remote/TwolLayer208/wikidatas/' + attr + '_wikidata.csv')
        trains = readContent('/home/ren/remote/ruleMining/outdatas/train_' + attr + '.csv')
        rulesRootlist = rulesGet.lzx_SCsearch(wikiDatas, trains)
        rulesRoot = rulesRootlist[0]
        allRules1.extend(rulesRoot)

        rules1 = {}
        rules2 = {}

        clusDict1 = json.load(open('/home/ren/remote/ruleMining/'+'BoD426'+'/cluster_'+attr+'.json'))
        clusDict2 = json.load(open('/home/ren/remote/ruleMining/'+'BoD426'+'/second_'+attr+'.json'))

        for i in clusDict1.keys():
            r1_rulesList = rulesGet.lzx_SCsearch(wikiDatas, clusDict1[i])
            r1 = r1_rulesList[0]
            rules1[i] = newRulesFirst(rulesRoot, r1)
            rules2[i] = {}
            clus2_i = clusDict2[i]

            for j in clus2_i.keys():
                if clus2_i[j] == clusDict1[i]:
                    new_rules2 = rules1[i]
                else:
                    r2_rulesList = rulesGet.lzx_SCsearch(wikiDatas, clus2_i[j])
                    r2 = r2_rulesList[0]
                    new_rules2 = newRulesFirst(rules1[i], r2)

                rules2[i][j] = new_rules2
        sum1, sum2 = 0, 0
        for i in rules1.keys():
            sum1 = sum1 + len(rules1[i])
            allRules2.extend(rules1[i])
        for j in rules2.keys():
            for _j in rules2[j]:
                sum2 = sum2 + len(rules2[j][_j])
                allRules3.extend(rules2[j][_j])
        print('第一二三层：',len(rulesRoot),sum1,sum2)

    allRules1 = list(set(allRules1))
    allRules2 = list(set(allRules2))
    allRules3 = list(set(allRules3))
    print('after set: ',len(allRules1),len(allRules2),len(allRules3))

    return allRules1, allRules2, allRules3


