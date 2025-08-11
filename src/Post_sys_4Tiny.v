
//////////////////////////////////////////////////////////////////////////////////
//=============================================================================
// Entidad Post_sys_4Tiny con CPU Post, memoria y comunicacion SPI.
//  En esta version:
//  * La entrada de reset (NRST) es activa en bajo.
//  * Se agregan puertos de salida OUT8B y OUT3B para monitorizacion de buses internos.
//  * Se agrega puerto de entrada OUT_CTRL para seleccionar lo que se presenta en
//    las salidas anteriores.
//  * El reloj del CPU se asume con una frecuencia f_CLK=1.5625MHz. 
//  * La velocidad para la comunicacion SPI resulta en f_SCK=195.3125 kHz con f_CLK=1.5625MHz.
//=============================================================================
// Codigo beta
//=============================================================================
// Author: Gerardo A. Laguna S.
// Universidad Autonoma Metropolitana
// Unidad Lerma
// 11.agosto.2025
//=============================================================================
//////////////////////////////////////////////////////////////////////////////////


module Post_sys_4Tiny
(
    input CLK,NRST,RUN,MODE,
    input [2:0] OUT_CTRL,
    output [3:0] STATE,
    output [7:0] OUT8B,
    output [2:0] OUT3B,
    input SPI_CS,        
    input SPI_MOSI,     
    output SPI_MISO,    
    input SPI_SCK     
    );
 
    //signals:
    wire run_sig;
    wire loc_rst;
    
    wire prog_clk;
    wire mem_clk;
    wire mxd_mem_clk;
    
    wire spi2ram_dout;
    wire cpu2ram_dout;

    wire spi2ram_din;
    wire cpu2ram_din;
    wire mxd_ram_din;

    wire [7:0] spi2ram_add;
    wire [7:0] cpu2ram_add;
    wire [7:0] mxd_ram_add;
    
    wire spi2ram_we;
    wire cpu2ram_we;
    wire mxd_ram_we;
    
    wire [3:0] spi2rom_dout;
    wire [3:0] cpu2rom_dout;

    wire [3:0] spi2rom_din;
    wire [3:0] mxd_rom_din;

    wire [7:0] spi2rom_add;
    wire [7:0] cpu2rom_add;
    wire [7:0] mxd_rom_add;

    wire spi2rom_we;
    wire mxd_rom_we;
  
    //instantiations:
    sync_ram #(.DATA_WIDTH(1), .ADD_WIDTH(8)) my_ram
    (.clk(mxd_mem_clk), .we(mxd_ram_we), .datain(mxd_ram_din), .address(mxd_ram_add), .dataout(cpu2ram_dout));

    sync_ram #(.DATA_WIDTH(4), .ADD_WIDTH(8)) my_rom
    (.clk(mxd_mem_clk), .we(mxd_rom_we), .datain(mxd_rom_din), .address(mxd_rom_add), .dataout(cpu2rom_dout));


    slave_spi4post my_PostSPI
    (
    .CLK(CLK), .RST(loc_rst),
    .CS(SPI_CS), .MOSI(SPI_MOSI), .SCK(SPI_SCK),
    .MISO(SPI_MISO),
    .cin_prg(spi2rom_dout),
    .cout_prg(spi2rom_din),
    .cadd_prg(spi2rom_add),
    .cwe_prg(spi2rom_we),
    .din_prg(spi2ram_dout),
    .dout_prg(spi2ram_din),
    .dadd_prg(spi2ram_add),
    .dwe_prg(spi2ram_we), .prog_clk(prog_clk)
    );    

   Post_cpu my_cpu
   (
    .clk(CLK), .reset(loc_rst),
    .run(run_sig),
    .state(STATE),
    .code_add(cpu2rom_add),
    .code(cpu2rom_dout),
    .data_add(cpu2ram_add),
    .din(cpu2ram_dout),
    .dout(cpu2ram_din),
    .data_we(cpu2ram_we)
   );
      
    pulse_generator my_pulse
        (.clk(CLK), .reset(loc_rst), .trigger(RUN), .p(run_sig));

  // interconnection logic:
    assign mem_clk = ~CLK;
    assign loc_rst = ~NRST;
    assign spi2ram_dout = cpu2ram_dout;
    assign spi2rom_dout = cpu2rom_dout;
  
  // multiplexors logic:
    assign mxd_ram_din = (MODE) ? cpu2ram_din : spi2ram_din;
    assign mxd_ram_add = (MODE) ? cpu2ram_add : spi2ram_add;
    assign mxd_ram_we = (MODE) ? cpu2ram_we :  spi2ram_we;
    assign mxd_rom_din =  (MODE) ? 4'b0000 : spi2rom_din;
    assign mxd_rom_add = (MODE) ? cpu2rom_add : spi2rom_add;
    assign mxd_rom_we = (MODE) ? 1'b0 :  spi2rom_we;
    assign mxd_mem_clk = (MODE) ? mem_clk :  prog_clk;
  
   //8 to 1 multiplexor for OUT8B:
     assign OUT8B = (OUT_CTRL[2] ? (OUT_CTRL[1] ? (OUT_CTRL[0] ? cpu2ram_add : cpu2ram_add) : (OUT_CTRL[0] ? cpu2rom_add : cpu2rom_add)) 
                              :
                             (OUT_CTRL[1] ? (OUT_CTRL[0] ? spi2ram_add : spi2ram_add) : (OUT_CTRL[0] ? spi2rom_add : spi2rom_add)));

   //8 to 1 multiplexor for OUT3B:
     assign OUT3B = (OUT_CTRL[2] ? (OUT_CTRL[1] ? (OUT_CTRL[0] ? {2'b00, cpu2ram_dout} : {2'b00, cpu2ram_din}) : (OUT_CTRL[0] ? cpu2rom_dout[2:0] : cpu2rom_dout[2:0])) 
                                :
                               (OUT_CTRL[1] ? (OUT_CTRL[0] ? {2'b00, spi2ram_dout} : {2'b00, spi2ram_din}) : (OUT_CTRL[0] ? spi2rom_dout[2:0] : spi2rom_din[2:0])));
  
endmodule
