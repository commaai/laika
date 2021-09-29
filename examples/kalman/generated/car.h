/******************************************************************************
 *                      Code generated with sympy 1.5.1                       *
 *                                                                            *
 *              See http://www.sympy.org/ for more information.               *
 *                                                                            *
 *                         This file is part of 'ekf'                         *
 ******************************************************************************/
void err_fun(double *nom_x, double *delta_x, double *out_6362621761555203585);
void inv_err_fun(double *nom_x, double *true_x, double *out_2288631393642840147);
void H_mod_fun(double *state, double *out_5565927872825724967);
void f_fun(double *state, double dt, double *out_6677597704705500997);
void F_fun(double *state, double dt, double *out_2542969289660916450);
void h_25(double *state, double *unused, double *out_3420596993672347610);
void H_25(double *state, double *unused, double *out_2900106186793674343);
void h_24(double *state, double *unused, double *out_7573029528848381135);
void H_24(double *state, double *unused, double *out_2939794646276439718);
void h_26(double *state, double *unused, double *out_2331567316550030204);
void H_26(double *state, double *unused, double *out_8639899703473690023);
void h_27(double *state, double *unused, double *out_1581076273988498035);
void H_27(double *state, double *unused, double *out_2400872300504788144);
void h_29(double *state, double *unused, double *out_6311863220896025324);
void H_29(double *state, double *unused, double *out_2108940206837862040);
void h_28(double *state, double *unused, double *out_4042592689951595552);
void H_28(double *state, double *unused, double *out_8476395214944423276);
#define DIM 8
#define EDIM 8
#define MEDIM 8
typedef void (*Hfun)(double *, double *, double *);

void predict(double *x, double *P, double *Q, double dt);
const static double MAHA_THRESH_25 = 3.841459;
void update_25(double *, double *, double *, double *, double *);
const static double MAHA_THRESH_24 = 5.991465;
void update_24(double *, double *, double *, double *, double *);
const static double MAHA_THRESH_26 = 3.841459;
void update_26(double *, double *, double *, double *, double *);
const static double MAHA_THRESH_27 = 3.841459;
void update_27(double *, double *, double *, double *, double *);
const static double MAHA_THRESH_29 = 3.841459;
void update_29(double *, double *, double *, double *, double *);
const static double MAHA_THRESH_28 = 5.991465;
void update_28(double *, double *, double *, double *, double *);
void set_mass(double x);

void set_rotational_inertia(double x);

void set_center_to_front(double x);

void set_center_to_rear(double x);

void set_stiffness_front(double x);

void set_stiffness_rear(double x);
