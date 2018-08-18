# -*- coding: utf-8 -*-
import writereadFile,savereadFile
import json
def sentValue(wikidata,sents):
    allsentValues = []
    for i_sent in range(len(sents)):
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
        allsentValues.append(itemInfo)
    return allsentValues

def writeDatas(datas,url):
    writes = open(url,'w',encoding='utf-8')
    for data in datas:
        writes.write(json.dumps(data)+'\n')

#第一步 把训练集的句子，以及句子对应的标签存成两个文件allsents_train_place.txt、alllabel_train_place.txt
#测试集通过同样方式得到真实标签
if __name__=='__main__':
    #song,'spouse','mother','film','father','child','filmCastmember','songPerformer'
    attrlist=['spouse','song','mother','film','father','child','filmCastmember','songPerformer']
    alllabels = []
    allpladatas = []

    for attr_i in range(len(attrlist)):
        attr = attrlist[attr_i]
        wikiDatas = writereadFile.readWikidatas('/home/ydm/ren/remote/ruleMining2/wikidatas/' + attr + '_wikidata.csv')
        trains = writereadFile.readContent('/home/ydm/ren/remote/ruleMining2/outdatas_baseline/train_' + attr + '.csv')
        allsentvalue = sentValue(wikiDatas, trains)
        print(attr,len(allsentvalue),len(trains))
        alllabels.extend(allsentvalue)

        allsents = savereadFile.getRawTrain(attr,'train')
        for sentlist in allsents:
            subname = sentlist[0]
            objname = sentlist[1]
            pladata = sentlist[2]
            subjPlace = sentlist[3]
            objPlace = sentlist[4]
            # newsents = pladata.replace(subjPlace,subname)
            # newsents = newsents.replace(objPlace,objname)
            allpladatas.append(pladata)

    print(len(allpladatas),len(alllabels))
    writeDatas(allpladatas, 'data/allsents_train_place.txt')
    writeDatas(alllabels, 'data/alllabel_train_place.txt')

