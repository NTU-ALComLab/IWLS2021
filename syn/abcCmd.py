import os

def abcCmd(cmd, abcPath):
    #abcBin = os.path.join(abcDir, 'abc')
    cmd = ['source {}.rc'.format(abcPath)] + cmd
    cmd = '; '.join(cmd)
    cmd = '{} -q "{}"'.format(abcPath, cmd)
    return cmd

def abcSyn(fin, fout, log, abcPath):
    cmd = ['r {}'.format(fin)]
    cmd += ['resyn', 'resyn2', 'resyn2a', 'resyn3', 'resyn2rs']
    cmd += ['dc2', 'dc2 -b'] * 3
    cmd += ['&get', '&w {}'.format(fout), '&ps -D {}'.format(log)]
    return abcCmd(cmd, abcPath)

def abcEval(fn, binData, log, abcPath):
    cmd = ['&iwls21test -D {} {} {}'.format(log, fn, binData)]
    return abcCmd(cmd, abcPath)
