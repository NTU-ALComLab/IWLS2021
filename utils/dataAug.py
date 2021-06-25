import numpy as np
from numpy.core.fromnumeric import transpose
import albumentations as A
from joblib import Parallel, delayed

albumTrans = A.Compose([
    #A.RandomRotate90(),
    A.Flip(),
    #A.Transpose(),
    #A.OneOf([
    #    A.IAAAdditiveGaussianNoise(),
    #    A.GaussNoise(),
    #], p=0.2),
    #A.OneOf([
    #    A.MotionBlur(p=.2),
    #    A.MedianBlur(blur_limit=3, p=0.1),
    #    A.Blur(blur_limit=3, p=0.1),
    #], p=0.2),
    A.ShiftScaleRotate(shift_limit=0.05, scale_limit=0.1, rotate_limit=5, p=0.2),
    #A.OneOf([
    #    A.OpticalDistortion(p=0.3),
    #    A.GridDistortion(p=.1),
    #    A.IAAPiecewiseAffine(p=0.3),
    #], p=0.2),
    #A.OneOf([
    #    A.CLAHE(clip_limit=2),
    #    A.IAASharpen(),
    #    A.IAAEmboss(),
    #    A.RandomBrightnessContrast(),            
    #], p=0.3),
    #A.HueSaturationValue(p=0.3),
])

def imgTransform(img):
    return albumTrans(image=img.transpose((1, 2, 0)))['image'].transpose((2, 0, 1))

def dataAug(data, labels, nRnd=1, nJob=1):
    newData = [
        Parallel(n_jobs=nJob, backend='threading')(
            delayed(imgTransform)(dat)
            for dat in data
        )
        for _ in range(nRnd)
    ]
    data = np.concatenate([data, *newData])
    return data, labels*(nRnd+1)
