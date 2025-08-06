/*
 * Copyright (c) 2025 Gerardo Laguna-Sanchez
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_galaguna_PostSys (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

    //signals:
    wire loc_clk;
    wire loc_NRst; 
    wire mode; 
    wire exec;
    wire [2:0] out_ctrl;
    wire spi_sck, spi_mosi, spi_cs, spi_miso;
    
    wire [3:0] state_nibble;
    wire [7:0] out8b;
    wire [2:0] out3b;
    
    //instantiations:
    Post_sys_4Tiny my_PostSys
    (
    .CLK(loc_clk), .NRST(loc_NRst),
    .RUN(exec), .MODE(mode), .OUT_CTRL(out_ctrl),
    .STATE(state_nibble),
    .OUT8B(out8b), .OUT3B(out3b),
    .SPI_CS(spi_cs), .SPI_MOSI(spi_mosi), .SPI_SCK(spi_sck),
    .SPI_MISO(spi_miso)
    );    
    
  // interconnection logic:
    assign loc_clk = clk; //1525.879 Hz
    assign loc_NRst = rst_n;

    assign out_ctrl = ui_in[2:0];
    assign spi_sck  = ui_in[3];
    assign spi_mosi = ui_in[4];
    assign spi_cs   = ui_in[5];
    assign exec     = ui_in[6];
    assign mode     = ui_in[7];

  //output logic:
    assign uio_oe  = 8'b11111111;
    assign uo_out = out8b;
    assign uio_out[3:0] = state_nibble;
    assign uio_out[6:4] = out3b;
    assign uio_out[7] = spi_miso;

  // List all unused inputs to prevent warnings
  wire _unused = &{ena, uio_in[0], uio_in[1], uio_in[2], uio_in[3], uio_in[4], uio_in[5], uio_in[6], uio_in[7], 1'b0};

endmodule
