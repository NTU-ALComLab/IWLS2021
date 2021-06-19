import math
from itertools import combinations as combs
from .svUtils import svTemplateTxt, svAssign, svModule, svVarGen, svBitPad, svBitSlice, svWrite

COMP_FLAG = 1

def genComparator_recur(sumList, i=0, maxId=0):
    if i == len(sumList) - 1:
        nCls = len(sumList)
        return '{}\'b{}'.format(str(nCls), ''.join(['1' if (j == (nCls-1-maxId)) else '0' for j in range(nCls)]))
    cond = sumList[maxId] + ' >= ' + sumList[i+1]
    state1 = genComparator_recur(sumList, i+1, maxId)
    state0 = genComparator_recur(sumList, i+1, i+1)
    return '({}) ? ({}) : ({})'.format(cond, state1, state0)

def genComparator1(sumList):
    return svAssign('pred', genComparator_recur(sumList))

def genComparator2(sumList):
    ret = ''
    nClass = len(sumList)
    for i in range(nClass):
        comp = ['({} >= {})'.format(sumList[i], sumList[j]) for j in range(nClass)]
        #ret += svAssign('pred[{}]'.format(str(i)), ' & '.join(comp))
        ret += svAssign(svBitSlice('pred', i), ' & '.join(comp))
    return ret

def genComparator(sumList, fBin):
    # use single output
    if fBin:
        assert len(sumList) == 2
        return svAssign('pred', '({} >= {}) ? (1\'b0) : (1\'b1)'.format(sumList[0], sumList[1]))
    
    # general case
    if COMP_FLAG == 1:
        return genComparator1(sumList)
    elif COMP_FLAG == 2:
        return genComparator2(sumList)
    else:
        raise NotImplementedError()

def BinVoter_dir(nClass, clfList):
    assert len(clfList) == 1
    ios = [('data_{}'.format(str(i)), ) * 2 for i in range(32*32*3)] + [('pred', 'pred')]
    body = svModule(clfList[0], 0, ios)
    return '', body

def BinVoter_oaa(nClass, clfList):
    raise NotImplementedError()

def bvPrep(nClass, clfList, nSumBit, nOut=1):
    predList = [c + '_pred' for c in clfList]
    sumList = ['sum_{}'.format(str(i)) for i in range(nClass)]

    vvars = svVarGen([('wire', nOut, predList[i], 1) for i in range(len(clfList))]) \
           + svVarGen([('wire', nSumBit, sumList[i], 1) for i in range(nClass)])

    body = ''
    # connect to clf modules
    for p, clf in zip(predList, clfList):
        #body += svModule(clf, 0, [('data', 'data'), ('pred', p)])
        ios = [('data_{}'.format(str(i)), ) * 2 for i in range(32*32*3)] + [('pred', p)]
        body += svModule(clf, 0, ios)
    body += '\n'

    return predList, sumList, vvars, body

def bvPost(sumList, accList, fBin=False):
    ret = ''
    for i, j in zip(sumList, accList):
        ret += svAssign(i, ' + '.join(j))

    # find the max vote
    #body += svAssign('pred', genComparator_recur(sumList))
    ret += genComparator(sumList, fBin)
    return ret

def BinVoter_gag(nClass, clfList):
    nSumBit = math.ceil(math.log2(len(clfList) + 1))
    predList, sumList, vvars, body = bvPrep(nClass, clfList, nSumBit)

    # accumulate votes
    accList = [[] for _ in range(nClass)]
    for i, s in enumerate(combs(range(nClass), nClass//2)):
        if i >= len(clfList): break
        s = set(s)
        for j in range(nClass):
            beg = '' if (j in s) else '~'
            #accList[j].append(beg + predList[i])
            accList[j].append(svBitPad(beg + predList[i], nSumBit-1))

    body += bvPost(sumList, accList)

    return vvars, body

def BinVoter_oao(nClass, clfList):
    nSumBit = math.ceil(math.log2(nClass)) *10
    predList, sumList, vvars, body = bvPrep(nClass, clfList, nSumBit)

    # accumulate votes
    accList = [[] for _ in range(nClass)]
    for i, s in enumerate(combs(range(nClass), 2)):
        #accList[s[0]].append('{{{}, {}}}'.format(head, '~' + predList[i]))
        #accList[s[1]].append('{{{}, {}}}'.format(head, predList[i]))
        accList[s[0]].append(svBitPad('~' + predList[i], nSumBit-1))
        accList[s[1]].append(svBitPad(predList[i], nSumBit-1))

    body += bvPost(sumList, accList)

    return vvars, body
    
def BinVoter_write(fn, mode, nClass, clfList):
    name = fn.split('/')[-1].replace('.v', '')
    ios = ['data_{}'.format(str(i)) for i in range(32*32*3)] + ['pred']
    #vars = svVarGen([('input', 8, 'data', 32*32*3), ('output', nClass, 'pred', 1)])
    vvars = svVarGen([('input', 8, 'data_{}'.format(i), 1) for i in range(32*32*3)])
    vvars += svVarGen([('output', nClass, 'pred', 1)])

    if mode == 'dir':
        nvars, body = BinVoter_dir(nClass, clfList)
    elif mode == 'oaa':
        nvars, body = BinVoter_oaa(nClass, clfList)
    elif mode == 'gag':
        nvars, body = BinVoter_gag(nClass, clfList)
    elif mode == 'oao':
        nvars, body = BinVoter_oao(nClass, clfList)
    else:
        assert False
    
    with open(fn, 'w') as fp:
        s = svWrite(name, ', '.join(ios), vvars + nvars, body)
        fp.write(s)