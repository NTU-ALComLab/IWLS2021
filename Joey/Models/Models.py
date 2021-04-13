#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 22:44:26 2020

@author: joey
"""
import time
import torch
import torch.nn as nn
import torch.nn.functional as F
from collections import namedtuple
#from torch.quantization import QuantStub, DeQuantStub

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

QTensor = namedtuple('QTensor', ['tensor', 'scale', 'zero_point'])

def quantize_tensor(x, num_bits=8, min_val=None, max_val=None,imposePow=None,roundType='round'):
    if imposePow is not None:
        scale=2**(-1*imposePow)
        qmin = (2.**(num_bits-1))*(-1.)
        qmax = 2.**(num_bits-1) - 1.
    else:
        if not min_val and not max_val: 
            min_val, max_val = x.min(), x.max()
    
        qmin = (2.**(num_bits-1))*(-1.)
        qmax = 2.**(num_bits-1) - 1.
    
        if min_val!=max_val:
            scale=2**(torch.ceil(torch.log2((max_val-min_val)/(qmax-qmin))))
            #print("scale:",torch.ceil(torch.log2((max_val-min_val)/(qmax-qmin))))
        else:
            scale=2**(torch.ceil(torch.log2((torch.tensor([1e-4]))/(qmax-qmin))))
            scale=scale.to(device)
    zero_point=0
    q_x = zero_point + x / scale
    if roundType=='round':
        q_x.clamp_(qmin, qmax).round_()
    elif roundType=='floor':
        q_x.clamp_(qmin, qmax).floor_()
    #q_x = q_x.round().byte()
    
    return QTensor(tensor=q_x, scale=scale, zero_point=zero_point)

def dequantize_tensor(q_x):
    return q_x.scale * (q_x.tensor.float() - q_x.zero_point)

class FakeQuantOp(torch.autograd.Function):
    @staticmethod
    def forward(ctx, w, numBits=4,imposePow=None,roundType='round'):
        x = quantize_tensor(w,num_bits=numBits,imposePow=imposePow,roundType=roundType)
        x = dequantize_tensor(x)
        return x

    @staticmethod
    def backward(ctx, grad_output):
        # straight through estimator
        return grad_output, None, None, None


##### FUSE Layers #####
class ConvBN(nn.Module):
    def __init__(self, in_planes, out_planes, kernel_size=3, stride=1, padding=1, dilation=1, groups=1, nBits=8, useBN=True, useBias=True):
        self.kernel_size = kernel_size
        self.stride = stride
        self.padding = padding
        self.nBits=nBits
        self.useBN=useBN
        self.useBias=useBias
        self.dilation=dilation
        self.groups=groups
        super(ConvBN, self).__init__()
        self.convW=nn.parameter.Parameter(torch.empty(out_planes,in_planes,kernel_size,kernel_size))
        if useBias:
            self.convB=nn.parameter.Parameter(torch.empty(out_planes))
            nn.init.normal_(self.convB)
        nn.init.normal_(self.convW)
        if useBN:
            self.bnW=nn.parameter.Parameter(torch.empty(out_planes))
            self.bnB=nn.parameter.Parameter(torch.empty(out_planes))
            self.mean=torch.zeros(out_planes).to(device)
            self.var=torch.ones(out_planes).to(device)
            nn.init.normal_(self.bnW)
            nn.init.normal_(self.bnB)

    def forward(self,x):
        eps=1e-5
        momentum=0.1
        if self.training:
            xStat=F.conv2d(x,self.convW,self.convB if self.useBias else None,self.stride,self.padding,self.dilation,self.groups)
            with torch.no_grad():
                self.mean=self.mean*(1-momentum)+xStat.mean([0,2,3])*momentum
                self.var=self.var*(1-momentum)+xStat.var([0,2,3])*momentum

        if self.useBN:
            r=self.bnW.unsqueeze(1).unsqueeze(1).unsqueeze(1)
            var=self.var.unsqueeze(1).unsqueeze(1).unsqueeze(1)
            w=self.convW*r/(torch.sqrt(var)+eps)
            if self.useBias:
                b=(self.convB-self.mean)*self.bnW/(torch.sqrt(self.var)+eps)+self.bnB
            else:
                b=(-self.mean)*self.bnW/(torch.sqrt(self.var)+eps)+self.bnB

        else:
            w=self.convW
            if self.useBias:
                b=self.convB

        w=FakeQuantOp.apply(w,self.nBits)
        if self.useBN or self.useBias:
            b=FakeQuantOp.apply(b,self.nBits)
        x=F.conv2d(x,w,b if (self.useBN or self.useBias) else None,self.stride,self.padding,self.dilation,self.groups)
        # self.convW.data=convWBu
        # self.convB.data=convBBu
        return x


class LinearBN(nn.Module):
    def __init__(self,inFeats,outFeats,nBits=8,useBN=True,useBias=True):
        super(LinearBN,self).__init__()
        self.inFeats=inFeats
        self.outFeats=outFeats
        self.nBits=nBits
        self.useBN=useBN
        self.useBias=useBias
        self.linW=nn.parameter.Parameter(torch.empty(outFeats,inFeats))
        if useBias:
            self.linB=nn.parameter.Parameter(torch.empty(outFeats))
            nn.init.normal_(self.linB)
        if useBN:
            self.bnW=nn.parameter.Parameter(torch.empty(outFeats))
            self.bnB=nn.parameter.Parameter(torch.empty(outFeats))
            self.mean=torch.zeros(outFeats).to(device)
            self.var=torch.ones(outFeats).to(device)
            nn.init.normal_(self.linW)
            nn.init.normal_(self.bnW)
            nn.init.normal_(self.bnB)

    def forward(self,x):

        eps=1e-5
        momentum=0.1
        if self.training and self.useBN:
            xStat=F.linear(x,self.linW,self.linB if self.useBias else None)
            with torch.no_grad():
                #print("xStat size:",xStat.size())
                self.mean=self.mean*(1-momentum)+xStat.mean([0])*momentum
                self.var=self.var*(1-momentum)+xStat.var([0])*momentum
        if self.useBN:
            r=self.bnW.unsqueeze(1)
            var=self.var.unsqueeze(1)

            w=self.linW*r/(torch.sqrt(var)+eps)
            if self.useBias:
                b=(self.linB-self.mean)*self.bnW/(torch.sqrt(self.var)+eps)+self.bnB
            else:
                b=(-self.mean)*self.bnW/(torch.sqrt(self.var)+eps)+self.bnB
        else:
            w=self.linW
            if self.useBias:
                b=self.linB
        #print('fcw')
        w=FakeQuantOp.apply(w,self.nBits)
        #print('fcb')
        if self.useBN or self.useBias::
            b=FakeQuantOp.apply(b,self.nBits)
        x=F.linear(x,w,b if (self.useBN or self.useBias) else None)
        return x




class ModelCIFAR10_3_c5f3(nn.Module):
    def __init__(self,nBits=8,ch=20):
        super(ModelCIFAR10_3_c5f3,self).__init__()

        self.nBits= nBits
        self.ch= ch

        self.convs=nn.ModuleList()
        self.convs.append(ConvBN(3,ch,nBits=nBits))
        for i in range(4):
            # if i%2==1 or i==6:
            #     self.convs.append(ConvBN(ch*int(2**((i+1)//2)),ch*int(2**((i+1)//2)),nBits=nBits))
            # else:
            #     self.convs.append(ConvBN(ch*int(2**((i+1)//2)),ch*int(2**((i+1)//2))*2,nBits=nBits))
            if i<=2:
                self.convs.append(ConvBN(ch,ch,nBits=nBits))
            elif i==3:
                self.convs.append(ConvBN(ch,int(ch*1),nBits=nBits))
            else:
                self.convs.append(ConvBN(int(ch*1),int(ch*1),nBits=nBits))
        self.fcs=nn.ModuleList()
        self.fcs.append(LinearBN(int(ch*1)*16,int(ch/2),nBits=nBits))
        for i in range(1):
            self.fcs.append(LinearBN(int(ch/2),int(ch/2),nBits=nBits))
        self.fcs.append(nn.Linear(int(ch/2),10))


    def forward(self,x):
        for i in range(len(self.convs)):
            #print(f'conv{i+1}')
            if i%2==1 or i==len(self.convs)-1:
                x=F.relu6(F.max_pool2d(self.convs[i](x),2))
            else:
                x=F.relu6(self.convs[i](x))
            x=FakeQuantOp.apply(x,self.nBits,self.nBits-4,'floor')

        x=x.view(-1,int(self.ch*1)*16)
        x=F.dropout(x,p=0.05)
        for i in range(len(self.fcs)):
            #print(f'fc{i+1}')
            #if i==len()
            x=self.fcs[i](x)
            if i<len(self.fcs)-1:
                x=F.relu6(x)
            x=FakeQuantOp.apply(x,self.nBits,self.nBits-4,'floor')
            if i<=0:
                x=F.dropout(x,p=0.05)
        return x


class ModelCIFAR10_float_c5f3(nn.Module):
    def __init__(self,ch=20):
        super(ModelCIFAR10_float_c5f3,self).__init__()

        self.ch= ch

        self.convs=nn.ModuleList()
        self.convs.append(nn.Conv2d(3,ch,3,padding=1))
        for i in range(4):
            # if i%2==1 or i==6:
            #     self.convs.append(ConvBN(ch*int(2**((i+1)//2)),ch*int(2**((i+1)//2)),nBits=nBits))
            # else:
            #     self.convs.append(ConvBN(ch*int(2**((i+1)//2)),ch*int(2**((i+1)//2))*2,nBits=nBits))
            if i<=2:
                self.convs.append(nn.Conv2d(ch,ch,3,padding=1))
            elif i==3:
                self.convs.append(nn.Conv2d(ch,int(ch*1),3,padding=1))
            else:
                self.convs.append(nn.Conv2d(int(ch*1),int(ch*1),3,padding=1))
        self.fcs=nn.ModuleList()
        self.fcs.append(nn.Linear(int(ch*1)*16,int(ch/2)))
        for i in range(1):
            self.fcs.append(nn.Linear(int(ch/2),int(ch/2)))
        self.fcs.append(nn.Linear(int(ch/2),10))
        

    def forward(self,x):
        for i in range(len(self.convs)):
            if i%2==1 or i==len(self.convs)-1:
                x=F.relu6(F.max_pool2d(self.convs[i](x),2))
            else:
                x=F.relu6(self.convs[i](x))

        x=x.view(-1,int(self.ch*1)*16)
        x=F.dropout(x,p=0.1)
        # with torch.no_grad():
        #     self.outLWFloatData=self.fcs[-1].weight.data
        #     self.outLBFloatData=self.fcs[-1].bias.data
        #     self.fcs[-1].weight.data=FakeQuantOp.apply(self.fcs[-1].weight.data,self.nBits)
        #     self.fcs[-1].bias.data=FakeQuantOp.apply(self.fcs[-1].bias.data,self.nBits)
        for i in range(len(self.fcs)):
            x=self.fcs[i](x)
            if i<len(self.fcs)-1:
                x=F.relu6(x) 
            if i<=0:
                x=F.dropout(x,p=0.1)
                
        # with torch.no_grad():
        #     self.fcs[-1].weight.data=self.outLWFloatData
        #     self.fcs[-1].bias.data=self.outLBFloatData

        return x


##### MNIST #####
class ModelMnist(nn.Module):
    def __init__(self,nBits=4,numNeurons=25,bias=True):
        super(ModelMnist, self).__init__()
          
        self.fc1 = nn.Linear(28*28, numNeurons,bias=bias)
        self.fc2 = nn.Linear(numNeurons, numNeurons, bias=bias)
        self.fc3 = nn.Linear(numNeurons,10,bias=bias)
        self.dropout=nn.Dropout(p=0.25)
        self.nBits=nBits
        self.bias=bias
      
    def forward(self, x):
        floatWeights=[]
        for p in self.parameters():
            floatWeights.append(p.data)
        
        x=x.view(-1,28*28)
        x=self.dropout(x)
        self.fc1.weight.data=FakeQuantOp.apply(self.fc1.weight.data,self.nBits)
        if self.bias:
            self.fc1.bias.data=FakeQuantOp.apply(self.fc1.bias.data,self.nBits)
        x=self.fc1(x)
        x=F.relu6(x)
        x=FakeQuantOp.apply(x,self.nBits,0,'floor')
        
        
        self.fc2.weight.data=FakeQuantOp.apply(self.fc2.weight.data,self.nBits)
        if self.bias:
            self.fc2.bias.data=FakeQuantOp.apply(self.fc2.bias.data,self.nBits)
        x=self.fc2(x)
        x=F.relu6(x)
        x=FakeQuantOp.apply(x,self.nBits,0,'floor')
        
        
        self.fc3.weight.data=FakeQuantOp.apply(self.fc3.weight.data,self.nBits)
        if self.bias:
            self.fc3.bias.data=FakeQuantOp.apply(self.fc3.bias.data,self.nBits)
        x=self.fc3(x)
        x=FakeQuantOp.apply(x,self.nBits,0,'floor')
        
        return x,floatWeights