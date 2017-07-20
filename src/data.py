#encoding:utf-8
"""
@author:Guo Yingmei
@created:2017.07.16
"""
import chardet
import jieba
import jieba.posseg as pseg
import numpy as np
import re
def getStopWord():
    fopen=open('../data/stopWord.txt','r')
    list=[]
    for line in fopen:
        line=line.strip()#必须要赋值
        line=line.decode('utf-8')#将utf-8的字符串转换成unicode,便于之后的比较
        list.append(line)
    return list

def getComment():
    input_fname='../data/trainData.txt'
    output_fname='../data/test_pre.txt'
    input_r=open(input_fname,'r')
    output_w=open(output_fname,'w')

    stopWordList=getStopWord()
    mark=0
    tvName='穆桂英挂帅'
    output_w.write(tvName+'\n')
    for line in input_r:
        line=line.split('\t')
        if(tvName!=line[1].strip()):
            output_w.write('\n')
            tvName=line[1].strip()
            output_w.write(tvName+'\n')
        result=line[3].strip()
        result=pseg.cut(result)
        for w in result:#删除停止词
            if w.word in stopWordList:
                continue
            output_w.write(w.word.encode('utf-8')+'/'+w.flag.encode('utf-8')+'\t')

def getComment2():
    input_fname='../data/trainData.txt'
    output_fname='../data/cutComment.txt'
    input_r=open(input_fname,'r')
    output_w=open(output_fname,'w')

    stopWordList=getStopWord()
    for line in input_r:
        line=line.split('\t')
        result=line[3].strip()
        result=pseg.cut(result)
        for w in result:#删除停止词
            if w.word in stopWordList:
                continue
            output_w.write(w.word.encode('utf-8')+'/'+w.flag.encode('utf-8')+'\t')
        output_w.write('\n')


def countWord():
    input_fname='../data/cutComment.txt'
    output_fname='../data/wordCount2.txt'

    input_r=open(input_fname,'r')
    output_w=open(output_fname,'w')
    wc={}
    for line in input_r:
        line=line.strip()
        line=line.split('\t')
        for w in line:
            if w in wc:
                wc[w]+=1
            else:
                wc[w]=1
    wc=wc.items()
    wc=sorted(wc,key=lambda t:(-t[1],t[0]))
    for w,c in wc:
        if c>=2:
            line='%s\t%d\n'%(w,c)
            output_w.write(line)
def filter():
    input_fname1='../data/cutComment.txt'
    input_fname2='../data/wordCount2.txt'
    output_fname='../data/wordCount3.txt'

    input_r2=open(input_fname2,'r')
    output_w=open(output_fname,'w')

    wc={}
    for line in input_r2:
        #line=line.strip()
        line=line.split('\t')
        word=line[0]#.strip()
        line[1]=line[1].strip()
        num=0
        with open(input_fname1) as input_r1:
            for com in input_r1:
                com=com.strip()
                com=com.split('\t')
                for i in com:
                    i=i.strip()
                    if i==word:
                        num+=1
                        break
                if num==2:
                    wc[line[0]]=int(line[1])
                    break
    wc=wc.items()
    wc=sorted(wc,key=lambda t:(-t[1],t[0]))
    for w,c in wc:
        line='%s\t%d\n' % (w,c)
        output_w.write(line)

def Chinese_word_extraction(text):#去除英文
        chinese_pattern = u"([\u4e00-\u9fff]+)"
        re_data = re.findall(chinese_pattern,text)#能够以列表的方式返回所有的子串
        result=''
        for i in re_data:
            result+=i
        return result

def getWord():
    ret={}
    input_fname='../data/wordCount3.txt'
    input_r=open(input_fname)
    index=0
    for line in input_r:
        line=line.strip()
        line=line.split('\t')
        ret[line[0]]=index
        index+=1
    return ret

def getInput():
    input_fname1='../data/cutComment.txt'
    input_fname2='../data/wordCount3.txt'
    fopen1=open(input_fname1,'r')
    fopen2=open(input_fname2,'r')

    wordList=getWord()
    corpus=[]
    for line in fopen1:
        corpus.append({})
        line=line.strip()
        line=line.split('\t')
        for w in line:
            if w in wordList:
                if wordList[w] in corpus[-1]:
                    corpus[-1][wordList[w]]+=1
                else:
                    corpus[-1][wordList[w]]=1
        if not corpus[-1]:
            corpus.pop()
    return corpus