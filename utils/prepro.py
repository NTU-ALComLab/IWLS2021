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
# n has to be the divisor of image height/width
# case: stride = 2 (3,4...)
#       10101010...
#       00000000...
#       10101010...
# if n < 0: perform data augmentation with offset
def imgDownSample(data, n=1):
    n, fAug = abs(n), (n < 0)
    assert isinstance(n, int) and (n >= 1)
    assert (data.shape[2] % n == 0) and (data.shape[3] % n == 0)
    if not fAug:
        return data[:, :, ::n, ::n]
    
    ret = [data[:, :, i::n, i::n] for i in range(n)]
    #####
    ## TODO: there should be more different offset settings
    ## Should be as follows (not tested):
    ## ret = [data[:, :, i::n, j::n] for i in range(n) for j in range(n)]
    #####
    
    return np.concatenate(ret)
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
# TODO: should change this function to channel selection
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
    #toBin = lambda x, k: np.array(list(np.binary_repr(x, k)), dtype=np.uint8)
    ret = []
    for i in range(n):
        ret.append((data >> i) & 1)
    return np.stack(ret, axis=-1)

# checking image property
def imgCheck(data):
    return data.shape[2] == data.shape[3]

# pad the image with 0s to its original size (n_data, 3, 32, 32) and 8-bit precision
def imgPad(data, fMergeCh, nLSB):
    assert data.shape[2] == data.shape[3]
    assert 32 % data.shape[2] == 0
    assert (fMergeCh is None) or (sum(fMergeCh) == 1)

    k = 32 // data.shape[2]
    ret = np.zeros((data.shape[0], data.shape[1], 32, 32), dtype=np.uint8)
    ret[:, :, ::k, ::k] = (data << nLSB)

    if fMergeCh is not None:
        assert data.shape[1] == 1
        fill = np.zeros((data.shape[0], 1, 32, 32), dtype=np.uint8)
        ret = [ret if fm else fill for fm in fMergeCh]
        ret = np.concatenate(ret, axis=1)
    
    assert ret.shape == (data.shape[0], 3, 32, 32)
    return ret

# overall image prepocessing
def imgPrepro(data, labels=None, nPeel=0, nStride=1, fMergeCh=None, nLSB=0, fBlast=False, fPad=True):
    if labels is None:
        nStride = abs(nStride)
    ret = imgPeel(data, nPeel)
    ret = imgDownSample(ret, nStride)
    if fMergeCh is not None:
        ret = imgMergeChannel(ret, fMergeCh)
    ret = imgRemoveLSB(ret, nLSB)
    if fPad:
        ret = imgPad(ret, fMergeCh, nLSB)
    if fBlast:
        ret = imgBitBlast(ret, 8 if fPad else (8-nLSB))
    assert imgCheck(ret)
    
    if labels is None: return ret

    assert (len(data) == len(labels)) and (type(labels) == list)
    if nStride > 0:
        assert len(ret) == len(labels)
    else:
        assert len(ret) % len(labels) == 0
    return ret, labels * (len(ret) // len(labels))