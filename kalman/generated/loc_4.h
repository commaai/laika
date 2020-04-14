/******************************************************************************
 *                      Code generated with sympy 1.5.1                       *
 *                                                                            *
 *              See http://www.sympy.org/ for more information.               *
 *                                                                            *
 *                         This file is part of 'ekf'                         *
 ******************************************************************************/
void err_fun(double *nom_x, double *delta_x, double *out_3107041075767078466);
void inv_err_fun(double *nom_x, double *true_x, double *out_139113788252016351);
void H_mod_fun(double *state, double *out_7622589417791933085);
void f_fun(double *state, double dt, double *out_6259647588555080807);
void F_fun(double *state, double dt, double *out_4489647396100515115);
void h_3(double *state, double *unused, double *out_7404683662349542347);
void H_3(double *state, double *unused, double *out_101926284974617469);
void h_4(double *state, double *unused, double *out_6607579711337344056);
void H_4(double *state, double *unused, double *out_3611008767552414035);
void h_9(double *state, double *unused, double *out_7445558704950768452);
void H_9(double *state, double *unused, double *out_1902375512790326020);
void h_10(double *state, double *unused, double *out_1448521894063138916);
void H_10(double *state, double *unused, double *out_5465019816330064629);
void h_6(double *state, double *sat_pos, double *out_141421789267001493);
void H_6(double *state, double *sat_pos, double *out_7135591810923355856);
void h_20(double *state, double *sat_pos, double *out_8776255657317534026);
void H_20(double *state, double *sat_pos, double *out_3328049729443289283);
void h_7(double *state, double *sat_pos_vel, double *out_3656109858763732733);
void H_7(double *state, double *sat_pos_vel, double *out_2675490248515020096);
void h_21(double *state, double *sat_pos_vel, double *out_3656109858763732733);
void H_21(double *state, double *sat_pos_vel, double *out_2675490248515020096);
void h_12(double *state, double *unused, double *out_7618137861830056825);
void H_12(double *state, double *unused, double *out_8477806963565060239);
void h_13(double *state, double *unused, double *out_1462080865256592459);
void H_13(double *state, double *unused, double *out_4112326350352683101);
void h_14(double *state, double *unused, double *out_7445558704950768452);
void H_14(double *state, double *unused, double *out_1902375512790326020);
void h_19(double *state, double *unused, double *out_9075765050920863556);
void H_19(double *state, double *unused, double *out_1729225573919485962);
void h_11(double *state, double *orb_epos_sym, double *out_697467670625335380);
void H_11(double *state, double *orb_epos_sym, double *out_1706546095113939193);
void h_16(double *state, double *track_epos_sym, double *out_2235929451854285060);
void H_16(double *state, double *track_epos_sym, double *out_6576241814830949509);
void He_16(double *state, double *track_epos_sym, double *out_6549761919614027088);
void h_15(double *state, double *track_epos_sym, double *out_8792616793400522944);
void H_15(double *state, double *track_epos_sym, double *out_4325265392737596187);
void He_15(double *state, double *track_epos_sym, double *out_2846145592310636019);
void h_17(double *state, double *track_epos_sym, double *out_8792616793400522944);
void H_17(double *state, double *track_epos_sym, double *out_4325265392737596187);
#define DIM 57
#define EDIM 52
#define MEDIM 28
typedef void (*Hfun)(double *, double *, double *);

void predict(double *x, double *P, double *Q, double dt);
const static double MAHA_THRESH_3 = 3.841459;
void update_3(double *, double *, double *, double *, double *);
const static double MAHA_THRESH_4 = 7.814728;
void update_4(double *, double *, double *, double *, double *);
const static double MAHA_THRESH_9 = 7.814728;
void update_9(double *, double *, double *, double *, double *);
const static double MAHA_THRESH_10 = 7.814728;
void update_10(double *, double *, double *, double *, double *);
const static double MAHA_THRESH_6 = 3.841459;
void update_6(double *, double *, double *, double *, double *);
const static double MAHA_THRESH_20 = 3.841459;
void update_20(double *, double *, double *, double *, double *);
const static double MAHA_THRESH_7 = 3.841459;
void update_7(double *, double *, double *, double *, double *);
const static double MAHA_THRESH_21 = 3.841459;
void update_21(double *, double *, double *, double *, double *);
const static double MAHA_THRESH_12 = 7.814728;
void update_12(double *, double *, double *, double *, double *);
const static double MAHA_THRESH_13 = 7.814728;
void update_13(double *, double *, double *, double *, double *);
const static double MAHA_THRESH_14 = 7.814728;
void update_14(double *, double *, double *, double *, double *);
const static double MAHA_THRESH_19 = 7.814728;
void update_19(double *, double *, double *, double *, double *);
const static double MAHA_THRESH_11 = 5.991465;
void update_11(double *, double *, double *, double *, double *);
const static double MAHA_THRESH_16 = 24.995790;
void update_16(double *, double *, double *, double *, double *);
const static double MAHA_THRESH_15 = 18.307038;
void update_15(double *, double *, double *, double *, double *);
const static double MAHA_THRESH_17 = 18.307038;
void update_17(double *, double *, double *, double *, double *);