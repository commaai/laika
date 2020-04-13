/******************************************************************************
 *                      Code generated with sympy 1.5.1                       *
 *                                                                            *
 *              See http://www.sympy.org/ for more information.               *
 *                                                                            *
 *                         This file is part of 'ekf'                         *
 ******************************************************************************/
void err_fun(double *nom_x, double *delta_x, double *out_7861167219672258566);
void inv_err_fun(double *nom_x, double *true_x, double *out_4169199458110130867);
void H_mod_fun(double *state, double *out_4010408429597161981);
void f_fun(double *state, double dt, double *out_8715827380682604135);
void F_fun(double *state, double dt, double *out_1766557707574631373);
void h_3(double *state, double *unused, double *out_4764363220033308170);
void H_3(double *state, double *unused, double *out_6293854881692266722);
void h_4(double *state, double *unused, double *out_869294148103320751);
void H_4(double *state, double *unused, double *out_7966307925965131092);
void h_9(double *state, double *unused, double *out_1800975446315359444);
void H_9(double *state, double *unused, double *out_3839614762528009890);
void h_10(double *state, double *unused, double *out_2005568109157386036);
void H_10(double *state, double *unused, double *out_3558676140055266778);
void h_12(double *state, double *unused, double *out_4095445679533609210);
void H_12(double *state, double *unused, double *out_3422364558238493336);
void h_13(double *state, double *unused, double *out_9213323650548886526);
void H_13(double *state, double *unused, double *out_478573194713041427);
void h_14(double *state, double *unused, double *out_1800975446315359444);
void H_14(double *state, double *unused, double *out_3839614762528009890);
void h_19(double *state, double *unused, double *out_8083511536625772422);
void H_19(double *state, double *unused, double *out_8272294613630441071);
#define DIM 23
#define EDIM 22
#define MEDIM 22
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
const static double MAHA_THRESH_12 = 7.814728;
void update_12(double *, double *, double *, double *, double *);
const static double MAHA_THRESH_13 = 7.814728;
void update_13(double *, double *, double *, double *, double *);
const static double MAHA_THRESH_14 = 7.814728;
void update_14(double *, double *, double *, double *, double *);
const static double MAHA_THRESH_19 = 7.814728;
void update_19(double *, double *, double *, double *, double *);