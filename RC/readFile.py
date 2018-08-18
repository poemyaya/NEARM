# -*- coding: utf-8 -*-
import nltk
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
from numpy import array

def onehot(data):
    values = array(data)
    label_encoder = LabelEncoder()
    integer_encoded = label_encoder.fit_transform(values)
    onehot_encoder = OneHotEncoder(sparse=False)
    integer_encoded = integer_encoded.reshape(len(integer_encoded), 1)
    onehot_encoded = onehot_encoder.fit_transform(integer_encoded)
    dictdata = dict(zip(data, onehot_encoded))
    return dictdata


def dictsubjobjpos(datas):
    allpos=[]
    for data in datas:
        subj = data[0]
        obj = data[1]
        sen = data[2]
        lable = data[3]
        word_tag_sub = nltk.pos_tag([subj])
        pos_sub = word_tag_sub[0][1]
        allpos.append(pos_sub)
        word_tag_obj = nltk.pos_tag([obj])
        pos_obj = word_tag_obj[0][1]
        allpos.append(pos_obj)
    dictpos = onehot(allpos)
    return dictpos

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