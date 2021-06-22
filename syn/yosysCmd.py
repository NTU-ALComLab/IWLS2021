import os

def yosysCmd(cmd, yosysPath):
    #yosysBin = os.path.join(yosysPath, 'yosys')
    cmd = '; '.join(cmd)
    cmd = '{} -QTp "{}"'.format(yosysPath, cmd)
    return cmd

def yosysSyn(fin, fout, yosysPath):
    cmd = ['read_verilog {}'.format(fin)]
    cmd += ['hierarchy -auto-top']
    cmd += ['proc', 'opt', 'flatten', 'opt', 'techmap', 'opt', 'aigmap', 'opt']
    cmd += ['write_aiger {}'.format(fout)]
    return yosysCmd(cmd, yosysPath)