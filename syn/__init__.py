import subprocess
from .abcCmd import abcSyn, abcEval
from .yosysCmd import yosysSyn

ABC_PATH = 'tools/abc/abc'
YOSYS_PATH = 'tools/yosys/yosys'

def sysExec(sysCmd, verbose):
    ret = subprocess.check_output(sysCmd, shell=True).decode('utf-8')
    if verbose: print(ret)
    return ret

def syn(fin, fout, verbose=False, abcPath=ABC_PATH, yosysPath=YOSYS_PATH):
    assert fout.endswith('.aig')
    fout_ = fout.replace('.aig', '_orig.aig')
    #fout1, fout2 = fout + '.aig', fout + '_opt.aig' 
    log = fout.replace('.aig', '_info.json')
    sysExec(yosysSyn(fin, fout_, yosysPath), verbose)
    sysExec(abcSyn(fout_, fout, log, abcPath), verbose)
    return log

def eval(fn, binData, verbose=False, abcPath=ABC_PATH):
    assert fn.endswith('.aig')
    log = fn.replace('.aig', '_acc.json')
    sysExec(abcEval(fn, binData, log, abcPath), verbose)
    return log