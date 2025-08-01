//=============================================================================
// myRAM.v
//=============================================================================
// Simple generic RAM Model
//=============================================================================
// Author: Gerardo A. Laguna S.
// Universidad Autonoma Metropolitana
// Unidad Lerma
// 10.julio.2025
//=============================================================================
// A partir de codigo 12.1 del libro 
// Chu, Pong P. (2008). FPGA Prototyping by Verilog Examples. EUA: Wiley.
//!!!Gracias Prof. P. Chu :) !!! 
//==========================================================

module sync_ram
   #(parameter DATA_WIDTH=8, ADD_WIDTH=8)
   (
    input wire clk,we, 
    input wire [DATA_WIDTH-1:0] datain,
    input wire [ADD_WIDTH-1:0] address,
    output wire [DATA_WIDTH-1:0] dataout
   );
   
   // signal declaration
  reg [DATA_WIDTH-1:0] ram[(2**ADD_WIDTH)-1:0];

   // body
   always @(posedge clk)
      if (we)
        ram[address]<= datain;
        
   
   // output logic
  assign dataout = ram[address];

endmodule
