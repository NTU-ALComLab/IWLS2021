from train_model_module import load_dataset
from train_model_module import model
import numpy as np
from tensorflow.keras.preprocessing.image import ImageDataGenerator

def view_weights(model):
  for layer in model.layers: 
   
    print(layer.name)
    for element in layer.get_weights():
      print(element)

def save_as_np(model,layerName):
  for layer in model.layers:
    if(layer.name==layerName):
      weight,bias=layer.get_weights()
      np.save(f"weight_array_dense2/{layerName}_weight.npy", weight)
      np.save(f"weight_array_dense2/{layerName}_bias.npy", bias)

def train_with_augmented_data(model,trainX, trainY):

  
  datagen = ImageDataGenerator(
    width_shift_range=0.1,
    height_shift_range=0.1,
    horizontal_flip=True,
    validation_split=0.1)
  
  datagen.fit(trainX)
  model.fit(datagen.flow(trainX, trainY, batch_size=180,
         subset='training'), 
          validation_data=datagen.flow(trainX, trainY,
         batch_size=15, subset='validation'), epochs=5)

  


if __name__ == '__main__':


	trainX, trainY = load_dataset()

	print("Training with no weight constraint")
	model1 = model(weightConstraintEnable=[False,False,False],biasConstraintEnable=False,quantizeEnable=False,roundInputs=False)
	model1.fit(trainX, trainY , batch_size=160, epochs=60, validation_split=0.1)
	train_with_augmented_data(model1,trainX, trainY)
	model1.fit(trainX, trainY , batch_size=180, epochs=10, validation_split=0.1)
	model1.save_weights("temp_weights/w0",save_format='tf')
	model1.save("temp_weights/w0",save_format='tf')



	print("Training with weight constraint on Conv11")
	model1 = model(weightConstraintEnable=[True,False,False],biasConstraintEnable=False,quantizeEnable=False,roundInputs=False)
	model1.load_weights("temp_weights/w0")
	model1.fit(trainX, trainY , batch_size=160, epochs=20, validation_split=0.1)
	model1.save_weights("temp_weights/w1",save_format='tf')
	model1.save("temp_weights/w1",save_format='tf')

	print("Training with weight constraint on Conv11,Conv21,Conv22")
	model1 = model(weightConstraintEnable=[True,True,False],biasConstraintEnable=False,quantizeEnable=False,roundInputs=False)
	model1.load_weights("temp_weights/w1")
	model1.fit(trainX, trainY , batch_size=160, epochs=20, validation_split=0.1)
	model1.save_weights("temp_weights/w2",save_format='tf')
	model1.save("temp_weights/w2",save_format='tf')

	print("Training with weight constraint on Conv11,Conv21,Conv22,Dense1")
	model1 = model(weightConstraintEnable=[True,True,True],biasConstraintEnable=False,quantizeEnable=False,roundInputs=False)
	model1.load_weights("temp_weights/w2")
	model1.fit(trainX, trainY , batch_size=160, epochs=10, validation_split=0.1)
	model1.save_weights("temp_weights/w3",save_format='tf')
	model1.save("temp_weights/w3",save_format='tf')

	print("Training with weight constraint on Conv11,Conv21,Conv22,Dense1,Dense")
	model1 = model(weightConstraintEnable=[True,True,True],biasConstraintEnable=False,quantizeEnable=True,roundInputs=False)
	model1.load_weights("temp_weights/w3")
	model1.fit(trainX, trainY , batch_size=160, epochs=10, validation_split=0.1)
	model1.save_weights("temp_weights/w4",save_format='tf')
	model1.save("temp_weights/w4",save_format='tf')

	print("Training with weight constraint on Conv11,Conv21,Conv22,Dense1,Dense,bias constraint")
	model1 = model(weightConstraintEnable=[True,True,True],biasConstraintEnable=True,quantizeEnable=True,roundInputs=False)
	model1.load_weights("temp_weights/w4")
	model1.fit(trainX, trainY , batch_size=160, epochs=5, validation_split=0.1)
	model1.save_weights("temp_weights/w5",save_format='tf')
	model1.save("temp_weights/w5",save_format='tf')

	print("Training with weight constraint on Conv11,Conv21,Conv22,Dense1,bias constraint,inputrounding")
	model1 = model(weightConstraintEnable=[True,True,True],biasConstraintEnable=True,quantizeEnable=True,roundInputs=True)
	model1.load_weights("temp_weights/w5")
	model1.fit(trainX, trainY , batch_size=160, epochs=5, validation_split=0.1)

	#print("View weights")
	view_weights(model1)
	save_as_np(model1,"conv11")
	save_as_np(model1,"conv21")
	save_as_np(model1,"conv22")
	save_as_np(model1,"dense")
	save_as_np(model1,"dense1")

