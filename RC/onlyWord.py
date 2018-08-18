# -*- coding: utf-8 -*-
import json
import time
import getBoDtemplate,getRules,getVector,readFile,wEntityVector
import nltk
import xgboost as xgb
from sklearn.externals import joblib
from sklearn import metrics
from sklearn.metrics import classification_report
import numpy as np
def printtime(tx):
    print(tx,time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))


def reSubjobjqueRule(sent):
    sent = sent.split(" ")
    ks=0
    ko=0
    for i in range(len(sent)):
        if 'subjplace_' in sent[i]:
            ks = i
        if 'objplace_' in sent[i]:
             ko=i
    if ks<ko:
        return 1
    else:
        return 0


def allVectors(trains,alltemplates,dict_pos,dict_entity):
    allvectors = []
    for data in trains:
        #subj、obj是id的形式
        subj = data[0]
        obj = data[1]
        sent = data[2]
        label = data[3]
        vectors = []
        wordVector = getVector.reVectorWords(sent, alltemplates)

        #主语和宾语的词性
        word_tag_sub = nltk.pos_tag([subj])
        word_tag_obj = nltk.pos_tag([obj])
        poss = dict_pos[word_tag_sub[0][1]].tolist()
        poso = dict_pos[word_tag_obj[0][1]].tolist()
        #主语和宾语的本身 对应的向量
        subvarr = dict_entity[subj]
        objvarr = dict_entity[obj]

        vectors.extend(wordVector)
        vectors.extend(poss)
        vectors.extend(poso)
        vectors.extend(subvarr)
        vectors.extend(objvarr)

        vectors.append(reSubjobjqueRule(sent))
        vectors.append(label)
        allvectors.append(vectors)
    return allvectors

def wVect(vectors,url):
    writes = open(url,'w+')
    for vector in vectors:
        for i in vector:
            writes.write(str(i)+' ')
        writes.write('\n')
def saveModel(trainsVect,numClass):
    trainsVect = np.array(trainsVect)
    train_y = trainsVect[:,-1]
    train_x = trainsVect[:,0:-1]
    xg_train = xgb.DMatrix(train_x, label=train_y)
    # setup parameters for xgboost
    param = {}
    # use softmax multi-class classification
    param['objective'] = 'multi:softmax'
    # scale weight of positive examples
    param['eta'] = 0.05
    param['max_depth'] = 6
    param['silent'] = 1
    param['nthread'] = 4
    param['num_class'] = numClass
    num_round = 500
    bst = xgb.train(param, xg_train,num_round)
    return bst

def predict(bst,testsVect):
    testsVect = np.array(testsVect)
    test_X = testsVect[:,0:-1]
    test_Y = testsVect[:,-1]
    xg_test = xgb.DMatrix(test_X, label=test_Y)
    pred = bst.predict(xg_test)
    print(classification_report(test_Y, pred,digits=3))
    confusion_matrix = metrics.confusion_matrix(test_Y, pred)
    print(confusion_matrix)

#关系分类，使用BOD把句子转化为向量 转化为多分类
if __name__=='__main__':
    printtime('load datas: ')
    attrs = ['spouse','song','mother','film','father','child','filmCastmember','songPerformer']

    alltemplates2 = getBoDtemplate.getTemplate(attrs)

    rawtrain = wEntityVector.getRawTrain(attrs, 'train')
    rawtest = wEntityVector.getRawTrain(attrs, 'test')
    dicttrain_pos = readFile.dictsubjobjpos(rawtrain)
    # print(dicttrain_pos)
    #wEntityVector.py得到这两个文件 分别是主语和宾语的向量表示
    dicttrain_entityurl = 'dictsWords/dicttrain.json'
    dicttest_entityurl = 'dictsWords/dicttest.json'


    dicttrain = json.load(open(dicttrain_entityurl))
    dicttest = json.load(open(dicttest_entityurl))

    url = 'onlyword'

    printtime(url+'start')
    all_train_vectors2 = allVectors(rawtrain,alltemplates2,dicttrain_pos,dicttrain)
    wVect(all_train_vectors2,'vectors/'+url+'_train2.txt')
    print('train 维数', len(all_train_vectors2[0]), len(all_train_vectors2))
    all_test_vectors2 = allVectors(rawtest,alltemplates2,dicttrain_pos,dicttest)
    print('test 维数', len(all_test_vectors2[0]), len(all_test_vectors2))
    wVect(all_test_vectors2,'vectors/'+url+'_test2.txt')
    printtime('vect over')
    all_model2 = saveModel(all_train_vectors2,8)
    joblib.dump(all_model2,'model/'+url+'_model2.model')
    predict(all_model2,all_test_vectors2,attrs)
    printtime('predict over')
