#encoding:utf-8
'''
@author:Guo Yingmei
@created:2017.07.18
'''
import operator
import random
import math
import data
import marshal
import gzip
def rand_mat(rows,cols):
    ret=[]
    for i in xrange(rows):
        ret.append([])
        for j in xrange(cols):
            ret[-1].append(random.random())
        norm=sum(ret[-1])
        for j in xrange(cols):
            ret[-1][j]/=norm
    return ret
class PLSA:
    def __init__(self,corpus,topics=5):
        self.topics=topics#种类数
        self.corpus=corpus#传入的文档集合
        self.docs=len(corpus)#文档的数量
        self.num=map(sum,map(lambda x:x.values(),corpus))#list,每个文档单词出现次数总和
        self.numofwords=max(reduce(operator.add,map(lambda x:x.keys(),corpus)))+1#单词的个数,即决定序号
        self.zw=rand_mat(self.topics,self.numofwords)
        self.dz=rand_mat(self.docs,self.topics)
        self.dw_z=None
        self.p_dw=[] #list,其中的元素是字典,选定d,w出现的概率
        self.beta=0.8

    def save(self,fname,iszip=True):
        d={}
        for k,v in self.__dict__.items():
            if hasattr(v,'__dict__'):
                d[k]=v.__dict__
            else:
                d[k]=v
        if not iszip:
            marshal.dump(d,open(fname,'wb'))
        else:
            f=gzip(fname,'wb')
            f.write(marshal.dumps(d))
            f.close()

    def load(self,fname,iszip=True):
        if not iszip:
            d=marshal.load(open(fname,'rb'))
        else:
            f=open(fname,'rb')
            d=marshal.load(f.read())
            f.close()
        for k,v in d.items():
            if hasattr(self.__dict__[k],'__dict__'):
                self.__dict__[k].__dict__=v
            else:
                self.__dict__[k]=v

    def cal_p_dw(self):
        self.p_dw=[]
        for d in xrange(self.docs):
            self.p_dw.append({})
            for w in self.corpus[d]:
                tmp=0
                for j in xrange(self.corpus[d][w]):#单词的出现次数即代表了权重
                    for z in xrange(self.topics):
                        tmp+=(self.zw[z][w]*self.dz[d][z])**self.beta
                self.p_dw[-1][w]=tmp

    def e_step(self):
        self.cal_p_dw()
        self.dw_z=[]
        for d in xrange(self.docs):
            self.dw_z.append({})
            for w in self.corpus[d]:
                self.dw_z[-1][w]=[]
                for z in xrange(self.topics):
                    self.dw_z[-1][w].append(((self.zw[z][w]*self.dz[d][z])**self.beta)/self.p_dw[d][w])

    def m_step(self):
        for z in xrange(self.topics):
            self.zw[z]=[0]*self.numofwords
            for d in xrange(self.docs):
                for w in self.corpus[d]:
                    self.zw[z][w]+=self.corpus[d][w]*self.dw_z[d][w][z]
            norm=sum(self.zw[z])
            for w in xrange(self.numofwords):
                self.zw[z][w]/=norm
        for d in xrange(self.docs):
            self.dz[d]=[0]*self.topics
            for z in xrange(self.topics):
                for w in self.corpus[d]:
                    self.dz[d][z]+=self.corpus[d][w]*self.dw_z[d][w][z]
            for z in xrange(self.topics):
                self.dz[d][z]/=self.num[d]

    def cal_likelihood(self):
        self.likelihood=0
        for d in xrange(self.docs):
            for w in self.corpus[d]:
                self.likelihood+=self.corpus[d][w]*math.log(self.p_dw[d][w])

    def train(self,max_iter=100):
        cur=0
        for i in xrange(max_iter):
            print '%d iter'% i
            self.e_step()
            self.m_step()
            self.cal_likelihood()
            print 'likelihood %f' % self.likelihood
            if cur!=0 and abs((self.likelihood-cur)/cur)< 1e-8:
                break
            cur=self.likelihood

    def inference(self,doc,max_iter=100):
        doc=dict(filter(lambda x:x[0]<self.numofwords,doc.items()))
        words=sum(doc.values())
        ret=[]
        for i in xrange(self.topics):
            ret.append(random.random())
        norm=sum(ret)
        for i in xrange(self.topics):
            ret[i]/=norm
        tmp=0
        for _ in xrange(max_iter):
            p_dw={}
            for w in doc.keys():
                p_dw[w]=0
                for _ in range(doc[w]):
                    for z in xrange(self.topics):
                        p_dw[w]+=(ret[z]*self.zw[z][w])**self.beta
                if p_dw[w]==0:#防止后面的除数为0
                    p_dw[w]=1e-8
            dw_z={}
            for w in doc:
                dw_z[w]=[]
                for z in xrange(self.topics):
                    dw_z[w].append(((self.zw[z][w]*ret[z])**self.beta)/p_dw[w])
            ret=[0]*self.topics
            for z in xrange(self.topics):
                ret[z]+=doc[w]*dw_z[w][z]
            for z in xrange(self.topics):
                ret[z]/=words
            likelihood=0
            for w in doc:
                likelihood+=doc[w]*math.log(p_dw[w])
            if tmp!=0 and abs((likelihood-tmp)/tmp)< 1e-8:
                break
            tmp=likelihood
        return ret



if __name__=="__main__":
    corpus=[{0:2,3:5},{0:5,2:1},{1:2,4:5}]
    p=PLSA(corpus)
    p.train()
    z = p.inference({0:4,2:4,8:3})
    print z


