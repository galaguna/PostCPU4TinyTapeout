//=============================
// MPM_cpu.v
//=============================
//
// Entidad para la Maquina de Post Mejorada (CPU MPM) 
// Version que opera con memrora RAM propia:
//  *Modulo sync_ram en myRAM.v 
// tanto para el espacio de código como el de datos.
//
//=============================================================================
// Codigo para la monografia:
// La Maquina de Post actualizada:
// Diseno, puesta en marcha y programacion del 
// prototipo de un pequeno CPU funcional
//=============================================================================
// Author: Gerardo Laguna
// UAM lerma
// Mexico
// 6/08/2025
//=============================================================================

module Post_cpu
   (
    input wire clk, reset,
    input wire run,
    output wire [3:0] state,
    output wire [7:0] code_add,
    input wire [3:0] code,
    output wire [7:0] data_add,
    input wire din,
    output wire dout,
    output wire  data_we
   );

   // symbolic state declaration
   localparam [3:0]
      stop = 			4'h0,
      start = 			4'h1, 
      fetch_decode = 	4'h2, 
      load_ha_jmp = 	4'h3, 
      load_la_jmp = 	4'h4, 
      jmp_exe = 		4'h5, 
      jz_exe = 		    4'h6,
      incdp_exe = 		4'h7, 
      decdp_exe = 		4'h8, 
      set_exe = 		4'h9,
      clr_exe = 		4'hA;

   // symbolic opcode declaration
   localparam [3:0]
      nop_code = 		4'h0,
      incdp_code = 	    4'h1, 
      decdp_code = 	    4'h2, 
      set_code = 		4'h3, 
      clr_code = 		4'h4, 
      jmp_code = 		4'h5, 
      jz_code = 		4'h6,
      stop_code = 		4'h7;

   // signal declaration
   reg [3:0] state_reg, state_next;
   reg [7:0] IP_reg, IP_next;
   reg [7:0] DP_reg, DP_next;
   reg [3:0] instruction_reg, instruction_next;
   reg [3:0] hadd_reg, hadd_next;
   reg [3:0] ladd_reg, ladd_next;
   reg bit_reg, bit_next;
   reg we_reg, we_next;
   

   // body
   // FSMD state & data registers
   always @(posedge clk, posedge reset)
      if (reset)
         begin
         	state_reg <= stop;
         	IP_reg <= 0;
         	DP_reg <= 0;
         	instruction_reg <= 0;
         	hadd_reg <= 0;
         	ladd_reg <= 0;
         	bit_reg <= 1'b0;
         	we_reg <= 1'b0;
         end
      else
         begin
         	state_reg <= state_next;
         	IP_reg <= IP_next;
         	DP_reg <= DP_next;
         	instruction_reg <= instruction_next;
         	hadd_reg <= hadd_next;
         	ladd_reg <= ladd_next;
         	bit_reg <= bit_next;
         	we_reg <= we_next;
         end

   // FSMD next-state logic
   always @*
   begin
      IP_next = IP_reg;
      DP_next = DP_reg;
      instruction_next = instruction_reg;
      hadd_next = hadd_reg;
      ladd_next = ladd_reg;

      case (state_reg)
         stop :
            if (run)
               state_next = start;
            else
               state_next = stop;
            
         start :
          begin	
            IP_next = 0;
            DP_next = 0;
            state_next = fetch_decode;
          end	

         fetch_decode :
          begin	
            instruction_next = code;
            IP_next = IP_reg + 1;
            
            case (code)
                nop_code :
                    state_next = fetch_decode;
                incdp_code:
                    state_next = incdp_exe;
                decdp_code :
                    state_next = decdp_exe;
                set_code :
                    state_next = set_exe;
                clr_code : 
                    state_next = clr_exe;                
                jmp_code :
                    state_next = load_ha_jmp;
                jz_code :
                    state_next = jz_exe;
                default :
                    state_next =stop;
            endcase
          end	

         load_ha_jmp : 
          begin	
            IP_next = IP_reg + 1;
            hadd_next = code;
            state_next = load_la_jmp;
          end	

         load_la_jmp :
          begin	
            ladd_next = code;
            state_next = jmp_exe;
          end	

         jmp_exe :
          begin	
            IP_next = {hadd_reg,  ladd_reg};
            state_next = fetch_decode;
          end	

         jz_exe :
            if (~din)
               state_next = load_ha_jmp;
            else
             begin
               IP_next = IP_reg + 2;
               state_next = fetch_decode;
             end
         incdp_exe :
          begin	
            DP_next = DP_reg + 1;
            state_next =fetch_decode;
          end	

         decdp_exe :
          begin	
            DP_next = DP_reg - 1;
            state_next =fetch_decode;
          end	

         set_exe :
            state_next =fetch_decode;
         
	     clr_exe :
            state_next =fetch_decode;

         default :
            state_next =stop;
      endcase

   end

   // look-ahead output logic
   always @*
   begin
      we_next = 1'b0;
      bit_next = 1'b0;

      case (state_next)
         set_exe :
          begin
            bit_next = 1'b1;
            we_next = 1'b1;
          end

         clr_exe :
            we_next = 1'b1;
      endcase
   end

   //outputs
   assign state = state_reg;
   assign code_add = IP_reg;
   assign data_add = DP_reg;
   assign dout = bit_reg;
   assign data_we = we_reg;

 endmodule
