extern "C" {
#include <math.h>
/******************************************************************************
 *                      Code generated with sympy 1.5.1                       *
 *                                                                            *
 *              See http://www.sympy.org/ for more information.               *
 *                                                                            *
 *                         This file is part of 'ekf'                         *
 ******************************************************************************/
void err_fun(double *nom_x, double *delta_x, double *out_2572225847926737909) {
   out_2572225847926737909[0] = delta_x[0] + nom_x[0];
   out_2572225847926737909[1] = delta_x[1] + nom_x[1];
   out_2572225847926737909[2] = delta_x[2] + nom_x[2];
   out_2572225847926737909[3] = delta_x[3] + nom_x[3];
   out_2572225847926737909[4] = delta_x[4] + nom_x[4];
   out_2572225847926737909[5] = delta_x[5] + nom_x[5];
   out_2572225847926737909[6] = delta_x[6] + nom_x[6];
   out_2572225847926737909[7] = delta_x[7] + nom_x[7];
   out_2572225847926737909[8] = delta_x[8] + nom_x[8];
   out_2572225847926737909[9] = delta_x[9] + nom_x[9];
   out_2572225847926737909[10] = delta_x[10] + nom_x[10];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_539577615850755275) {
   out_539577615850755275[0] = -nom_x[0] + true_x[0];
   out_539577615850755275[1] = -nom_x[1] + true_x[1];
   out_539577615850755275[2] = -nom_x[2] + true_x[2];
   out_539577615850755275[3] = -nom_x[3] + true_x[3];
   out_539577615850755275[4] = -nom_x[4] + true_x[4];
   out_539577615850755275[5] = -nom_x[5] + true_x[5];
   out_539577615850755275[6] = -nom_x[6] + true_x[6];
   out_539577615850755275[7] = -nom_x[7] + true_x[7];
   out_539577615850755275[8] = -nom_x[8] + true_x[8];
   out_539577615850755275[9] = -nom_x[9] + true_x[9];
   out_539577615850755275[10] = -nom_x[10] + true_x[10];
}
void H_mod_fun(double *state, double *out_1352348085656852477) {
   out_1352348085656852477[0] = 1.0;
   out_1352348085656852477[1] = 0.0;
   out_1352348085656852477[2] = 0.0;
   out_1352348085656852477[3] = 0.0;
   out_1352348085656852477[4] = 0.0;
   out_1352348085656852477[5] = 0.0;
   out_1352348085656852477[6] = 0.0;
   out_1352348085656852477[7] = 0.0;
   out_1352348085656852477[8] = 0.0;
   out_1352348085656852477[9] = 0.0;
   out_1352348085656852477[10] = 0.0;
   out_1352348085656852477[11] = 0.0;
   out_1352348085656852477[12] = 1.0;
   out_1352348085656852477[13] = 0.0;
   out_1352348085656852477[14] = 0.0;
   out_1352348085656852477[15] = 0.0;
   out_1352348085656852477[16] = 0.0;
   out_1352348085656852477[17] = 0.0;
   out_1352348085656852477[18] = 0.0;
   out_1352348085656852477[19] = 0.0;
   out_1352348085656852477[20] = 0.0;
   out_1352348085656852477[21] = 0.0;
   out_1352348085656852477[22] = 0.0;
   out_1352348085656852477[23] = 0.0;
   out_1352348085656852477[24] = 1.0;
   out_1352348085656852477[25] = 0.0;
   out_1352348085656852477[26] = 0.0;
   out_1352348085656852477[27] = 0.0;
   out_1352348085656852477[28] = 0.0;
   out_1352348085656852477[29] = 0.0;
   out_1352348085656852477[30] = 0.0;
   out_1352348085656852477[31] = 0.0;
   out_1352348085656852477[32] = 0.0;
   out_1352348085656852477[33] = 0.0;
   out_1352348085656852477[34] = 0.0;
   out_1352348085656852477[35] = 0.0;
   out_1352348085656852477[36] = 1.0;
   out_1352348085656852477[37] = 0.0;
   out_1352348085656852477[38] = 0.0;
   out_1352348085656852477[39] = 0.0;
   out_1352348085656852477[40] = 0.0;
   out_1352348085656852477[41] = 0.0;
   out_1352348085656852477[42] = 0.0;
   out_1352348085656852477[43] = 0.0;
   out_1352348085656852477[44] = 0.0;
   out_1352348085656852477[45] = 0.0;
   out_1352348085656852477[46] = 0.0;
   out_1352348085656852477[47] = 0.0;
   out_1352348085656852477[48] = 1.0;
   out_1352348085656852477[49] = 0.0;
   out_1352348085656852477[50] = 0.0;
   out_1352348085656852477[51] = 0.0;
   out_1352348085656852477[52] = 0.0;
   out_1352348085656852477[53] = 0.0;
   out_1352348085656852477[54] = 0.0;
   out_1352348085656852477[55] = 0.0;
   out_1352348085656852477[56] = 0.0;
   out_1352348085656852477[57] = 0.0;
   out_1352348085656852477[58] = 0.0;
   out_1352348085656852477[59] = 0.0;
   out_1352348085656852477[60] = 1.0;
   out_1352348085656852477[61] = 0.0;
   out_1352348085656852477[62] = 0.0;
   out_1352348085656852477[63] = 0.0;
   out_1352348085656852477[64] = 0.0;
   out_1352348085656852477[65] = 0.0;
   out_1352348085656852477[66] = 0.0;
   out_1352348085656852477[67] = 0.0;
   out_1352348085656852477[68] = 0.0;
   out_1352348085656852477[69] = 0.0;
   out_1352348085656852477[70] = 0.0;
   out_1352348085656852477[71] = 0.0;
   out_1352348085656852477[72] = 1.0;
   out_1352348085656852477[73] = 0.0;
   out_1352348085656852477[74] = 0.0;
   out_1352348085656852477[75] = 0.0;
   out_1352348085656852477[76] = 0.0;
   out_1352348085656852477[77] = 0.0;
   out_1352348085656852477[78] = 0.0;
   out_1352348085656852477[79] = 0.0;
   out_1352348085656852477[80] = 0.0;
   out_1352348085656852477[81] = 0.0;
   out_1352348085656852477[82] = 0.0;
   out_1352348085656852477[83] = 0.0;
   out_1352348085656852477[84] = 1.0;
   out_1352348085656852477[85] = 0.0;
   out_1352348085656852477[86] = 0.0;
   out_1352348085656852477[87] = 0.0;
   out_1352348085656852477[88] = 0.0;
   out_1352348085656852477[89] = 0.0;
   out_1352348085656852477[90] = 0.0;
   out_1352348085656852477[91] = 0.0;
   out_1352348085656852477[92] = 0.0;
   out_1352348085656852477[93] = 0.0;
   out_1352348085656852477[94] = 0.0;
   out_1352348085656852477[95] = 0.0;
   out_1352348085656852477[96] = 1.0;
   out_1352348085656852477[97] = 0.0;
   out_1352348085656852477[98] = 0.0;
   out_1352348085656852477[99] = 0.0;
   out_1352348085656852477[100] = 0.0;
   out_1352348085656852477[101] = 0.0;
   out_1352348085656852477[102] = 0.0;
   out_1352348085656852477[103] = 0.0;
   out_1352348085656852477[104] = 0.0;
   out_1352348085656852477[105] = 0.0;
   out_1352348085656852477[106] = 0.0;
   out_1352348085656852477[107] = 0.0;
   out_1352348085656852477[108] = 1.0;
   out_1352348085656852477[109] = 0.0;
   out_1352348085656852477[110] = 0.0;
   out_1352348085656852477[111] = 0.0;
   out_1352348085656852477[112] = 0.0;
   out_1352348085656852477[113] = 0.0;
   out_1352348085656852477[114] = 0.0;
   out_1352348085656852477[115] = 0.0;
   out_1352348085656852477[116] = 0.0;
   out_1352348085656852477[117] = 0.0;
   out_1352348085656852477[118] = 0.0;
   out_1352348085656852477[119] = 0.0;
   out_1352348085656852477[120] = 1.0;
}
void f_fun(double *state, double dt, double *out_8900138899586851029) {
   out_8900138899586851029[0] = dt*state[3] + state[0];
   out_8900138899586851029[1] = dt*state[4] + state[1];
   out_8900138899586851029[2] = dt*state[5] + state[2];
   out_8900138899586851029[3] = state[3];
   out_8900138899586851029[4] = state[4];
   out_8900138899586851029[5] = state[5];
   out_8900138899586851029[6] = dt*state[7] + state[6];
   out_8900138899586851029[7] = dt*state[8] + state[7];
   out_8900138899586851029[8] = state[8];
   out_8900138899586851029[9] = state[9];
   out_8900138899586851029[10] = state[10];
}
void F_fun(double *state, double dt, double *out_3235793707817571148) {
   out_3235793707817571148[0] = 1;
   out_3235793707817571148[1] = 0;
   out_3235793707817571148[2] = 0;
   out_3235793707817571148[3] = dt;
   out_3235793707817571148[4] = 0;
   out_3235793707817571148[5] = 0;
   out_3235793707817571148[6] = 0;
   out_3235793707817571148[7] = 0;
   out_3235793707817571148[8] = 0;
   out_3235793707817571148[9] = 0;
   out_3235793707817571148[10] = 0;
   out_3235793707817571148[11] = 0;
   out_3235793707817571148[12] = 1;
   out_3235793707817571148[13] = 0;
   out_3235793707817571148[14] = 0;
   out_3235793707817571148[15] = dt;
   out_3235793707817571148[16] = 0;
   out_3235793707817571148[17] = 0;
   out_3235793707817571148[18] = 0;
   out_3235793707817571148[19] = 0;
   out_3235793707817571148[20] = 0;
   out_3235793707817571148[21] = 0;
   out_3235793707817571148[22] = 0;
   out_3235793707817571148[23] = 0;
   out_3235793707817571148[24] = 1;
   out_3235793707817571148[25] = 0;
   out_3235793707817571148[26] = 0;
   out_3235793707817571148[27] = dt;
   out_3235793707817571148[28] = 0;
   out_3235793707817571148[29] = 0;
   out_3235793707817571148[30] = 0;
   out_3235793707817571148[31] = 0;
   out_3235793707817571148[32] = 0;
   out_3235793707817571148[33] = 0;
   out_3235793707817571148[34] = 0;
   out_3235793707817571148[35] = 0;
   out_3235793707817571148[36] = 1;
   out_3235793707817571148[37] = 0;
   out_3235793707817571148[38] = 0;
   out_3235793707817571148[39] = 0;
   out_3235793707817571148[40] = 0;
   out_3235793707817571148[41] = 0;
   out_3235793707817571148[42] = 0;
   out_3235793707817571148[43] = 0;
   out_3235793707817571148[44] = 0;
   out_3235793707817571148[45] = 0;
   out_3235793707817571148[46] = 0;
   out_3235793707817571148[47] = 0;
   out_3235793707817571148[48] = 1;
   out_3235793707817571148[49] = 0;
   out_3235793707817571148[50] = 0;
   out_3235793707817571148[51] = 0;
   out_3235793707817571148[52] = 0;
   out_3235793707817571148[53] = 0;
   out_3235793707817571148[54] = 0;
   out_3235793707817571148[55] = 0;
   out_3235793707817571148[56] = 0;
   out_3235793707817571148[57] = 0;
   out_3235793707817571148[58] = 0;
   out_3235793707817571148[59] = 0;
   out_3235793707817571148[60] = 1;
   out_3235793707817571148[61] = 0;
   out_3235793707817571148[62] = 0;
   out_3235793707817571148[63] = 0;
   out_3235793707817571148[64] = 0;
   out_3235793707817571148[65] = 0;
   out_3235793707817571148[66] = 0;
   out_3235793707817571148[67] = 0;
   out_3235793707817571148[68] = 0;
   out_3235793707817571148[69] = 0;
   out_3235793707817571148[70] = 0;
   out_3235793707817571148[71] = 0;
   out_3235793707817571148[72] = 1;
   out_3235793707817571148[73] = dt;
   out_3235793707817571148[74] = 0;
   out_3235793707817571148[75] = 0;
   out_3235793707817571148[76] = 0;
   out_3235793707817571148[77] = 0;
   out_3235793707817571148[78] = 0;
   out_3235793707817571148[79] = 0;
   out_3235793707817571148[80] = 0;
   out_3235793707817571148[81] = 0;
   out_3235793707817571148[82] = 0;
   out_3235793707817571148[83] = 0;
   out_3235793707817571148[84] = 1;
   out_3235793707817571148[85] = dt;
   out_3235793707817571148[86] = 0;
   out_3235793707817571148[87] = 0;
   out_3235793707817571148[88] = 0;
   out_3235793707817571148[89] = 0;
   out_3235793707817571148[90] = 0;
   out_3235793707817571148[91] = 0;
   out_3235793707817571148[92] = 0;
   out_3235793707817571148[93] = 0;
   out_3235793707817571148[94] = 0;
   out_3235793707817571148[95] = 0;
   out_3235793707817571148[96] = 1;
   out_3235793707817571148[97] = 0;
   out_3235793707817571148[98] = 0;
   out_3235793707817571148[99] = 0;
   out_3235793707817571148[100] = 0;
   out_3235793707817571148[101] = 0;
   out_3235793707817571148[102] = 0;
   out_3235793707817571148[103] = 0;
   out_3235793707817571148[104] = 0;
   out_3235793707817571148[105] = 0;
   out_3235793707817571148[106] = 0;
   out_3235793707817571148[107] = 0;
   out_3235793707817571148[108] = 1;
   out_3235793707817571148[109] = 0;
   out_3235793707817571148[110] = 0;
   out_3235793707817571148[111] = 0;
   out_3235793707817571148[112] = 0;
   out_3235793707817571148[113] = 0;
   out_3235793707817571148[114] = 0;
   out_3235793707817571148[115] = 0;
   out_3235793707817571148[116] = 0;
   out_3235793707817571148[117] = 0;
   out_3235793707817571148[118] = 0;
   out_3235793707817571148[119] = 0;
   out_3235793707817571148[120] = 1;
}
void h_6(double *state, double *sat_pos, double *out_6606989255780333083) {
   out_6606989255780333083[0] = sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2)) + state[6];
}
void H_6(double *state, double *sat_pos, double *out_4785527618276088513) {
   out_4785527618276088513[0] = (-sat_pos[0] + state[0])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_4785527618276088513[1] = (-sat_pos[1] + state[1])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_4785527618276088513[2] = (-sat_pos[2] + state[2])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_4785527618276088513[3] = 0;
   out_4785527618276088513[4] = 0;
   out_4785527618276088513[5] = 0;
   out_4785527618276088513[6] = 1;
   out_4785527618276088513[7] = 0;
   out_4785527618276088513[8] = 0;
   out_4785527618276088513[9] = 0;
   out_4785527618276088513[10] = 0;
}
void h_20(double *state, double *sat_pos, double *out_764831846531854296) {
   out_764831846531854296[0] = sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2)) + sat_pos[3]*state[10] + state[6] + state[9];
}
void H_20(double *state, double *sat_pos, double *out_3111045652100265697) {
   out_3111045652100265697[0] = (-sat_pos[0] + state[0])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_3111045652100265697[1] = (-sat_pos[1] + state[1])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_3111045652100265697[2] = (-sat_pos[2] + state[2])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_3111045652100265697[3] = 0;
   out_3111045652100265697[4] = 0;
   out_3111045652100265697[5] = 0;
   out_3111045652100265697[6] = 1;
   out_3111045652100265697[7] = 0;
   out_3111045652100265697[8] = 0;
   out_3111045652100265697[9] = 1;
   out_3111045652100265697[10] = sat_pos[3];
}
void h_7(double *state, double *sat_pos_vel, double *out_1935398902179795105) {
   out_1935398902179795105[0] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + state[7];
}
void H_7(double *state, double *sat_pos_vel, double *out_6324310137951649025) {
   out_6324310137951649025[0] = pow(sat_pos_vel[0] - state[0], 2)*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_6324310137951649025[1] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[1] - state[1], 2)*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_6324310137951649025[2] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[2] - state[2], 2)*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_6324310137951649025[3] = -(sat_pos_vel[0] - state[0])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_6324310137951649025[4] = -(sat_pos_vel[1] - state[1])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_6324310137951649025[5] = -(sat_pos_vel[2] - state[2])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_6324310137951649025[6] = 0;
   out_6324310137951649025[7] = 1;
   out_6324310137951649025[8] = 0;
   out_6324310137951649025[9] = 0;
   out_6324310137951649025[10] = 0;
}
void h_21(double *state, double *sat_pos_vel, double *out_1935398902179795105) {
   out_1935398902179795105[0] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + state[7];
}
void H_21(double *state, double *sat_pos_vel, double *out_6324310137951649025) {
   out_6324310137951649025[0] = pow(sat_pos_vel[0] - state[0], 2)*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_6324310137951649025[1] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[1] - state[1], 2)*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_6324310137951649025[2] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[2] - state[2], 2)*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_6324310137951649025[3] = -(sat_pos_vel[0] - state[0])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_6324310137951649025[4] = -(sat_pos_vel[1] - state[1])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_6324310137951649025[5] = -(sat_pos_vel[2] - state[2])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_6324310137951649025[6] = 0;
   out_6324310137951649025[7] = 1;
   out_6324310137951649025[8] = 0;
   out_6324310137951649025[9] = 0;
   out_6324310137951649025[10] = 0;
}
}

extern "C"{
#define DIM 11
#define EDIM 11
#define MEDIM 11
typedef void (*Hfun)(double *, double *, double *);

void predict(double *x, double *P, double *Q, double dt);
const static double MAHA_THRESH_6 = 3.841459;
void update_6(double *, double *, double *, double *, double *);
const static double MAHA_THRESH_20 = 3.841459;
void update_20(double *, double *, double *, double *, double *);
const static double MAHA_THRESH_7 = 3.841459;
void update_7(double *, double *, double *, double *, double *);
const static double MAHA_THRESH_21 = 3.841459;
void update_21(double *, double *, double *, double *, double *);
}

#include <eigen3/Eigen/Dense>
#include <iostream>

typedef Eigen::Matrix<double, DIM, DIM, Eigen::RowMajor> DDM;
typedef Eigen::Matrix<double, EDIM, EDIM, Eigen::RowMajor> EEM;
typedef Eigen::Matrix<double, DIM, EDIM, Eigen::RowMajor> DEM;

void predict(double *in_x, double *in_P, double *in_Q, double dt) {
  typedef Eigen::Matrix<double, MEDIM, MEDIM, Eigen::RowMajor> RRM;
  
  double nx[DIM] = {0};
  double in_F[EDIM*EDIM] = {0};

  // functions from sympy
  f_fun(in_x, dt, nx);
  F_fun(in_x, dt, in_F);


  EEM F(in_F);
  EEM P(in_P);
  EEM Q(in_Q);

  RRM F_main = F.topLeftCorner(MEDIM, MEDIM);
  P.topLeftCorner(MEDIM, MEDIM) = (F_main * P.topLeftCorner(MEDIM, MEDIM)) * F_main.transpose();
  P.topRightCorner(MEDIM, EDIM - MEDIM) = F_main * P.topRightCorner(MEDIM, EDIM - MEDIM);
  P.bottomLeftCorner(EDIM - MEDIM, MEDIM) = P.bottomLeftCorner(EDIM - MEDIM, MEDIM) * F_main.transpose();

  P = P + dt*Q;

  // copy out state
  memcpy(in_x, nx, DIM * sizeof(double));
  memcpy(in_P, P.data(), EDIM * EDIM * sizeof(double));
}

// note: extra_args dim only correct when null space projecting
// otherwise 1
template <int ZDIM, int EADIM, bool MAHA_TEST>
void update(double *in_x, double *in_P, Hfun h_fun, Hfun H_fun, Hfun Hea_fun, double *in_z, double *in_R, double *in_ea, double MAHA_THRESHOLD) {
  typedef Eigen::Matrix<double, ZDIM, ZDIM, Eigen::RowMajor> ZZM;
  typedef Eigen::Matrix<double, ZDIM, DIM, Eigen::RowMajor> ZDM;
  typedef Eigen::Matrix<double, Eigen::Dynamic, EDIM, Eigen::RowMajor> XEM;
  //typedef Eigen::Matrix<double, EDIM, ZDIM, Eigen::RowMajor> EZM;
  typedef Eigen::Matrix<double, Eigen::Dynamic, 1> X1M;
  typedef Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> XXM;

  double in_hx[ZDIM] = {0};
  double in_H[ZDIM * DIM] = {0};
  double in_H_mod[EDIM * DIM] = {0};
  double delta_x[EDIM] = {0};
  double x_new[DIM] = {0};


  // state x, P
  Eigen::Matrix<double, ZDIM, 1> z(in_z);
  EEM P(in_P);
  ZZM pre_R(in_R);
  
  // functions from sympy
  h_fun(in_x, in_ea, in_hx);
  H_fun(in_x, in_ea, in_H);
  ZDM pre_H(in_H); 
  
  // get y (y = z - hx)
  Eigen::Matrix<double, ZDIM, 1> pre_y(in_hx); pre_y = z - pre_y;
  X1M y; XXM H; XXM R;
  if (Hea_fun){
    typedef Eigen::Matrix<double, ZDIM, EADIM, Eigen::RowMajor> ZAM;
    double in_Hea[ZDIM * EADIM] = {0};
    Hea_fun(in_x, in_ea, in_Hea);
    ZAM Hea(in_Hea);
    XXM A = Hea.transpose().fullPivLu().kernel();
   

    y = A.transpose() * pre_y;
    H = A.transpose() * pre_H;
    R = A.transpose() * pre_R * A;
  } else {
    y = pre_y;
    H = pre_H;
    R = pre_R;
  }
  // get modified H
  H_mod_fun(in_x, in_H_mod);
  DEM H_mod(in_H_mod);
  XEM H_err = H * H_mod;
  
  // Do mahalobis distance test
  if (MAHA_TEST){
    XXM a = (H_err * P * H_err.transpose() + R).inverse();
    double maha_dist = y.transpose() * a * y;
    if (maha_dist > MAHA_THRESHOLD){
      R = 1.0e16 * R;
    }
  }

  // Outlier resilient weighting
  double weight = 1;//(1.5)/(1 + y.squaredNorm()/R.sum());

  // kalman gains and I_KH
  XXM S = ((H_err * P) * H_err.transpose()) + R/weight;
  XEM KT = S.fullPivLu().solve(H_err * P.transpose());
  //EZM K = KT.transpose(); TODO: WHY DOES THIS NOT COMPILE?
  //EZM K = S.fullPivLu().solve(H_err * P.transpose()).transpose();
  //std::cout << "Here is the matrix rot:\n" << K << std::endl;
  EEM I_KH = Eigen::Matrix<double, EDIM, EDIM>::Identity() - (KT.transpose() * H_err);

  // update state by injecting dx
  Eigen::Matrix<double, EDIM, 1> dx(delta_x);
  dx  = (KT.transpose() * y);
  memcpy(delta_x, dx.data(), EDIM * sizeof(double));
  err_fun(in_x, delta_x, x_new);
  Eigen::Matrix<double, DIM, 1> x(x_new);
 
  // update cov 
  P = ((I_KH * P) * I_KH.transpose()) + ((KT.transpose() * R) * KT);

  // copy out state
  memcpy(in_x, x.data(), DIM * sizeof(double));
  memcpy(in_P, P.data(), EDIM * EDIM * sizeof(double));
  memcpy(in_z, y.data(), y.rows() * sizeof(double));
}



extern "C"{

      void update_6(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
        update<1,3,0>(in_x, in_P, h_6, H_6, NULL, in_z, in_R, in_ea, MAHA_THRESH_6);
      }
    
      void update_20(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
        update<1,3,0>(in_x, in_P, h_20, H_20, NULL, in_z, in_R, in_ea, MAHA_THRESH_20);
      }
    
      void update_7(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
        update<1,3,0>(in_x, in_P, h_7, H_7, NULL, in_z, in_R, in_ea, MAHA_THRESH_7);
      }
    
      void update_21(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
        update<1,3,0>(in_x, in_P, h_21, H_21, NULL, in_z, in_R, in_ea, MAHA_THRESH_21);
      }
    
}
