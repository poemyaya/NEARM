# -*- coding: utf-8 -*-
import json,pickle
import numpy as np
def readDatas(url):
    alldatas = []
    lines = open(url).readlines()
    for line in lines:
        line = line.strip()
        line = json.loads(line)
        alldatas.append(line)
    return alldatas

def getSentattr(true_label):
    attrlist_set = set()
    for item in true_label:
        attr = item[:item.rindex("_")]
        attrlist_set.add(attr)
    return list(attrlist_set)

def rePreAndNum(allpredictsets):
    radios = np.linspace(0.02, 1.02, num=50, endpoint=False, retstep=False, dtype=None)
    sort_allpredictsets_lvl2 = sorted(allpredictsets, key=lambda dict: dict[1], reverse=True)
    sort_allpredictsets_lvl2 = sort_allpredictsets_lvl2[:60000]
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

#第五步 计算准确率 与BOD Beta BOW的方法一样 测试集数据由第一步得到
if __name__=='__main__':
    url = '/home/ydm/ren/remote/multiLabel/data/result_place.txt'
    pre_labels = readDatas(url)
    true_labels = readDatas('/home/ydm/ren/remote/multiLabel/data/alllabel_test.txt')
    filtlist = ['subjplace_datebirth',  'subjplace_dateofdeath','subjplace_instanceof',
                'objplace_datebirth',  'objplace_dateofdeath','objplace_instanceof']
    allpredictsets_ignore = []
    allpredictsets_strict= []
    for i in range(len(pre_labels)):
        pre_label = pre_labels[i]
        true_label = true_labels[i]
        true_label_attr = getSentattr(true_label)
        keylist = pre_label.keys()
        for key in keylist:
            attr = key[:key.rindex("_")]
            if attr in filtlist:
                continue
            if pre_label[key]<0.5:
                continue
            if attr not in true_label_attr:
                allpredictsets_strict.append((key,pre_label[key],0))
            else:
                if key in true_label:
                    allpredictsets_strict.append((key, pre_label[key], 1))
                    allpredictsets_ignore.append((key, pre_label[key], 1))
                else:
                    allpredictsets_strict.append((key, pre_label[key], 0))
                    allpredictsets_ignore.append((key, pre_label[key], 0))
    print(len(allpredictsets_ignore),len(allpredictsets_strict))
    multilabel_ignore_pre, multilabel_ignore_number = rePreAndNum(allpredictsets_ignore)
    multilabel_strict_pre, multilabel_strict_number = rePreAndNum(allpredictsets_strict)

    write1 = open('result/multilabel_place_60000.pkl', 'wb')
    pickle.dump([multilabel_ignore_pre, multilabel_ignore_number,multilabel_strict_pre, multilabel_strict_number,], write1)


