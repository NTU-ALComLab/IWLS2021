import numpy as np
# data shape: (n_data, n_channel, img_length, img_width)

# remove the outermost n layers of the image
def imgPeel(data, n=0):
    assert isinstance(n, int)
    if n == 0: return data
    ret = []
    for dat in data:
        new = []
        for ch in dat:
            img = []
            if 2*n > len(ch):
                print('Cannot peel {} layers of a {}x{} image.'.format(str(n), str(len(ch)), str(len(ch))))
                return data
            for x in ch[n:-n]:
                img.append(x[n:-n])
            new.append(img)
        ret.append(new)
    return np.array(ret, dtype=np.uint8)

# down-sample the pixels with the specified stride
# case: stride = 2 (3,4...)
#       10101010...
#       00000000...
#       10101010...
def imgDownSample(data, n=1):
    assert isinstance(n, int) and (n >= 1)
    return data[:, :, ::n, ::n]
    """
    ret = []
    for dat in data:
        new = []
        for ch in dat:
            img = []
            m = (len(ch) // 2) * 2
            for i in range(len(ch)):
                if i % 2 == 0:
                    img.append(ch[i][0:m:2])
                else:
                    img.append(ch[i][1:m:2])
            new.append(img)
        ret.append(new)
    return np.array(ret, dtype=np.uint8)
    """  

# merge channels into one
# flag: specify which channel is used
def imgMergeChannel(data, flag=(True, True, True)):
    assert len(flag) == 3
    s = [i for i in range(3) if flag[i]]
    ret = np.sum(data[:, s], axis=1, keepdims=True) / len(s)
    return np.round(ret).astype(np.uint8)

# remove n LSBs
def imgRemoveLSB(data, n=0):
    assert isinstance(n, int) and (n >=0) and (n < 8)
    return data >> n

# bit blast the image vectors
# n: number of bits
def imgBitBlast(data, n=8):
    assert isinstance(n, int) and (n >=0) and (n <= 8)
    ret = []
    for i in range(n):
        ret.append((data >> n) & 1)
    return np.stack(ret, axis=-1)

# checking image property
def imgCheck(data):
    return data.shape[2] == data.shape[3]

# overall image prepocessing
def imgPrepro(data, nPeel=0, nStride=1, fMergeCh=None, nLSB=0, fBlast=True):
    ret = imgPeel(data, nPeel)
    ret = imgDownSample(ret, nStride)
    if fMergeCh is not None:
        ret = imgMergeChannel(ret, fMergeCh)
    ret = imgRemoveLSB(ret, nLSB)
    if fBlast:
        ret = imgBitBlast(ret, 8-nLSB)
    assert imgCheck(ret)
    return ret