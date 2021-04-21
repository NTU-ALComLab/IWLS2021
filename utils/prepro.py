import numpy as np
# data shape: (n_data, n_channel, img_length, img_width)

# remove the outermost n layers of the image
def imgPeel(data, n=1):
    assert isinstance(n, int)
    ret = []
    for dat in data:
        img = []
        for ch in dat:
            if 2*n > len(ch):
                print('Cannot peel {} layers of a {}x{} image.'.format(str(n), str(len(ch)), str(len(ch))))
                return data
            for x in ch[n:-n]:
                img.append(x[n:-n])
        ret.append(img)
    return np.array(ret, dtype=np.uint8)

# down-sample the pixels with the specified stride
# case: stride = 0.5
#       10101010...
#       01010101...
# case: stride = 1
#       10101010...
#       00000000...
#       10101010...
def imgDownSample(data, n=0.5):
    pass

# merge channels
# flag: specify which channel is used
def imgMergeChannel(data, flag=(True, True, True)):
    assert len(flag) == 3
    pass

# remove n LSBs
def imgRemoveLSB(data, n=1):
    assert isinstance(n, int) and (n >=0) and (n < 8)
    return data >> n


# bit blast the image vectors
# n: number of bits
def imgBitBlast(data, n=8):
    assert isinstance(n, int) and (n >=0) and (n <= 8)
    ret = []
    for i in range(n):
        ret.append((data >> n) & 1)
    return np.stack(ret,axis=-1)