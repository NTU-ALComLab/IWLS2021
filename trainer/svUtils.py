# templates
svTemplateTxt = \
'''
module MODULE(
    IOPORTS
);

VARS

BODY

endmodule
'''

svModuleTxt = \
"""
MODULE MODULE_inst_IDX(IOPORTS);
"""

# generate var (io/wire) texts
# varList: list of tuples (var_type, n_bits, port_name, array_len)
def svVarGen(varList):
    assert len(varList) > 0

    getNB = lambda n: '' if (n == 1) else '[{}:0]'.format(str(n - 1))
    getAL = lambda n: '' if (n == 1) else '[0:{}]'.format(str(n - 1))

    ret = []
    for x in varList:
        assert (len(x) == 4) and (x[0] in {'input', 'output', 'wire'}) and (x[1] > 0) and (x[3] > 0)
        ret.append('{} {} {} {};\n'.format(x[0], getNB(x[1]), x[2], getAL(x[3])))
    
    return ''.join(ret)

# assign var = val;
def svAssign(vvar, val):
    return 'assign {} = {};\n'.format(vvar, val)

# ioList: list of (module port, wire) tuples
def svModule(name, idx, ioList):
    ios = ', '.join(['.{}({})'.format(i, j) for i, j in ioList])
    ret = svModuleTxt.replace('MODULE', name) \
                     .replace('IDX', str(idx)) \
                     .replace('IOPORTS', ios)
    return ret

def svBitPad(vvar, n):
    pad = '{}\'d0'.format(str(n))
    return '{{{}, {}}}'.format(pad, vvar)

def svBitSlice(vvar, start, end=None):
    assert isinstance(start, int) and (start >= 0)
    if end is None:
        return '{}[{}]'.format(vvar, str(start))
    else:
        assert isinstance(end, int) and (end >= 0)
        return  '{}[{}:{}]'.format(vvar, str(start), str(end))