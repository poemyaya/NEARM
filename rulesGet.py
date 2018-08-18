# -*- coding: utf-8 -*-
from collections import Counter
import numpy as np


def getRules(transctions):
    if(len(transctions)) < 50:
        return [] ,[] ,[]

    itemCounter = Counter()
    pairCounter = Counter()

    for tran in transctions:
        itemCounter.update(tran)

    num_item = len(itemCounter)
    item_List = list(itemCounter.most_common(num_item))
    item_conf = np.zeros(len(item_List))
    for idx, (item, count) in enumerate(item_List):
        item_conf[idx] = count*1.0/len(transctions)

    item_ordered = []
    for idx in np.argsort(-1 * item_conf):
        item_ordered.append(item_List[idx])
    item_conf_ordered = item_conf[np.argsort(-1 * item_conf)]

    maxconf = 0.8
    if maxconf < item_conf_ordered[0]:
        maxconf = item_conf_ordered[0]
    th_conf = maxconf * 0.8
    # no filt
    # th_conf = 0.0

    rule1 = []
    item_ignord = set()
    for idx, conf in enumerate(item_conf_ordered):
        if conf >= th_conf:
            # if len(rule1)<10:
            rule1.append((item_ordered[idx][0],conf,conf)) #1阶规则conf和sup相等
        if conf == 1.0:
            item_ignord.add(item_ordered[idx][0])

    if(len(transctions)) < 100:
        return rule1, [], []

    for tran in transctions:
        for item1 in tran:
            if item1 in item_ignord:
                continue
            for item2 in tran:
                if item2 in item_ignord:
                    continue
                if item1 == item2:
                    continue
                pair = (item1, item2)
                pairCounter.update([pair])

    pair_list = []
    for pair in pairCounter.keys():
        conf_new = pairCounter[pair]*1.0/itemCounter[pair[0]]
        conf_old = itemCounter[pair[1]] * 1.0 / len(transctions)
        if conf_new <= conf_old:
            continue
        sup_pair = pairCounter[pair]*1.0/len(transctions)
        if sup_pair < 0.4:          #pair的支持度阈值，这里可以稍微小点
            continue
        pair_list.append((pair,conf_new,sup_pair))


    pair_list.sort(key=lambda x:-x[1])

    max_pair_conf = 0.8
    if pair_list[0][1] > max_pair_conf:
        max_pair_conf = pair_list[0][1]
    th_pair_conf = max_pair_conf * 0.8

    # no filt
    # th_pair_conf = 0.0

    rule2 = []
    for idx, (pair,pair_conf,pair_sup) in enumerate(pair_list):
        if pair_conf >= th_pair_conf:
            # if len(rule2)<10:
            rule2.append(pair_list[idx])
    filtlist = ['subjplace_datebirth', 'subjplace_publicdate', 'subjplace_gender', 'subjplace_dateofdeath',
                'objplace_datebirth', 'objplace_publicdate', 'objplace_gender', 'objplace_dateofdeath',
                'subjplace_citizenship', 'objplace_citizenship', 'subjplace_placeofinterment', 'objplace_placeofinterment',
                'objplace_inception','subjplace_inception']
    filtset = set(filtlist)
    attr_in_rule2 = set()
    for rule in rule2:
        consiqunce = rule[0][1]
        attr = consiqunce[:consiqunce.rindex("_")]
        attr_in_rule2.add(attr)
    filtrule1 = []
    for rule in rule1:
        consiqunce = rule[0]
        attr = consiqunce[:consiqunce.rindex("_")]
        if attr in attr_in_rule2 and attr in filtset:
            continue
        filtrule1.append(rule)
    #rule2.extend(filtrule1)

    return rule1, filtrule1, rule2


def sentValue(wikidata,sents):
    allsentValues = []
    for i_sent in range(len(sents)):
        if type(sents[i_sent]) == tuple:
            sent = sents[i_sent][0]
        else:
            sent = sents[i_sent]
        ks=0
        ko=0
        itemInfo = []

        for word in sent.split(' '):
            if (ks+ko) == 2:
                break
            if 'subjplace' in word:
                subjPlace = word
                subjPlacesplit = subjPlace.split('_')
                if subjPlacesplit[1] in wikidata:
                    values = set(wikidata[subjPlacesplit[1]])
                    itemInfo.extend([subjPlacesplit[0] + '_' + value for value in values])
                ks=1
            if 'objplace' in word:
                objPlace = word
                objPlacesplit = objPlace.split('_')
                if objPlacesplit[1] in wikidata:
                    values = set(wikidata[objPlacesplit[1]])
                    itemInfo.extend([objPlacesplit[0] + '_' + value for value in values])
                ko=1
        # except:
        #     print(sent)
        allsentValues.append(itemInfo)
    return allsentValues

def rulesConftoRules(rules):
    newrules = []
    for item in rules:
        newrules.append(item[0])
    return newrules

# 去掉含有instance的规则
def removerules(rules):
    newRules = []
    for rule in rules:
        #  or 'gender' in rule[0]
        if 'instanceof' in rule[0] or 'datebirth' in rule[0] or 'dateofdeath' in rule[0] \
              :
            continue
        newRules.append(rule)
    return newRules
def removerules2(rules):
    newRules = []
    for rule in rules:
        pre = rule[0][0]
        post = rule[0][1]
        # or 'gender' in post
        if 'instanceof' in pre or 'datebirth' in pre or 'instanceof' in post or 'datebirth' in post \
                or 'dateofdeath' in pre or 'dateofdeath' in post:
            continue
        newRules.append(rule)
    return newRules

def lzx_SCsearch(wikidata,sents):
    trans = sentValue(wikidata,sents)
    rule1, filtrule1, rule2 = getRules(trans)
    newrules1,newrules2 = rulesConftoRules(rule1),rulesConftoRules(rule2)
    return newrules1,newrules2

def lzx_SCsearch_conf(wikidata,sents):
    trans = sentValue(wikidata,sents)
    rule1, filtrule1, rule2 = getRules(trans)
    return rule1,rule2

def lzx_SCsearch_conf_filt(wikidata,sents):
    trans = sentValue(wikidata,sents)
    rule1, filtrule1, rule2 = getRules(trans)
    rule1 = removerules(rule1)
    rule2 = removerules2(rule2)
    return rule1,rule2
