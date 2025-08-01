//=============================================================================
// Entidad para generar un pulso
//=============================================================================
// Codigo para realizacion de pruebas manuales con botones
//=============================================================================
// Author: Gerardo A. Laguna S.
// Universidad Autonoma Metropolitana
// Unidad Lerma
// 4.julio.2025
//=============================================================================

module pulse_generator
   (
    input wire clk, reset, trigger,
    output reg  p
   );
   
   //Constants:
   
   // symbolic state declaration
   localparam [1:0]
      Idle = 2'b00,
      High  = 2'b01,
      wait_Low  = 2'b10;

   // signal declaration
   reg [1:0] state_reg, state_next;

   // body
   // FSMD state & data registers
   always @(posedge clk, posedge reset)
      if (reset)
            state_reg <= Idle;
      else
            state_reg <= state_next;

   // FSMD next-state logic
   always @*
   begin
      p = 1'b0;
      case (state_reg)
         Idle:
            begin
               if (trigger)
                  state_next = High;
               else
                  state_next = Idle;
            end
         High:
            begin
              state_next = wait_Low;       	
       	  p = 1'b1;
            end
         wait_Low:
            begin
               if (trigger)
                  state_next = wait_Low;
               else
                  state_next = Idle;
            end
         default:
            state_next = Idle;
      endcase
   end


endmodule
