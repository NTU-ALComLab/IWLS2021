# import tensorflow as tf
# import numpy as np
# from tensorflow.keras.models import Model
# from tensorflow.keras.layers import Input,Dense,Flatten,Dropout,MaxPooling2D, Conv2D
# from tensorflow.keras.layers.merge import concatenate
# from tensorflow.keras.datasets import cifar10
# from tensorflow.keras.utils.np_utils import to_categorical
# from tensorflow.keras.models import load_model
# from tensorflow.keras.layers import ReLU
# from tensorflow.keras import constraints
# from tensorflow.keras.initializers import RandomUniform

from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, Flatten, Dropout, MaxPooling2D, Conv2D, concatenate
from tensorflow.keras.datasets import cifar10
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import load_model
from tensorflow.keras.layers import ReLU
from tensorflow.keras import constraints
from tensorflow.keras.initializers import RandomUniform
import tensorflow as tf
import numpy as np


def load_dataset():
    # load dataset
	(trainX, trainY), _ = cifar10.load_data()
    
	trainX >>= 1
	trainX = np.concatenate((trainX[:, ::2, ::2, :], trainX[:, 1::2, 1::2, :]), axis=0)
	trainY = np.concatenate(2 * (trainY, ), axis=0)
	trainY = to_categorical(trainY)
    
   
	return trainX, trainY

#For modeling fixpoint inputs
class rounding(tf.keras.layers.Layer):

	def __init__(self):
		super(rounding, self).__init__()

	def call(self, inputs):
		return tf.round(inputs*2)/2


#Fixpoint constraint for output dense layer
class fix_4bits(tf.keras.constraints.Constraint):

	def __init__(self):
		pass


	def __call__(self, w):
      

		return tf.round(w*16)/16


#Constrain weights to power of 2
class fixpoint(tf.keras.constraints.Constraint):


	def __init__(self):
		pass

	def __call__(self, w):
    
		w = tf.where(w>0.8,1.0,tf.where(w>0.45,0.5,tf.where(w>0.2,0.25,tf.where(w > 0.09375 , 0.125, tf.where(w > 0.03125, 0.0625 
        ,tf.where(w<-0.8,-1.0,tf.where(w<-0.45,-0.5,tf.where(w<-0.2,-0.25,tf.where(w < -0.09375, -0.125 , tf.where(w < -0.03125, -0.0625 , 0) )) ) )   )))))
   
		return w 


#Constraint for bias
class fixpoint_b(tf.keras.constraints.Constraint):
 

	def __init__(self):
		pass

	def __call__(self, b):
		b = tf.round(b*4)/4
		return b 





def model(weightConstraintEnable,biasConstraintEnable,quantizeEnable,roundInputs):

	fixpoint1 = fixpoint()
	fixpoint_b1 = fixpoint_b()
	fix_4bits1=fix_4bits()

	f_w = lambda x : fixpoint1 if x else None
	result_w = list(map(f_w,weightConstraintEnable))

	f_b = lambda x : fixpoint_b1 if x else None
	result_b = f_b(biasConstraintEnable)

	f_q = lambda x : fix_4bits1 if x else None
	result_q = f_q(quantizeEnable)

	input = Input(shape=(16,16,3))

	initializer = RandomUniform(minval=-0.1 , maxval=0.1)

  
	conv11 = Conv2D(10,(2, 2),strides=2, padding='valid',data_format="channels_last",activation=ReLU(max_value=16,threshold=0)
	,use_bias=True,kernel_constraint=result_w[0],name='conv11',bias_constraint=result_b,kernel_initializer=initializer)(input)

	if roundInputs:
		r1 = rounding()(conv11)
		drop1 = Dropout(0.1)(r1)

	else:
		drop1 = Dropout(0.1)(conv11)

 

	conv21 = Conv2D(18, (2, 2),strides=2,activation=ReLU(max_value=16,threshold=0),use_bias=True
          ,kernel_constraint=result_w[1],name='conv21',bias_constraint=result_b,kernel_initializer=initializer)(drop1[:,:,:,0:8])

	conv22 = Conv2D(13, (2, 2),strides=2,activation=ReLU(max_value=16,threshold=0),use_bias=True
          ,kernel_constraint=result_w[1],name='conv22',bias_constraint=result_b,kernel_initializer=initializer)(drop1[:,:,:,4:10])
  
 

	drop21 = Dropout(0.1)(conv21)
	drop22 = Dropout(0.1)(conv22)
  
	flat1 = Flatten()(drop21)
	flat2 = Flatten()(drop22)



	merge_last= concatenate([flat1,flat2])
  
	if roundInputs:
		r2 = rounding()(merge_last)
		dense1 = Dense(16,activation=ReLU(max_value=32,threshold=0),use_bias=True,name='dense1',bias_constraint=result_b,kernel_constraint=result_w[2])(r2)
	else:
		dense1 = Dense(16,activation=ReLU(max_value=32,threshold=0),use_bias=True,name='dense1',bias_constraint=result_b,kernel_constraint=result_w[2])(merge_last)

	if roundInputs:
		r3 = rounding()(dense1)
		output = Dense(10,activation='softmax',use_bias=True,name='dense',bias_constraint=result_b,kernel_constraint=result_q)(r3)
	else:
		output = Dense(10,activation='softmax',use_bias=True,name='dense',bias_constraint=result_b,kernel_constraint=result_q)(dense1)


	model = Model(inputs=input,outputs=output)

	model.compile(optimizer = "adam", loss='categorical_crossentropy',metrics=['accuracy'])


	return model  







