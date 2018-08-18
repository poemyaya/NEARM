# -*- coding: utf-8 -*-
import json
import time
import getBoDtemplate,getRules,getVector,readFile,wEntityVector
import xgboost as xgb
import nltk
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


def allVectors(trains,allrules,alltemplates,allwikiDatas,dict_pos,dict_entity):
    allvectors = []
    for data in trains:
        subj = data[0]
        obj = data[1]
        sent = data[2]
        label = data[3]
        vectors = []
        ruleVector = getVector.reVectorSetRules(sent,allrules,allwikiDatas)
        wordVector = getVector.reVectorWords(sent, alltemplates)


        word_tag_sub = nltk.pos_tag([subj])
        word_tag_obj = nltk.pos_tag([obj])
        poss = dict_pos[word_tag_sub[0][1]].tolist()
        poso = dict_pos[word_tag_obj[0][1]].tolist()
        subvarr = dict_entity[subj]
        objvarr = dict_entity[obj]


        vectors.extend(ruleVector)
        vectors.extend(wordVector)
        vectors.extend(poss)
        vectors.extend(poso)
        vectors.extend(subvarr)
        vectors.extend(objvarr)

        vectors.append(reSubjobjqueRule(sent))
        vectors.append(label)
        allvectors.append(vectors)
    return allvectors

def wVect(vectors,type):
    writes = open(type+'_vectors.txt','w+')
    for vector in vectors:
        for i in vector:
            writes.write(str(i)+' ')
        writes.write('\n')
def saveModel(trainsVect):
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
    param['num_class'] = 8
    num_round = 500
    bst = xgb.train(param, xg_train,num_round)
    return bst

def predict(bst,testsVect,target_names):
    testsVect = np.array(testsVect)
    test_X = testsVect[:,0:-1]
    test_Y = testsVect[:,-1]
    xg_test = xgb.DMatrix(test_X, label=test_Y)
    pred = bst.predict(xg_test)
    print(classification_report(test_Y, pred, target_names=target_names,digits=3))
    confusion_matrix = metrics.confusion_matrix(test_Y, pred)
    print(confusion_matrix)

#把规则后件使用one-hot编码 当做特征 拼接到句子特征上
if __name__=='__main__':
    printtime('load datas: ')
    attrs = ['spouse','song','mother','film','father','child','filmCastmember','songPerformer']
    allwikiDatas = readFile.readWikidatas('/home/ren/remote/TwolLayer208/wikidatas/all_wikidatas.csv')
    allRules1, allRules2, allRules3 = getRules.reRulesLevel(attrs)
    alltemplates2 = getBoDtemplate.getTemplate(attrs)

    rawtrain = wEntityVector.getRawTrain(attrs, 'train')
    rawtest = wEntityVector.getRawTrain(attrs, 'test')
    dicttrain_pos = readFile.dictsubjobjpos(rawtrain)

    dicttrain_entityurl = 'dictsWords/dicttrain.json'
    dicttest_entityurl = 'dictsWords/dicttest.json'


    dicttrain = json.load(open(dicttrain_entityurl))
    dicttest = json.load(open(dicttest_entityurl))

    printtime('rules_two+words start')
    all_train_vectors2 = allVectors(rawtrain,allRules2,alltemplates2,allwikiDatas,dicttrain_pos,dicttrain)
    wVect(all_train_vectors2,'vectors/Setall_train2.txt')
    print('train 维数', len(all_train_vectors2[0]), len(all_train_vectors2))
    all_test_vectors2 = allVectors(rawtest,allRules2,alltemplates2,allwikiDatas,dicttrain_pos,dicttest)
    print('test 维数', len(all_test_vectors2[0]), len(all_test_vectors2))
    wVect(all_test_vectors2,'vectors/Setall_test2.txt')
    printtime('vect over')
    all_model2 = saveModel(all_train_vectors2)
    joblib.dump(all_model2,'model/Setall_model2.model')
    predict(all_model2,all_test_vectors2,attrs)
    printtime('predict over')
