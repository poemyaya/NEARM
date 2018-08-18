# -*- coding: utf-8 -*-
import writereadFile

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

#第三步 得到所有的标签集合
if __name__=='__main__':
    #song,'spouse','mother','film','father','child','filmCastmember','songPerformer'
    attrlist=['spouse','song','mother','film','father','child','filmCastmember','songPerformer']
    alllabels = set()
    for attr_i in range(len(attrlist)):
        attr = attrlist[attr_i]
        wikiDatas = writereadFile.readWikidatas('/home/ydm/ren/remote/ruleMining2/wikidatas/' + attr + '_wikidata.csv')
        trains = writereadFile.readContent('/home/ydm/ren/remote/ruleMining2/outdatas_baseline/train_' + attr + '.csv')
        allsentvalue = sentValue(wikiDatas, trains)
        for item in allsentvalue:
            for im in item:
                alllabels.add(im)
    print(len(alllabels))
    writes = open('data/labels.txt','w',encoding='utf-8')
    for la in alllabels:
        writes.write(la+'\n')
