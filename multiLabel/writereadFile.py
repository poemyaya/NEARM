# -*- coding: utf-8 -*-
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
