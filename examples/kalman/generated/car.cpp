
extern "C"{

double mass;

void set_mass(double x){ mass = x;}

double rotational_inertia;

void set_rotational_inertia(double x){ rotational_inertia = x;}

double center_to_front;

void set_center_to_front(double x){ center_to_front = x;}

double center_to_rear;

void set_center_to_rear(double x){ center_to_rear = x;}

double stiffness_front;

void set_stiffness_front(double x){ stiffness_front = x;}

double stiffness_rear;

void set_stiffness_rear(double x){ stiffness_rear = x;}

}
extern "C" {
#include <math.h>
/******************************************************************************
 *                      Code generated with sympy 1.5.1                       *
 *                                                                            *
 *              See http://www.sympy.org/ for more information.               *
 *                                                                            *
 *                         This file is part of 'ekf'                         *
 ******************************************************************************/
void err_fun(double *nom_x, double *delta_x, double *out_6362621761555203585) {
   out_6362621761555203585[0] = delta_x[0] + nom_x[0];
   out_6362621761555203585[1] = delta_x[1] + nom_x[1];
   out_6362621761555203585[2] = delta_x[2] + nom_x[2];
   out_6362621761555203585[3] = delta_x[3] + nom_x[3];
   out_6362621761555203585[4] = delta_x[4] + nom_x[4];
   out_6362621761555203585[5] = delta_x[5] + nom_x[5];
   out_6362621761555203585[6] = delta_x[6] + nom_x[6];
   out_6362621761555203585[7] = delta_x[7] + nom_x[7];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_2288631393642840147) {
   out_2288631393642840147[0] = -nom_x[0] + true_x[0];
   out_2288631393642840147[1] = -nom_x[1] + true_x[1];
   out_2288631393642840147[2] = -nom_x[2] + true_x[2];
   out_2288631393642840147[3] = -nom_x[3] + true_x[3];
   out_2288631393642840147[4] = -nom_x[4] + true_x[4];
   out_2288631393642840147[5] = -nom_x[5] + true_x[5];
   out_2288631393642840147[6] = -nom_x[6] + true_x[6];
   out_2288631393642840147[7] = -nom_x[7] + true_x[7];
}
void H_mod_fun(double *state, double *out_5565927872825724967) {
   out_5565927872825724967[0] = 1.0;
   out_5565927872825724967[1] = 0.0;
   out_5565927872825724967[2] = 0.0;
   out_5565927872825724967[3] = 0.0;
   out_5565927872825724967[4] = 0.0;
   out_5565927872825724967[5] = 0.0;
   out_5565927872825724967[6] = 0.0;
   out_5565927872825724967[7] = 0.0;
   out_5565927872825724967[8] = 0.0;
   out_5565927872825724967[9] = 1.0;
   out_5565927872825724967[10] = 0.0;
   out_5565927872825724967[11] = 0.0;
   out_5565927872825724967[12] = 0.0;
   out_5565927872825724967[13] = 0.0;
   out_5565927872825724967[14] = 0.0;
   out_5565927872825724967[15] = 0.0;
   out_5565927872825724967[16] = 0.0;
   out_5565927872825724967[17] = 0.0;
   out_5565927872825724967[18] = 1.0;
   out_5565927872825724967[19] = 0.0;
   out_5565927872825724967[20] = 0.0;
   out_5565927872825724967[21] = 0.0;
   out_5565927872825724967[22] = 0.0;
   out_5565927872825724967[23] = 0.0;
   out_5565927872825724967[24] = 0.0;
   out_5565927872825724967[25] = 0.0;
   out_5565927872825724967[26] = 0.0;
   out_5565927872825724967[27] = 1.0;
   out_5565927872825724967[28] = 0.0;
   out_5565927872825724967[29] = 0.0;
   out_5565927872825724967[30] = 0.0;
   out_5565927872825724967[31] = 0.0;
   out_5565927872825724967[32] = 0.0;
   out_5565927872825724967[33] = 0.0;
   out_5565927872825724967[34] = 0.0;
   out_5565927872825724967[35] = 0.0;
   out_5565927872825724967[36] = 1.0;
   out_5565927872825724967[37] = 0.0;
   out_5565927872825724967[38] = 0.0;
   out_5565927872825724967[39] = 0.0;
   out_5565927872825724967[40] = 0.0;
   out_5565927872825724967[41] = 0.0;
   out_5565927872825724967[42] = 0.0;
   out_5565927872825724967[43] = 0.0;
   out_5565927872825724967[44] = 0.0;
   out_5565927872825724967[45] = 1.0;
   out_5565927872825724967[46] = 0.0;
   out_5565927872825724967[47] = 0.0;
   out_5565927872825724967[48] = 0.0;
   out_5565927872825724967[49] = 0.0;
   out_5565927872825724967[50] = 0.0;
   out_5565927872825724967[51] = 0.0;
   out_5565927872825724967[52] = 0.0;
   out_5565927872825724967[53] = 0.0;
   out_5565927872825724967[54] = 1.0;
   out_5565927872825724967[55] = 0.0;
   out_5565927872825724967[56] = 0.0;
   out_5565927872825724967[57] = 0.0;
   out_5565927872825724967[58] = 0.0;
   out_5565927872825724967[59] = 0.0;
   out_5565927872825724967[60] = 0.0;
   out_5565927872825724967[61] = 0.0;
   out_5565927872825724967[62] = 0.0;
   out_5565927872825724967[63] = 1.0;
}
void f_fun(double *state, double dt, double *out_6677597704705500997) {
   out_6677597704705500997[0] = state[0];
   out_6677597704705500997[1] = state[1];
   out_6677597704705500997[2] = state[2];
   out_6677597704705500997[3] = state[3];
   out_6677597704705500997[4] = state[4];
   out_6677597704705500997[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_6677597704705500997[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_6677597704705500997[7] = state[7];
}
void F_fun(double *state, double dt, double *out_2542969289660916450) {
   out_2542969289660916450[0] = 1;
   out_2542969289660916450[1] = 0;
   out_2542969289660916450[2] = 0;
   out_2542969289660916450[3] = 0;
   out_2542969289660916450[4] = 0;
   out_2542969289660916450[5] = 0;
   out_2542969289660916450[6] = 0;
   out_2542969289660916450[7] = 0;
   out_2542969289660916450[8] = 0;
   out_2542969289660916450[9] = 1;
   out_2542969289660916450[10] = 0;
   out_2542969289660916450[11] = 0;
   out_2542969289660916450[12] = 0;
   out_2542969289660916450[13] = 0;
   out_2542969289660916450[14] = 0;
   out_2542969289660916450[15] = 0;
   out_2542969289660916450[16] = 0;
   out_2542969289660916450[17] = 0;
   out_2542969289660916450[18] = 1;
   out_2542969289660916450[19] = 0;
   out_2542969289660916450[20] = 0;
   out_2542969289660916450[21] = 0;
   out_2542969289660916450[22] = 0;
   out_2542969289660916450[23] = 0;
   out_2542969289660916450[24] = 0;
   out_2542969289660916450[25] = 0;
   out_2542969289660916450[26] = 0;
   out_2542969289660916450[27] = 1;
   out_2542969289660916450[28] = 0;
   out_2542969289660916450[29] = 0;
   out_2542969289660916450[30] = 0;
   out_2542969289660916450[31] = 0;
   out_2542969289660916450[32] = 0;
   out_2542969289660916450[33] = 0;
   out_2542969289660916450[34] = 0;
   out_2542969289660916450[35] = 0;
   out_2542969289660916450[36] = 1;
   out_2542969289660916450[37] = 0;
   out_2542969289660916450[38] = 0;
   out_2542969289660916450[39] = 0;
   out_2542969289660916450[40] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_2542969289660916450[41] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_2542969289660916450[42] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_2542969289660916450[43] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_2542969289660916450[44] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_2542969289660916450[45] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_2542969289660916450[46] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_2542969289660916450[47] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_2542969289660916450[48] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_2542969289660916450[49] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_2542969289660916450[50] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_2542969289660916450[51] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_2542969289660916450[52] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_2542969289660916450[53] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_2542969289660916450[54] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_2542969289660916450[55] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_2542969289660916450[56] = 0;
   out_2542969289660916450[57] = 0;
   out_2542969289660916450[58] = 0;
   out_2542969289660916450[59] = 0;
   out_2542969289660916450[60] = 0;
   out_2542969289660916450[61] = 0;
   out_2542969289660916450[62] = 0;
   out_2542969289660916450[63] = 1;
}
void h_25(double *state, double *unused, double *out_3420596993672347610) {
   out_3420596993672347610[0] = state[6];
}
void H_25(double *state, double *unused, double *out_2900106186793674343) {
   out_2900106186793674343[0] = 0;
   out_2900106186793674343[1] = 0;
   out_2900106186793674343[2] = 0;
   out_2900106186793674343[3] = 0;
   out_2900106186793674343[4] = 0;
   out_2900106186793674343[5] = 0;
   out_2900106186793674343[6] = 1;
   out_2900106186793674343[7] = 0;
}
void h_24(double *state, double *unused, double *out_7573029528848381135) {
   out_7573029528848381135[0] = state[4];
   out_7573029528848381135[1] = state[5];
}
void H_24(double *state, double *unused, double *out_2939794646276439718) {
   out_2939794646276439718[0] = 0;
   out_2939794646276439718[1] = 0;
   out_2939794646276439718[2] = 0;
   out_2939794646276439718[3] = 0;
   out_2939794646276439718[4] = 1;
   out_2939794646276439718[5] = 0;
   out_2939794646276439718[6] = 0;
   out_2939794646276439718[7] = 0;
   out_2939794646276439718[8] = 0;
   out_2939794646276439718[9] = 0;
   out_2939794646276439718[10] = 0;
   out_2939794646276439718[11] = 0;
   out_2939794646276439718[12] = 0;
   out_2939794646276439718[13] = 1;
   out_2939794646276439718[14] = 0;
   out_2939794646276439718[15] = 0;
}
void h_26(double *state, double *unused, double *out_2331567316550030204) {
   out_2331567316550030204[0] = state[7];
}
void H_26(double *state, double *unused, double *out_8639899703473690023) {
   out_8639899703473690023[0] = 0;
   out_8639899703473690023[1] = 0;
   out_8639899703473690023[2] = 0;
   out_8639899703473690023[3] = 0;
   out_8639899703473690023[4] = 0;
   out_8639899703473690023[5] = 0;
   out_8639899703473690023[6] = 0;
   out_8639899703473690023[7] = 1;
}
void h_27(double *state, double *unused, double *out_1581076273988498035) {
   out_1581076273988498035[0] = state[3];
}
void H_27(double *state, double *unused, double *out_2400872300504788144) {
   out_2400872300504788144[0] = 0;
   out_2400872300504788144[1] = 0;
   out_2400872300504788144[2] = 0;
   out_2400872300504788144[3] = 1;
   out_2400872300504788144[4] = 0;
   out_2400872300504788144[5] = 0;
   out_2400872300504788144[6] = 0;
   out_2400872300504788144[7] = 0;
}
void h_29(double *state, double *unused, double *out_6311863220896025324) {
   out_6311863220896025324[0] = state[1];
}
void H_29(double *state, double *unused, double *out_2108940206837862040) {
   out_2108940206837862040[0] = 0;
   out_2108940206837862040[1] = 1;
   out_2108940206837862040[2] = 0;
   out_2108940206837862040[3] = 0;
   out_2108940206837862040[4] = 0;
   out_2108940206837862040[5] = 0;
   out_2108940206837862040[6] = 0;
   out_2108940206837862040[7] = 0;
}
void h_28(double *state, double *unused, double *out_4042592689951595552) {
   out_4042592689951595552[0] = state[5];
   out_4042592689951595552[1] = state[6];
}
void H_28(double *state, double *unused, double *out_8476395214944423276) {
   out_8476395214944423276[0] = 0;
   out_8476395214944423276[1] = 0;
   out_8476395214944423276[2] = 0;
   out_8476395214944423276[3] = 0;
   out_8476395214944423276[4] = 0;
   out_8476395214944423276[5] = 1;
   out_8476395214944423276[6] = 0;
   out_8476395214944423276[7] = 0;
   out_8476395214944423276[8] = 0;
   out_8476395214944423276[9] = 0;
   out_8476395214944423276[10] = 0;
   out_8476395214944423276[11] = 0;
   out_8476395214944423276[12] = 0;
   out_8476395214944423276[13] = 0;
   out_8476395214944423276[14] = 1;
   out_8476395214944423276[15] = 0;
}
}

extern "C"{
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

      void update_25(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
        update<1,3,0>(in_x, in_P, h_25, H_25, NULL, in_z, in_R, in_ea, MAHA_THRESH_25);
      }
    
      void update_24(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
        update<2,3,0>(in_x, in_P, h_24, H_24, NULL, in_z, in_R, in_ea, MAHA_THRESH_24);
      }
    
      void update_26(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
        update<1,3,0>(in_x, in_P, h_26, H_26, NULL, in_z, in_R, in_ea, MAHA_THRESH_26);
      }
    
      void update_27(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
        update<1,3,0>(in_x, in_P, h_27, H_27, NULL, in_z, in_R, in_ea, MAHA_THRESH_27);
      }
    
      void update_29(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
        update<1,3,0>(in_x, in_P, h_29, H_29, NULL, in_z, in_R, in_ea, MAHA_THRESH_29);
      }
    
      void update_28(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
        update<2,3,0>(in_x, in_P, h_28, H_28, NULL, in_z, in_R, in_ea, MAHA_THRESH_28);
      }
    
}
