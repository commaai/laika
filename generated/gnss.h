/******************************************************************************
 *                      Code generated with sympy 1.5.1                       *
 *                                                                            *
 *              See http://www.sympy.org/ for more information.               *
 *                                                                            *
 *                         This file is part of 'ekf'                         *
 ******************************************************************************/
void err_fun(double *nom_x, double *delta_x, double *out_2572225847926737909);
void inv_err_fun(double *nom_x, double *true_x, double *out_539577615850755275);
void H_mod_fun(double *state, double *out_1352348085656852477);
void f_fun(double *state, double dt, double *out_8900138899586851029);
void F_fun(double *state, double dt, double *out_3235793707817571148);
void h_6(double *state, double *sat_pos, double *out_6606989255780333083);
void H_6(double *state, double *sat_pos, double *out_4785527618276088513);
void h_20(double *state, double *sat_pos, double *out_764831846531854296);
void H_20(double *state, double *sat_pos, double *out_3111045652100265697);
void h_7(double *state, double *sat_pos_vel, double *out_1935398902179795105);
void H_7(double *state, double *sat_pos_vel, double *out_6324310137951649025);
void h_21(double *state, double *sat_pos_vel, double *out_1935398902179795105);
void H_21(double *state, double *sat_pos_vel, double *out_6324310137951649025);
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