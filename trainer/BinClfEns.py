import math
from itertools import combinations as combs
from .svUtils import svTemplateTxt, svAssign, svModule, svVarGen

def genComparator_recur(sumList, i=0, maxId=0):
    if i == len(sumList) - 1:
        nCls = len(sumList)
        return '{}\'b{}'.format(str(nCls), ''.join(['1' if (j == maxId) else '0' for j in range(nCls)]))
    cond = sumList[maxId] + ' >= ' + sumList[i+1]
    state1 = genComparator_recur(sumList, i+1, maxId)
    state0 = genComparator_recur(sumList, i+1, i+1)
    return '({}) ? ({}) : ({})'.format(cond, state1, state0)

def BinVoter_dir(nClass, clfList):
    assert len(clfList) == 1
    body = svModule(clfList[0], 0, [('data', 'data'), ('pred', 'pred')])
    return '', body

def BinVoter_oaa(nClass, clfList):
    raise NotImplementedError()

def BinVoter_gag(nClass, clfList):
    predList = [c + '_pred' for c in clfList]
    nSumBit = math.ceil(math.log2(len(clfList) + 1))
    sumList = ['sum_{}'.format(str(i)) for i in range(nClass)]

    vars = svVarGen([('wire', 1, predList[i], 1) for i in range(len(clfList))]) \
           + svVarGen([('wire', nSumBit, sumList[i], 1) for i in range(nClass)])
    
    body = ''
    # connect to clf modules
    for p, clf in zip(predList, clfList):
        body += svModule(clf, 0, [('data', 'data'), ('pred', p)])
    body += '\n'

    # accumulate votes
    accList = [[] for _ in range(nClass)]
    for i, s in enumerate(combs(range(nClass), 2)):
        if i >= len(clfList): break
        s = set(s)
        for j in range(nClass):
            beg = '' if (j in s) else '~'
            accList[j].append(beg + predList[i])
    for i, j in zip(sumList, accList):
        body += svAssign(i, ' + '.join(j))

    # find the max vote
    body += svAssign('pred', genComparator_recur(sumList))
    return vars, body

def BinVoter_oao(nClass, clfList):
    predList = [c + '_pred' for c in clfList]
    nSumBit = math.ceil(math.log2(nClass))
    sumList = ['sum_{}'.format(str(i)) for i in range(nClass)]

    vars = svVarGen([('wire', 1, predList[i], 1) for i in range(len(clfList))]) \
           + svVarGen([('wire', nSumBit, sumList[i], 1) for i in range(nClass)])
    
    body = ''
    # connect to clf modules
    for p, clf in zip(predList, clfList):
        body += svModule(clf, 0, [('data', 'data'), ('pred', p)])
    body += '\n'

    # accumulate votes
    accList = [[] for _ in range(nClass)]
    for i, s in enumerate(combs(range(nClass), 2)):
        accList[s[0]].append('~' + predList[i])
        accList[s[1]].append(predList[i])
    for i, j in zip(sumList, accList):
            body += svAssign(i, ' + '.join(j))

    # find the max vote
    body += svAssign('pred', genComparator_recur(sumList))
    return vars, body
    

def BinVoter_write(fn, mode, nClass, clfList):
    name = fn.split('/')[-1].replace('.sv', '')
    ios = 'data, pred'
    vars = svVarGen([('input', 8, 'data', 32*32*3), ('output', nClass, 'pred', 1)])

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
    
    s = svTemplateTxt.replace('MODULE', name) \
             .replace('IOPORTS', ios) \
             .replace('VARS', vars + nvars) \
             .replace('BODY', body)

    with open(fn, 'w') as fp:
        fp.write(s)