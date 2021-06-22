from .abcCmd import abcSyn, abcParseInfo, abcEval, abcGetAcc
from .yosysCmd import yosysSyn

ABC_PATH = 'tools/abc'
YOSYS_PATH = 'tools/yosys'

def sysExec(sysCmd):
    ret = subprocess.check_output(sysCmd, shell=True)
    return ret.decode('utf-8')

def syn(fin, fout, abcPath=ABC_PATH, yosysPath=YOSYS_PATH):
    fout1, fout2 = fout + '.aig', fout + '_opt.aig' 
    sysExec(yosysSyn(fin, fout1, yosysPath))
    stat = sysExec(abcSyn(fout1, fout2, abcPath))
    ret = abcParseInfo(stat)
    return ret

def eval(fn, binData, abcPath=ABC_PATH):
    stat = sysExec(abcEval(fn, binData, abcPath))
    ret = abcGetAcc(stat)
    return ret