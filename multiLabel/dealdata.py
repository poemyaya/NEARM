# -*- coding: utf-8 -*-
import json
def readDatas(lines):
    alldatas = []
    for line in lines:
        line = line.strip()
        line = json.loads(line)
        alldatas.append(line)
    return alldatas
#第二步 将训练集数据存成magpie需要的格式
if __name__=='__main__':
    urlsent = open('data/allsents_train_place.txt').readlines()
    urllabel = open('data/alllabel_train_place.txt').readlines()
    preurl = 'data/hep-categories/'
    allsents = readDatas(urlsent)
    alllabels = readDatas(urllabel)
    print(len(allsents),len(alllabels))
    for i in range(len(alllabels)):
        writes1 = open(preurl+str(i)+'.txt','w',encoding='utf-8')
        writes1.write(allsents[i])
        writes2 = open(preurl+str(i)+'.lab','w',encoding='utf-8')
        for la in alllabels[i]:
            writes2.write(la+'\n')
