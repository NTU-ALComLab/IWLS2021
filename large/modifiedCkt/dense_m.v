module Dense(
input [5:0] x0 ,
input [5:0] x1 ,
input [5:0] x2 ,
input [5:0] x3 ,
input [5:0] x4 ,
input [5:0] x5 ,
input [5:0] x6 ,
input [5:0] x7 ,
input [5:0] x8 ,
input [5:0] x9 ,
input [5:0] x10 ,
input [5:0] x11 ,
input [5:0] x12 ,
input [5:0] x13 ,
input [5:0] x14 ,
input [5:0] x15 ,
input [5:0] x16 ,
input [5:0] x17 ,
input [5:0] x18 ,
input [5:0] x19 ,
output [9:0] y 
);
wire [13:0] sharing0;
wire [13:0] sharing1;
wire [13:0] sharing2;
wire [13:0] sharing3;
wire [13:0] sharing4;
wire [13:0] sharing5;
wire [13:0] sharing6;
wire [13:0] sharing7;
wire [13:0] sharing8;
wire [13:0] sharing9;
wire [13:0] sharing10;
wire [13:0] sharing11;
wire [13:0] sharing12;
assign sharing0 = $signed(-{2'b0,x13}<<<3'd1)+$signed({1'b0,x10})+$signed(-{2'b0,x1}<<<3'd1)+$signed(-{1'b0,x18})+$signed(-{2'b0,x18}<<<3'd1)+$signed({2'b0,x15}<<<3'd1);
assign sharing1 = $signed({3'b0,x16}<<<3'd2)+$signed(-{2'b0,x8}<<<3'd1)+$signed(-{1'b0,x7});
assign sharing2 = $signed(-{3'b0,x19}<<<3'd2)+$signed(-{2'b0,x19}<<<3'd1)+$signed({3'b0,x7}<<<3'd2)+$signed({3'b0,x14}<<<3'd2)+$signed(-{1'b0,x1})+$signed(-{1'b0,x15})+$signed({1'b0,x3})+$signed(-{2'b0,x4}<<<3'd1)+$signed(-{3'b0,x18}<<<3'd2);
assign sharing3 = $signed({2'b0,x6}<<<3'd1);
assign sharing4 = $signed(-{2'b0,x19}<<<3'd1)+$signed(-{1'b0,x19})+$signed(-{2'b0,x16}<<<3'd1)+$signed(-{1'b0,x16})+$signed(-{2'b0,x10}<<<3'd1)+$signed({1'b0,x4})+$signed(-{2'b0,x17}<<<3'd1);
assign sharing5 = $signed(-{2'b0,x1}<<<3'd1)+$signed(-{2'b0,x18}<<<3'd1)+$signed({2'b0,x7}<<<3'd1);
assign sharing6 = $signed(-{2'b0,x6}<<<3'd1)+$signed({1'b0,x1})+$signed(-{2'b0,x11}<<<3'd1)+$signed(-{1'b0,x11})+$signed(-{2'b0,x5}<<<3'd1)+$signed(-{1'b0,x5})+$signed(-{2'b0,x12}<<<3'd1);
assign sharing7 = $signed(-{1'b0,x4})+$signed({2'b0,x14}<<<3'd1)+$signed({1'b0,x16});
assign sharing8 = $signed(-{1'b0,x6})+$signed({1'b0,x0})+$signed(-{2'b0,x1}<<<3'd1)+$signed(-{1'b0,x1})+$signed(-{1'b0,x8})+$signed({3'b0,x15}<<<3'd2)+$signed({1'b0,x3})+$signed({3'b0,x17}<<<3'd2)+$signed(-{3'b0,x5}<<<3'd2)+$signed(-{3'b0,x18}<<<3'd2)+$signed(-{1'b0,x5});
assign sharing9 = $signed(-{2'b0,x19}<<<3'd1)+$signed({1'b0,x16})+$signed(-{2'b0,x7}<<<3'd1)+$signed(-{2'b0,x4}<<<3'd1)+$signed({1'b0,x2});
assign sharing10 = $signed({2'b0,x3}<<<3'd1)+$signed({2'b0,x0}<<<3'd1)+$signed({2'b0,x11}<<<3'd1)+$signed(-{2'b0,x10}<<<3'd1);
assign sharing11 = $signed({1'b0,x14})+$signed(-{2'b0,x10}<<<3'd1)+$signed(-{2'b0,x2}<<<3'd1);
assign sharing12 = $signed({2'b0,x13}<<<3'd1)+$signed({1'b0,x8})+$signed(-{1'b0,x2});
wire signed[16:0] temp_y  [0:9];
assign temp_y[0] = 
$signed(-{2'b0,x6}<<<3'd1)+$signed({2'b0,x13}<<<3'd1)+$signed(-{1'b0,x14})+$signed({2'b0,x15}<<<3'd1)+$signed({3'b0,x9}<<<3'd2)+$signed({2'b0,x9}<<<3'd1)+$signed(sharing8)+$signed(sharing9)+$signed(sharing10)-$signed(16'd40);
assign temp_y[1] = 
$signed({3'b0,x0}<<<3'd2)+$signed(-{1'b0,x6})+$signed({1'b0,x7})+$signed({2'b0,x14}<<<3'd1)+$signed({1'b0,x9})+$signed({1'b0,x16})+$signed(-{3'b0,x10}<<<3'd2)+$signed({1'b0,x17})+$signed(-{2'b0,x5}<<<3'd1)+$signed(-{3'b0,x12}<<<3'd2)+$signed({3'b0,x11}<<<3'd2)+$signed(sharing2)+$signed(-sharing3)+$signed(sharing12)-$signed(16'd40);
wire [16:0] max1;
assign max1 = $signed(temp_y[0]) > $signed(temp_y[1]) ? temp_y[0] : temp_y[1];
assign temp_y[2] = 
$signed(-{3'b0,x6}<<<3'd2)+$signed(-{1'b0,x12})+$signed({1'b0,x0})+$signed(-{1'b0,x8})+$signed({1'b0,x2})+$signed({1'b0,x15})+$signed({2'b0,x3}<<<3'd1)+$signed({1'b0,x3})+$signed({2'b0,x4}<<<3'd1)+$signed({1'b0,x11})+$signed({2'b0,x5}<<<3'd1)+$signed(sharing0)+$signed(sharing1)+$signed(-sharing11)-$signed(16'd16);
wire [16:0] max2;
assign max2 = $signed(temp_y[2]) > $signed(max1) ? temp_y[2] : max1;
assign temp_y[3] = 
$signed(-{2'b0,x6}<<<3'd1)+$signed(-{1'b0,x6})+$signed({2'b0,x0}<<<3'd1)+$signed(-{2'b0,x19}<<<3'd1)+$signed(-{1'b0,x9})+$signed(-{2'b0,x17}<<<3'd1)+$signed(-{3'b0,x5}<<<3'd2)+$signed({3'b0,x12}<<<3'd2)+$signed(sharing0)+$signed(-sharing1)-$signed(16'd0);
wire [16:0] max3;
assign max3 = $signed(temp_y[3]) > $signed(max2) ? temp_y[3] : max2;
assign temp_y[4] = 
$signed(-{2'b0,x0}<<<3'd1)+$signed(-{2'b0,x8}<<<3'd1)+$signed({3'b0,x2}<<<3'd2)+$signed({3'b0,x15}<<<3'd2)+$signed({1'b0,x2})+$signed(-{1'b0,x3})+$signed({2'b0,x4}<<<3'd1)+$signed(-{1'b0,x17})+$signed(sharing6)+$signed(-sharing7)+$signed(16'd48);
wire [16:0] max4;
assign max4 = $signed(temp_y[4]) > $signed(max3) ? temp_y[4] : max3;
assign temp_y[5] = 
$signed(-{3'b0,x6}<<<3'd2)+$signed(-{3'b0,x13}<<<3'd2)+$signed({2'b0,x0}<<<3'd1)+$signed(-{1'b0,x1})+$signed({2'b0,x2}<<<3'd1)+$signed({1'b0,x15})+$signed(-{1'b0,x9})+$signed({2'b0,x3}<<<3'd1)+$signed(-{1'b0,x17})+$signed({1'b0,x11})+$signed(-{1'b0,x5})+$signed({3'b0,x12}<<<3'd2)+$signed(sharing4)+$signed(sharing5)-$signed(16'd8);
wire [16:0] max5;
assign max5 = $signed(temp_y[5]) > $signed(max4) ? temp_y[5] : max4;
assign temp_y[6] = 
$signed(-{3'b0,x6}<<<3'd2)+$signed(-{1'b0,x12})+$signed({3'b0,x0}<<<3'd2)+$signed({1'b0,x19})+$signed(-{3'b0,x13}<<<3'd2)+$signed(-{1'b0,x13})+$signed(-{3'b0,x8}<<<3'd2)+$signed({1'b0,x9})+$signed(-{1'b0,x11})+$signed(sharing8)+$signed(-sharing9)+$signed(16'd64);
wire [16:0] max6;
assign max6 = $signed(temp_y[6]) > $signed(max5) ? temp_y[6] : max5;
assign temp_y[7] = 
$signed(-{1'b0,x6})+$signed(-{1'b0,x14})+$signed({1'b0,x3})+$signed(-{1'b0,x10})+$signed({3'b0,x4}<<<3'd2)+$signed({2'b0,x11}<<<3'd1)+$signed(-{2'b0,x5}<<<3'd1)+$signed({1'b0,x18})+$signed({2'b0,x12}<<<3'd1)+$signed(sharing4)+$signed(-sharing5)+$signed(-sharing12)-$signed(16'd0);
wire [16:0] max7;
assign max7 = $signed(temp_y[7]) > $signed(max6) ? temp_y[7] : max6;
assign temp_y[8] = 
$signed(-{3'b0,x19}<<<3'd2)+$signed(-{1'b0,x6})+$signed({3'b0,x13}<<<3'd2)+$signed({2'b0,x1}<<<3'd1)+$signed(-{1'b0,x8})+$signed({3'b0,x3}<<<3'd2)+$signed({2'b0,x3}<<<3'd1)+$signed(-{1'b0,x10})+$signed(-{3'b0,x18}<<<3'd2)+$signed(sharing6)+$signed(sharing7)+$signed(sharing11)+$signed(16'd8);
wire [16:0] max8;
assign max8 = $signed(temp_y[8]) > $signed(max7) ? temp_y[8] : max7;
assign temp_y[9] = 
$signed(-{1'b0,x19})+$signed({1'b0,x0})+$signed(-{2'b0,x8}<<<3'd1)+$signed(-{2'b0,x2}<<<3'd1)+$signed(-{2'b0,x16}<<<3'd1)+$signed(-{1'b0,x10})+$signed(-{3'b0,x17}<<<3'd2)+$signed(-{3'b0,x5}<<<3'd2)+$signed(-{2'b0,x12}<<<3'd1)+$signed(sharing2)+$signed(sharing3)+$signed(sharing10)-$signed(16'd32);
wire [16:0] max9;
assign max9 = $signed(temp_y[9]) > $signed(max8) ? temp_y[9] : max8;
assign y[0]= max9 == temp_y[0] ? 1'b1 : 1'b0;
assign y[1]= max9 == temp_y[1] ? 1'b1 : 1'b0;
assign y[2]= max9 == temp_y[2] ? 1'b1 : 1'b0;
assign y[3]= max9 == temp_y[3] ? 1'b1 : 1'b0;
assign y[4]= max9 == temp_y[4] ? 1'b1 : 1'b0;
assign y[5]= max9 == temp_y[5] ? 1'b1 : 1'b0;
assign y[6]= max9 == temp_y[6] ? 1'b1 : 1'b0;
assign y[7]= max9 == temp_y[7] ? 1'b1 : 1'b0;
assign y[8]= max9 == temp_y[8] ? 1'b1 : 1'b0;
assign y[9]= max9 == temp_y[9] ? 1'b1 : 1'b0;
endmodule