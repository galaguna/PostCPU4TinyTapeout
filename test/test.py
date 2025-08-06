# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst_n.value = 1

    dut._log.info("Test project behavior")

    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #Masks definitions:
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #   +--------+-------------+--------------------+
    #   |out_ctrl|    OUT8B    |       OUT3B        |
    #   +--------+-------------+--------------------+
    #   |   0    | spi2rom_add | spi2rom_din[2:0]   |
    #   +--------+-------------+--------------------+
    #   |   1    | spi2rom_add | spi2rom_dout[2:0]  |
    #   +--------+-------------+--------------------+
    #   |   2    | spi2ram_add |{2'b00,spi2rom_din} |
    #   +--------+-------------+--------------------+
    #   |   3    | spi2ram_add |{2'b00,spi2rom_dout}|
    #   +--------+-------------+--------------------+
    #   |   4    | cpu2rom_add | cpu2rom_dout[2:0]  |
    #   +--------+-------------+--------------------+
    #   |   5    | cpu2rom_add | cpu2rom_dout[2:0]  |
    #   +--------+-------------+--------------------+
    #   |   6    | cpu2ram_add |{2'b00,cpu2rom_din} |
    #   +--------+-------------+--------------------+
    #   |   7    | cpu2ram_add |{2'b00,cpu2rom_dout}|
    #   +--------+-------------+--------------------+
    MSK_OUT_CTRL_TO_0 = 0xF8
    MSK_OUT_CTRL_TO_4 = 0x04
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    MSK_SPI_SCK_TO_ON = 0x08
    MSK_SPI_SCK_TO_OFF = 0xF7
    MSK_SPI_MOSI_TO_ON = 0x10
    MSK_SPI_MOSI_TO_OFF = 0xEF
    MSK_SPI_CS_TO_ON = 0x20
    MSK_SPI_CS_TO_OFF = 0xDF
    MSK_RUN_TO_ON = 0x40
    MSK_RUN_TO_OFF = 0xBF
    MSK_MODE_TO_ON = 0x80
    MSK_MODE_TO_OFF = 0x7F
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    MSK_out3b = 0x70
    MSK_state = 0x0F

    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Programing mode (MODE=0) with OUT_CTRL=0 (OUT8B = spi2rom_add, OUT3B=spi2rom_din[2:0])
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #Master SPI initial values:  
    dut.ui_in.value  = MSK_SPI_SCK_TO_ON | MSK_SPI_CS_TO_ON | MSK_SPI_MOSI_TO_ON
    await ClockCycles(dut.clk, 16)

    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Sequence of ROM write SPI commands to store Post intructions
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #
    #    |-------------------------------|
    #    |         2 Bytes SPI word      |
    #    |-------------------------------|
    #    | RW  |  Address  |     Data    |                                                        
    #    | bit |   bits    |     bits    |                                                    
    #    |-----|-----------|-------------|
    #    | b15 | [b14:b04] |  [b03:b00]  |
    #    |-----|-----------|-------------|
    #    |  x  |xxxxxxxxxxx|    xxxx     |
    #    |-----|-----------|-------------|
    #
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #     SPI 11 bits address map:
    #
    #     -----+-----------+--
    #     0x000|           |   Code                                                               
    #          |    ROM    |   space                                                              
    #     0x3FF|           |                                                             
    #     -----|-----------|--
    #     0x400|           |   Data 
    #          |    RAM    |   space                                                              
    #     0x7FF|           |                                                                 
    #     -----|-----------|--
    #    
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # STOP intruction (0x7) in loc 0x00
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
       #SCK period #1:
    dut.ui_in.value = dut.ui_in.value &   MSK_SPI_CS_TO_OFF  &   MSK_SPI_MOSI_TO_OFF
    await ClockCycles(dut.clk, 1)
    ###SCK falling edge:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_SCK_TO_OFF
    await ClockCycles(dut.clk, 4)
    ###SCK rising edge:
    dut.ui_in.value = dut.ui_in.value |  MSK_SPI_SCK_TO_ON
    await ClockCycles(dut.clk, 4)
    
    #SCK period #2:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_MOSI_TO_OFF
    await ClockCycles(dut.clk, 1)
    ###SCK falling edge:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_SCK_TO_OFF
    await ClockCycles(dut.clk, 4)
    ###SCK rising edge:
    dut.ui_in.value = dut.ui_in.value |  MSK_SPI_SCK_TO_ON
    await ClockCycles(dut.clk, 4)

    #SCK period #3:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_MOSI_TO_OFF
    await ClockCycles(dut.clk, 1)
    ###SCK falling edge:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_SCK_TO_OFF
    await ClockCycles(dut.clk, 4)
    ###SCK rising edge:
    dut.ui_in.value = dut.ui_in.value |  MSK_SPI_SCK_TO_ON
    await ClockCycles(dut.clk, 4)

    #SCK period #4:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_MOSI_TO_OFF
    await ClockCycles(dut.clk, 1)
    ###SCK falling edge:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_SCK_TO_OFF
    await ClockCycles(dut.clk, 4)
    ###SCK rising edge:
    dut.ui_in.value = dut.ui_in.value |  MSK_SPI_SCK_TO_ON
    await ClockCycles(dut.clk, 4)

    #SCK period #5:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_MOSI_TO_OFF
    await ClockCycles(dut.clk, 1)
    ###SCK falling edge:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_SCK_TO_OFF
    await ClockCycles(dut.clk, 4)
    ###SCK rising edge:
    dut.ui_in.value = dut.ui_in.value |  MSK_SPI_SCK_TO_ON
    await ClockCycles(dut.clk, 4)

    #SCK period #6:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_MOSI_TO_OFF
    await ClockCycles(dut.clk, 1)
    ###SCK falling edge:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_SCK_TO_OFF
    await ClockCycles(dut.clk, 4)
    ###SCK rising edge:
    dut.ui_in.value = dut.ui_in.value |  MSK_SPI_SCK_TO_ON
    await ClockCycles(dut.clk, 4)

    #SCK period #7:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_MOSI_TO_OFF
    await ClockCycles(dut.clk, 1)
    ###SCK falling edge:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_SCK_TO_OFF
    await ClockCycles(dut.clk, 4)
    ###SCK rising edge:
    dut.ui_in.value = dut.ui_in.value |  MSK_SPI_SCK_TO_ON
    await ClockCycles(dut.clk, 4)

    #SCK period #8:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_MOSI_TO_OFF
    await ClockCycles(dut.clk, 1)
    ###SCK falling edge:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_SCK_TO_OFF
    await ClockCycles(dut.clk, 4)
    ###SCK rising edge:
    dut.ui_in.value = dut.ui_in.value |  MSK_SPI_SCK_TO_ON
    await ClockCycles(dut.clk, 4)

    #SCK period #9:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_MOSI_TO_OFF
    await ClockCycles(dut.clk, 1)
    ###SCK falling edge:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_SCK_TO_OFF
    await ClockCycles(dut.clk, 4)
    ###SCK rising edge:
    dut.ui_in.value = dut.ui_in.value |  MSK_SPI_SCK_TO_ON
    await ClockCycles(dut.clk, 4)

    #SCK period #10:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_MOSI_TO_OFF
    await ClockCycles(dut.clk, 1)
    ###SCK falling edge:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_SCK_TO_OFF
    await ClockCycles(dut.clk, 4)
    ###SCK rising edge:
    dut.ui_in.value = dut.ui_in.value |  MSK_SPI_SCK_TO_ON
    await ClockCycles(dut.clk, 4)

    #SCK period #11:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_MOSI_TO_OFF
    await ClockCycles(dut.clk, 1)
    ###SCK falling edge:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_SCK_TO_OFF
    await ClockCycles(dut.clk, 4)
    ###SCK rising edge:
    dut.ui_in.value = dut.ui_in.value |  MSK_SPI_SCK_TO_ON
    await ClockCycles(dut.clk, 4)

    #SCK period #12:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_MOSI_TO_OFF
    await ClockCycles(dut.clk, 1)
    ###SCK falling edge:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_SCK_TO_OFF
    await ClockCycles(dut.clk, 4)
    ###SCK rising edge:
    dut.ui_in.value = dut.ui_in.value |  MSK_SPI_SCK_TO_ON
    await ClockCycles(dut.clk, 4)

    #SCK period #13:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_MOSI_TO_OFF
    await ClockCycles(dut.clk, 1)
    ###SCK falling edge:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_SCK_TO_OFF
    await ClockCycles(dut.clk, 4)
    ###SCK rising edge:
    dut.ui_in.value = dut.ui_in.value |  MSK_SPI_SCK_TO_ON
    await ClockCycles(dut.clk, 4)

    #SCK period #14:
    dut.ui_in.value = dut.ui_in.value |  MSK_SPI_MOSI_TO_ON
    await ClockCycles(dut.clk, 1)
    ###SCK falling edge:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_SCK_TO_OFF
    await ClockCycles(dut.clk, 4)
    ###SCK rising edge:
    dut.ui_in.value = dut.ui_in.value |  MSK_SPI_SCK_TO_ON
    await ClockCycles(dut.clk, 4)

    #SCK period #15:
    dut.ui_in.value = dut.ui_in.value |  MSK_SPI_MOSI_TO_ON
    await ClockCycles(dut.clk, 1)
    ###SCK falling edge:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_SCK_TO_OFF
    await ClockCycles(dut.clk, 4)
    ###SCK rising edge:
    dut.ui_in.value = dut.ui_in.value |  MSK_SPI_SCK_TO_ON
    await ClockCycles(dut.clk, 4)

    #SCK period #16:
    dut.ui_in.value = dut.ui_in.value |  MSK_SPI_MOSI_TO_ON
    await ClockCycles(dut.clk, 1)
    ###SCK falling edge:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_SCK_TO_OFF
    await ClockCycles(dut.clk, 4)
    ###SCK rising edge:
    dut.ui_in.value = dut.ui_in.value |  MSK_SPI_SCK_TO_ON
    await ClockCycles(dut.clk, 4)

    ###Last SCK falling edge:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_SCK_TO_OFF
    await ClockCycles(dut.clk, 4)
    #Master SPI final values:
    dut.ui_in.value = MSK_SPI_CS_TO_ON  | MSK_SPI_MOSI_TO_ON | MSK_SPI_SCK_TO_ON
    await ClockCycles(dut.clk, 4)

    await ClockCycles(dut.clk, 16)

    expected_c_add = 0x00
    assert dut.uo_out.value == expected_c_add
    expected_op_code = 0x7 #STOP code
    assert (dut.uio_out.value & MSK_out3b)>>4 == expected_op_code

    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # NOP intruction (0x0) in loc 0x01
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
       #SCK period #1:
    dut.ui_in.value = dut.ui_in.value &   MSK_SPI_CS_TO_OFF  &   MSK_SPI_MOSI_TO_OFF
    await ClockCycles(dut.clk, 1)
    ###SCK falling edge:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_SCK_TO_OFF
    await ClockCycles(dut.clk, 4)
    ###SCK rising edge:
    dut.ui_in.value = dut.ui_in.value |  MSK_SPI_SCK_TO_ON
    await ClockCycles(dut.clk, 4)
    
    #SCK period #2:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_MOSI_TO_OFF
    await ClockCycles(dut.clk, 1)
    ###SCK falling edge:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_SCK_TO_OFF
    await ClockCycles(dut.clk, 4)
    ###SCK rising edge:
    dut.ui_in.value = dut.ui_in.value |  MSK_SPI_SCK_TO_ON
    await ClockCycles(dut.clk, 4)

    #SCK period #3:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_MOSI_TO_OFF
    await ClockCycles(dut.clk, 1)
    ###SCK falling edge:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_SCK_TO_OFF
    await ClockCycles(dut.clk, 4)
    ###SCK rising edge:
    dut.ui_in.value = dut.ui_in.value |  MSK_SPI_SCK_TO_ON
    await ClockCycles(dut.clk, 4)

    #SCK period #4:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_MOSI_TO_OFF
    await ClockCycles(dut.clk, 1)
    ###SCK falling edge:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_SCK_TO_OFF
    await ClockCycles(dut.clk, 4)
    ###SCK rising edge:
    dut.ui_in.value = dut.ui_in.value |  MSK_SPI_SCK_TO_ON
    await ClockCycles(dut.clk, 4)

    #SCK period #5:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_MOSI_TO_OFF
    await ClockCycles(dut.clk, 1)
    ###SCK falling edge:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_SCK_TO_OFF
    await ClockCycles(dut.clk, 4)
    ###SCK rising edge:
    dut.ui_in.value = dut.ui_in.value |  MSK_SPI_SCK_TO_ON
    await ClockCycles(dut.clk, 4)

    #SCK period #6:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_MOSI_TO_OFF
    await ClockCycles(dut.clk, 1)
    ###SCK falling edge:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_SCK_TO_OFF
    await ClockCycles(dut.clk, 4)
    ###SCK rising edge:
    dut.ui_in.value = dut.ui_in.value |  MSK_SPI_SCK_TO_ON
    await ClockCycles(dut.clk, 4)

    #SCK period #7:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_MOSI_TO_OFF
    await ClockCycles(dut.clk, 1)
    ###SCK falling edge:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_SCK_TO_OFF
    await ClockCycles(dut.clk, 4)
    ###SCK rising edge:
    dut.ui_in.value = dut.ui_in.value |  MSK_SPI_SCK_TO_ON
    await ClockCycles(dut.clk, 4)

    #SCK period #8:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_MOSI_TO_OFF
    await ClockCycles(dut.clk, 1)
    ###SCK falling edge:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_SCK_TO_OFF
    await ClockCycles(dut.clk, 4)
    ###SCK rising edge:
    dut.ui_in.value = dut.ui_in.value |  MSK_SPI_SCK_TO_ON
    await ClockCycles(dut.clk, 4)

    #SCK period #9:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_MOSI_TO_OFF
    await ClockCycles(dut.clk, 1)
    ###SCK falling edge:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_SCK_TO_OFF
    await ClockCycles(dut.clk, 4)
    ###SCK rising edge:
    dut.ui_in.value = dut.ui_in.value |  MSK_SPI_SCK_TO_ON
    await ClockCycles(dut.clk, 4)

    #SCK period #10:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_MOSI_TO_OFF
    await ClockCycles(dut.clk, 1)
    ###SCK falling edge:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_SCK_TO_OFF
    await ClockCycles(dut.clk, 4)
    ###SCK rising edge:
    dut.ui_in.value = dut.ui_in.value |  MSK_SPI_SCK_TO_ON
    await ClockCycles(dut.clk, 4)

    #SCK period #11:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_MOSI_TO_OFF
    await ClockCycles(dut.clk, 1)
    ###SCK falling edge:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_SCK_TO_OFF
    await ClockCycles(dut.clk, 4)
    ###SCK rising edge:
    dut.ui_in.value = dut.ui_in.value |  MSK_SPI_SCK_TO_ON
    await ClockCycles(dut.clk, 4)

    #SCK period #12:
    dut.ui_in.value = dut.ui_in.value |  MSK_SPI_MOSI_TO_ON
    await ClockCycles(dut.clk, 1)
    ###SCK falling edge:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_SCK_TO_OFF
    await ClockCycles(dut.clk, 4)
    ###SCK rising edge:
    dut.ui_in.value = dut.ui_in.value |  MSK_SPI_SCK_TO_ON
    await ClockCycles(dut.clk, 4)

    #SCK period #13:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_MOSI_TO_OFF
    await ClockCycles(dut.clk, 1)
    ###SCK falling edge:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_SCK_TO_OFF
    await ClockCycles(dut.clk, 4)
    ###SCK rising edge:
    dut.ui_in.value = dut.ui_in.value |  MSK_SPI_SCK_TO_ON
    await ClockCycles(dut.clk, 4)

    #SCK period #14:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_MOSI_TO_OFF
    await ClockCycles(dut.clk, 1)
    ###SCK falling edge:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_SCK_TO_OFF
    await ClockCycles(dut.clk, 4)
    ###SCK rising edge:
    dut.ui_in.value = dut.ui_in.value |  MSK_SPI_SCK_TO_ON
    await ClockCycles(dut.clk, 4)

    #SCK period #15:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_MOSI_TO_OFF
    await ClockCycles(dut.clk, 1)
    ###SCK falling edge:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_SCK_TO_OFF
    await ClockCycles(dut.clk, 4)
    ###SCK rising edge:
    dut.ui_in.value = dut.ui_in.value |  MSK_SPI_SCK_TO_ON
    await ClockCycles(dut.clk, 4)

    #SCK period #16:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_MOSI_TO_OFF
    await ClockCycles(dut.clk, 1)
    ###SCK falling edge:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_SCK_TO_OFF
    await ClockCycles(dut.clk, 4)
    ###SCK rising edge:
    dut.ui_in.value = dut.ui_in.value |  MSK_SPI_SCK_TO_ON
    await ClockCycles(dut.clk, 4)

    ###Last SCK falling edge:
    dut.ui_in.value = dut.ui_in.value &  MSK_SPI_SCK_TO_OFF
    await ClockCycles(dut.clk, 4)
    #Master SPI final values:
    dut.ui_in.value = MSK_SPI_CS_TO_ON  | MSK_SPI_MOSI_TO_ON | MSK_SPI_SCK_TO_ON
    await ClockCycles(dut.clk, 4)

    await ClockCycles(dut.clk, 16)

    expected_c_add = 0x01
    assert dut.uo_out.value == expected_c_add
    expected_op_code = 0x0 #NOP code
    assert (dut.uio_out.value & MSK_out3b)>>4 == expected_op_code

    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Execution mode (MODE=1) with OUT_CTRL=4 (OUT8B = IP, OUT3B=OP_CODE)
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    dut.ui_in.value = MSK_MODE_TO_ON | MSK_OUT_CTRL_TO_4
    await ClockCycles(dut.clk, 16)

    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Run the coded program (Just the STOP instruction)
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    dut.ui_in.value = dut.ui_in.value | MSK_RUN_TO_ON
    while((dut.uio_out.value & MSK_state) == 0):
        await ClockCycles(dut.clk, 1)


    expected_state = 0x1 #Start state
    assert (dut.uio_out.value & MSK_state) == expected_state
    expected_c_add = 0x00 #First IP
    assert dut.uo_out.value == expected_c_add
    expected_op_code = 0x7 #Programmed STOP code
    assert (dut.uio_out.value & MSK_out3b)>>4 == expected_op_code

    dut.ui_in.value = dut.ui_in.value &  MSK_RUN_TO_OFF
    while((dut.uio_out.value & MSK_state) != 0):
        await ClockCycles(dut.clk, 1)

    expected_c_add = 0x01   #Next IP
    assert dut.uo_out.value == expected_c_add
