from revised_circuit_module import genconv
from revised_circuit_module import gendense
from revised_circuit_module import generate_ports_dense
from revised_circuit_module import connect_input
from revised_circuit_module import connect
from revised_circuit_module import concatenate
from revised_circuit_module import connect_output
from revised_circuit_module import gen_inner_dense
from revised_circuit_module import bind
import numpy as np

def gen_top(outputFile):

  fout = open(outputFile,"w")
  generate_ports_dense("top",fout,32*32*3,8,10)
  fout.write(f"wire [6:0]conv11in[0:16*16*3-1];\n")
  connect_input(fout,"Bind","b","x","conv11in", 32*32*3 , 16*16*3)
  fout.write(f"wire [4:0]conv11out[0:8*8*10-1];\n")
  fout.write(f"wire [4:0]conv21out[0:4*4*18-1];\n")
  fout.write(f"wire [4:0]conv22out[0:4*4*13-1];\n")
  fout.write(f"wire [5:0]dense1out[0:20-1];\n")

  connect(fout,"Conv11","conv11","conv11in","conv11out", 16*16*3 , 8*8*10 , 0)
  connect(fout,"Conv21","conv21","conv11out","conv21out", 8*8*8 , 4*4*18 , 0)
  connect(fout,"Conv22","conv22","conv11out","conv22out", 8*8*6 , 4*4*13 , 8*8*4)
  concatenate(fout,"Dense1","dense1","conv21out","conv22out", 4*4*18 , 4*4*13 ,False,20,"dense1out")
  connect_output(fout,"Dense","dense","dense1out",20)

  fout.write(f"endmodule")





if __name__== '__main__':
  
  weight=np.load("weight_array_dense2/conv11_weight.npy")
  bias=np.load("weight_array_dense2/conv11_bias.npy")
  genconv(7,5,weight,bias,"cktFolder/conv11.v","Conv11", [16,16,3], [8,8,10]
      , channelFirst=True, kernelSize=2, strides=2,shift_amount=0,max=4,output_resolution=1,out_channelFirst=True)

  weight=np.load("weight_array_dense2/conv21_weight.npy")
  bias=np.load("weight_array_dense2/conv21_bias.npy")
  genconv(5,5,weight,bias,"cktFolder/conv21.v","Conv21", [8,8,8], [4,4,18]
      , channelFirst=True, kernelSize=2, strides=2,shift_amount=1,max=4,output_resolution=1,out_channelFirst=False)

  weight=np.load("weight_array_dense2/conv22_weight.npy")
  bias=np.load("weight_array_dense2/conv22_bias.npy")
  genconv(5,5,weight,bias,"cktFolder/conv22.v","Conv22", [8,8,6], [4,4,13]
      , channelFirst=True, kernelSize=2, strides=2,shift_amount=1,max=4,output_resolution=1,out_channelFirst=False)

  weight=np.load("weight_array_dense2/dense1_weight.npy")
  bias=np.load("weight_array_dense2/dense1_bias.npy")
  gen_inner_dense(5,"cktFolder/dense1.v", "Dense1",  496 , 20 , weight , bias , 1 , 1 ,6,5)


  weight=np.load("weight_array_dense2/dense_weight.npy")
  bias=np.load("weight_array_dense2/dense_bias.npy")
  gendense(6,"cktFolder/dense.v", "Dense", 20 , 10 , weight , bias )

  gen_top("cktFolder/top.v")
  
  bind("cktFolder/bind.v","Bind",3072,768,[32,32,3],[16,16,3])







