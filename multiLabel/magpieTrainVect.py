# -*- coding: utf-8 -*-
from magpie import Magpie
import json
def getlabel(url):
    lines = open(url).readlines()
    alllabel = []
    for line in lines:
        line = line.strip()
        alllabel.append(line)
    return alllabel

#第四步 训练模型预测测试集的标签
if __name__=='__main__':

    labels = getlabel('/home/ydm/ren/remote/multiLabel/data/labels.txt')
    # magpie = Magpie(
    #     keras_model='/home/ydm/ren/remote/multiLabel/data/here.h5',
    #     word2vec_model='/home/ydm/ren/remote/multiLabel/data/word2vec_mode',
    #     scaler='/home/ydm/ren/remote/multiLabel/data/scaler',
    #     labels=labels
    # )

    magpie = Magpie()
    magpie.init_word_vectors('/home/ydm/ren/remote/multiLabel/data/hep-categories', vec_dim=100)

    print(len(labels))
    magpie.train('/home/ydm/ren/remote/multiLabel/data/hep-categories', labels, epochs=30, batch_size=128)
    magpie.save_word2vec_model('/home/ydm/ren/remote/multiLabel/data/word2vec_mode_place')
    magpie.save_scaler('/home/ydm/ren/remote/multiLabel/data/scaler_place', overwrite=True)
    magpie.save_model('/home/ydm/ren/remote/multiLabel/data/model_place.h5')

    alltest = getlabel('/home/ydm/ren/remote/multiLabel/data/allsents_test.txt')
    # alltest = [alltest]
    writes = open('/home/ydm/ren/remote/multiLabel/data/result_place.txt','w',encoding='utf-8')

    for sent in alltest:
        # print(sent)
        pre_result = magpie.predict_from_text(sent)[:30]
        # print(pre_result)
        resultDict = {}
        for item in pre_result:
            resultDict[item[0]] = float(item[1])
        writes.write(json.dumps(resultDict) + '\n')
