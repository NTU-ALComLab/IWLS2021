# Self-implemented fused convolution and linear layer.

They can be used for quantization aware training and using them may be more convinent when converting NN to circuits later.

Batch normalization can be disabled by setting `useBN=False`.

`ModelCIFAR10_3_c5f3` is an example of building a model using the two layers.

It should be okay to set `dilation` and `groups` for `conv2d`, but have to pay attention to the size of the weight.
The size of weight is only decided by `in_planes`, `out_planes` and `kernel_size`.
