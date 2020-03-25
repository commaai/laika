import sys
import os
from bisect import bisect_right
import sympy as sp
import numpy as np
from numpy import dot
from .ffi_wrapper import ffi_wrap, compile_code, wrap_compiled
from .sympy_helpers import sympy_into_c
import scipy
from scipy.stats import chi2


EXTERNAL_PATH = os.path.dirname(os.path.abspath(__file__))

def solve(a, b):
  if a.shape[0] == 1 and a.shape[1] == 1:
    #assert np.allclose(b/a[0][0], np.linalg.solve(a, b))
    return b/a[0][0]
  else:
    return np.linalg.solve(a, b)

def null(H, eps=1e-12):
  from scipy import linalg
  u, s, vh = linalg.svd(H)
  padding = max(0,np.shape(H)[1]-np.shape(s)[0])
  null_mask = np.concatenate(((s <= eps), np.ones((padding,),dtype=bool)),axis=0)
  null_space = scipy.compress(null_mask, vh, axis=0)
  return scipy.transpose(null_space)

def gen_code(name, f_sym, dt_sym, x_sym, obs_eqs, dim_x, dim_err, eskf_params=None, msckf_params=None, maha_test_kinds=[]):
  # optional state transition matrix, H modifier
  # and err_function if an error-state kalman filter (ESKF)
  # is desired. Best described in "Quaternion kinematics
  # for the error-state Kalman filter" by Joan Sola

  if eskf_params:
    err_eqs = eskf_params[0]
    inv_err_eqs = eskf_params[1]
    H_mod_sym = eskf_params[2]
    f_err_sym = eskf_params[3]
    x_err_sym = eskf_params[4]
  else:
    nom_x = sp.MatrixSymbol('nom_x',dim_x,1)
    true_x = sp.MatrixSymbol('true_x',dim_x,1)
    delta_x = sp.MatrixSymbol('delta_x',dim_x,1)
    err_function_sym = sp.Matrix(nom_x + delta_x)
    inv_err_function_sym = sp.Matrix(true_x - nom_x)
    err_eqs = [err_function_sym, nom_x, delta_x]
    inv_err_eqs = [inv_err_function_sym, nom_x, true_x]

    H_mod_sym = sp.Matrix(np.eye(dim_x))
    f_err_sym = f_sym
    x_err_sym = x_sym

  # This configures the multi-state augmentation
  # needed for EKF-SLAM with MSCKF (Mourikis et al 2007)
  if msckf_params:
    msckf = True
    dim_main = msckf_params[0]      # size of the main state
    dim_augment = msckf_params[1]   # size of one augment state chunk
    dim_main_err = msckf_params[2]
    dim_augment_err = msckf_params[3]
    N = msckf_params[4]
    feature_track_kinds = msckf_params[5]
    assert dim_main + dim_augment*N == dim_x
    assert dim_main_err + dim_augment_err*N == dim_err
  else:
    msckf = False
    dim_main = dim_x
    dim_augment = 0
    dim_main_err = dim_err
    dim_augment_err = 0
    N = 0

  # linearize with jacobians
  F_sym = f_err_sym.jacobian(x_err_sym)
  for sym in x_err_sym:
    F_sym = F_sym.subs(sym, 0)
  for i in xrange(len(obs_eqs)):
    obs_eqs[i].append(obs_eqs[i][0].jacobian(x_sym))
    if msckf and obs_eqs[i][1] in feature_track_kinds:
      obs_eqs[i].append(obs_eqs[i][0].jacobian(obs_eqs[i][2]))
    else:
      obs_eqs[i].append(None)

  # collect sympy functions
  sympy_functions = []

  # error functions
  sympy_functions.append(('err_fun', err_eqs[0], [err_eqs[1], err_eqs[2]]))
  sympy_functions.append(('inv_err_fun', inv_err_eqs[0], [inv_err_eqs[1], inv_err_eqs[2]]))

  # H modifier for ESKF updates
  sympy_functions.append(('H_mod_fun', H_mod_sym, [x_sym]))

  # state propagation function 
  sympy_functions.append(('f_fun', f_sym, [x_sym, dt_sym]))
  sympy_functions.append(('F_fun', F_sym, [x_sym, dt_sym]))

  # observation functions
  for h_sym, kind, ea_sym, H_sym, He_sym in obs_eqs:
    sympy_functions.append(('h_%d' % kind, h_sym, [x_sym, ea_sym]))
    sympy_functions.append(('H_%d' % kind, H_sym, [x_sym, ea_sym]))
    if msckf and kind in feature_track_kinds:
      sympy_functions.append(('He_%d' % kind, He_sym, [x_sym, ea_sym]))

  # Generate and wrap all th c code 
  header, code = sympy_into_c(sympy_functions)
  extra_header = "#define DIM %d\n" % dim_x
  extra_header += "#define EDIM %d\n" % dim_err
  extra_header += "#define MEDIM %d\n" % dim_main_err
  extra_header += "typedef void (*Hfun)(double *, double *, double *);\n"

  extra_header += "\nvoid predict(double *x, double *P, double *Q, double dt);"

  extra_post = ""

  for h_sym, kind, ea_sym, H_sym, He_sym in obs_eqs:
    if msckf and kind in feature_track_kinds:
      He_str = 'He_%d' % kind
      ea_dim = ea_sym.shape[0]
    else:
      He_str = 'NULL'
      ea_dim = 1 # not really dim of ea but makes c function work
    maha_thresh = chi2.ppf(0.95, int(h_sym.shape[0])) # mahalanobis distance for outlier detection
    maha_test = kind in maha_test_kinds
    extra_post += """
      void update_%d(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
        update<%d,%d,%d>(in_x, in_P, h_%d, H_%d, %s, in_z, in_R, in_ea, MAHA_THRESH_%d);
      }
    """ % (kind, h_sym.shape[0], 3, maha_test, kind, kind, He_str, kind)
    extra_header += "\nconst static double MAHA_THRESH_%d = %f;" % (kind, maha_thresh)
    extra_header += "\nvoid update_%d(double *, double *, double *, double *, double *);" % kind

  code += "\n" + extra_header
  code += "\n" + open(os.path.join(EXTERNAL_PATH, "ekf_c.c")).read()
  code += "\n" + extra_post
  header += "\n" + extra_header
  compile_code(name, code, header, EXTERNAL_PATH)

class EKF_sym(object):
  def __init__(self, name, Q, x_initial, P_initial, dim_main, dim_main_err,
                     N=0, dim_augment=0, dim_augment_err=0, maha_test_kinds=[]):
    '''
    Generates process function and all
    observation functions for the kalman
    filter.
    '''
    if N > 0:
      self.msckf = True
    else:
      self.msckf = False
    self.N = N
    self.dim_augment = dim_augment
    self.dim_augment_err = dim_augment_err
    self.dim_main = dim_main
    self.dim_main_err = dim_main_err

    # state
    x_initial = x_initial.reshape((-1, 1))
    self.dim_x = x_initial.shape[0]
    self.dim_err = P_initial.shape[0]
    assert dim_main + dim_augment*N == self.dim_x
    assert dim_main_err + dim_augment_err*N == self.dim_err

    # kinds that should get mahalanobis distance
    # tested for outlier rejection
    self.maha_test_kinds = maha_test_kinds

    # process noise
    self.Q = Q

    # rewind stuff
    self.rewind_t = []
    self.rewind_states = []
    self.rewind_obscache = []
    self.init_state(x_initial, P_initial, None)

    ffi, lib = wrap_compiled(name, EXTERNAL_PATH)
    kinds, self.feature_track_kinds = [], []
    for func in dir(lib):
      if func[:2] == 'h_':
        kinds.append(int(func[2:]))
      if func[:3] == 'He_':
        self.feature_track_kinds.append(int(func[3:]))

    # wrap all the sympy functions
    def wrap_1lists(name):
      func = eval("lib.%s" % name, {"lib":lib})
      def ret(lst1, out):
        func(ffi.cast("double *", lst1.ctypes.data),
          ffi.cast("double *", out.ctypes.data))
      return ret
    def wrap_2lists(name):
      func = eval("lib.%s" % name, {"lib":lib})
      def ret(lst1, lst2, out):
        func(ffi.cast("double *", lst1.ctypes.data),
          ffi.cast("double *", lst2.ctypes.data),
          ffi.cast("double *", out.ctypes.data))
      return ret
    def wrap_1list_1float(name):
      func = eval("lib.%s" % name, {"lib":lib})
      def ret(lst1, fl, out):
        func(ffi.cast("double *", lst1.ctypes.data),
          ffi.cast("double", fl),
          ffi.cast("double *", out.ctypes.data))
      return ret

    self.f = wrap_1list_1float("f_fun")
    self.F = wrap_1list_1float("F_fun")

    self.err_function = wrap_2lists("err_fun")
    self.inv_err_function = wrap_2lists("inv_err_fun")
    self.H_mod = wrap_1lists("H_mod_fun")

    self.hs, self.Hs, self.Hes = {}, {}, {}
    for kind in kinds:
      self.hs[kind] = wrap_2lists("h_%d" % kind)
      self.Hs[kind] = wrap_2lists("H_%d" % kind)
      if self.msckf  and kind in self.feature_track_kinds:
        self.Hes[kind] = wrap_2lists("He_%d" % kind)

    # wrap the C++ predict function
    def _predict_blas(x, P, dt):
      lib.predict(ffi.cast("double *", x.ctypes.data),
                  ffi.cast("double *", P.ctypes.data),
                  ffi.cast("double *", self.Q.ctypes.data),
                  ffi.cast("double", dt))
      return x, P

    # wrap the C++ update function
    def fun_wrapper(f, kind):
      f = eval("lib.%s" % f, {"lib": lib})
      def _update_inner_blas(x, P, z, R, extra_args):
        f(ffi.cast("double *", x.ctypes.data),
          ffi.cast("double *", P.ctypes.data),
          ffi.cast("double *", z.ctypes.data),
          ffi.cast("double *", R.ctypes.data),
          ffi.cast("double *", extra_args.ctypes.data))
        if self.msckf and kind in self.feature_track_kinds:
          y = z[:-len(extra_args)]
        else:
          y = z
        return x, P, y
      return _update_inner_blas

    self._updates = {}
    for kind in kinds:
      self._updates[kind] = fun_wrapper("update_%d" % kind, kind)

    def _update_blas(x, P, kind, z, R, extra_args=[]):
        return self._updates[kind](x, P, z, R, extra_args)

    # assign the functions
    self._predict = _predict_blas
    #self._predict = self._predict_python
    self._update = _update_blas
    #self._update = self._update_python


  def init_state(self, state, covs, filter_time):
    self.x = np.array(state.reshape((-1, 1))).astype(np.float64)
    self.P = np.array(covs).astype(np.float64)
    self.filter_time = filter_time
    self.augment_times = [0]*self.N
    self.rewind_obscache = []
    self.rewind_t = []
    self.rewind_states = []

  def augment(self):
    # TODO this is not a generalized way of doing
    # this and implies that the augmented states
    # are simply the first (dim_augment_state)
    # elements of the main state.
    assert self.msckf
    d1 = self.dim_main
    d2 = self.dim_main_err
    d3 = self.dim_augment
    d4 = self.dim_augment_err
    # push through augmented states
    self.x[d1:-d3] = self.x[d1+d3:]
    self.x[-d3:] = self.x[:d3]
    assert self.x.shape == (self.dim_x, 1)
    # push through augmented covs
    assert self.P.shape == (self.dim_err, self.dim_err)
    P_reduced = self.P
    P_reduced = np.delete(P_reduced, np.s_[d2:d2+d4], axis=1)
    P_reduced = np.delete(P_reduced, np.s_[d2:d2+d4], axis=0)
    assert P_reduced.shape == (self.dim_err -d4, self.dim_err -d4)
    to_mult = np.zeros((self.dim_err, self.dim_err - d4))
    to_mult[:-d4,:] = np.eye(self.dim_err - d4)
    to_mult[-d4:,:d4] = np.eye(d4)
    self.P = to_mult.dot(P_reduced.dot(to_mult.T))
    self.augment_times = self.augment_times[1:]
    self.augment_times.append(self.filter_time)
    assert self.P.shape == (self.dim_err, self.dim_err)

  def state(self):
    return np.array(self.x).flatten()

  def covs(self):
    return self.P

  def rewind(self, t):
    # find where we are rewinding to
    idx = bisect_right(self.rewind_t, t)
    assert self.rewind_t[idx-1] <= t
    assert self.rewind_t[idx] > t    # must be true, or rewind wouldn't be called

    # set the state to the time right before that
    self.filter_time = self.rewind_t[idx-1]
    self.x[:] = self.rewind_states[idx-1][0]
    self.P[:] = self.rewind_states[idx-1][1]

    # return the observations we rewound over for fast forwarding
    ret = self.rewind_obscache[idx:]

    # throw away the old future
    # TODO: is this making a copy?
    self.rewind_t = self.rewind_t[:idx]
    self.rewind_states = self.rewind_states[:idx]
    self.rewind_obscache = self.rewind_obscache[:idx]

    return ret

  def checkpoint(self, obs):
    # push to rewinder
    self.rewind_t.append(self.filter_time)
    self.rewind_states.append((np.copy(self.x), np.copy(self.P)))
    self.rewind_obscache.append(obs)

    # only keep a certain number around
    REWIND_TO_KEEP = 512
    self.rewind_t = self.rewind_t[-REWIND_TO_KEEP:]
    self.rewind_states = self.rewind_states[-REWIND_TO_KEEP:]
    self.rewind_obscache = self.rewind_obscache[-REWIND_TO_KEEP:]

  def predict_and_update_batch(self, t, kind, z, R, extra_args=[[]], augment=False):
    # TODO handle rewinding at this level"

    # rewind
    if t < self.filter_time:
      if len(self.rewind_t) == 0 or t < self.rewind_t[0] or t < self.rewind_t[-1] -1.0:
        print("observation too old at %.3f with filter at %.3f, ignoring" % (t, self.filter_time))
        return None
      rewound = self.rewind(t)
    else:
      rewound = []

    ret = self._predict_and_update_batch(t, kind, z, R, extra_args, augment)

    # optional fast forward
    for r in rewound:
      self._predict_and_update_batch(*r)

    return ret

  def _predict_and_update_batch(self, t, kind, z, R, extra_args, augment=False):
    """The main kalman filter function
    Predicts the state and then updates a batch of observations

    dim_x: dimensionality of the state space
    dim_z: dimensionality of the observation and depends on kind
    n: number of observations

    Args:
      t                 (float): Time of observation
      kind                (int): Type of observation
      z         (vec [n,dim_z]): Measurements
      R  (mat [n,dim_z, dim_z]): Measurement Noise
      extra_args    (list, [n]): Values used in H computations
    """
    # initialize time
    if self.filter_time is None:
      self.filter_time = t

    # predict
    dt = t - self.filter_time
    assert dt >= 0
    self.x, self.P = self._predict(self.x, self.P, dt)
    self.filter_time = t
    xk_km1, Pk_km1 = np.copy(self.x).flatten(), np.copy(self.P)

    # update batch
    y = []
    for i in xrange(len(z)):
      # these are from the user, so we canonicalize them
      z_i = np.array(z[i], dtype=np.float64, order='F')
      R_i = np.array(R[i], dtype=np.float64, order='F')
      extra_args_i = np.array(extra_args[i], dtype=np.float64, order='F')
      # update
      self.x, self.P, y_i = self._update(self.x, self.P, kind, z_i, R_i, extra_args=extra_args_i)
      y.append(y_i)
    xk_k, Pk_k = np.copy(self.x).flatten(), np.copy(self.P)

    if augment:
      self.augment()

    # checkpoint
    self.checkpoint((t, kind, z, R, extra_args))

    return xk_km1, xk_k, Pk_km1, Pk_k, t, kind, y, z, extra_args


  def rts_smooth(self, estimates, norm_quats=False):
    '''
    Returns rts smoothed results of
    kalman filter estimates

    If the kalman state is augmented with
    old states only the main state is smoothed
    '''
    xk_n = estimates[-1][0]
    Pk_n = estimates[-1][2]
    Fk_1 = np.zeros(Pk_n.shape, dtype=np.float64)

    states_smoothed = [xk_n]
    covs_smoothed = [Pk_n]
    for k in xrange(len(estimates) - 2, -1, -1):
      xk1_n = xk_n
      if norm_quats:
        xk1_n[3:7] /= np.linalg.norm(xk1_n[3:7])
      Pk1_n = Pk_n

      xk1_k, _, Pk1_k, _, t2, _, _, _, _ = estimates[k + 1]
      _, xk_k, _, Pk_k, t1, _, _, _, _ = estimates[k]
      dt = t2 - t1
      self.F(xk_k, dt, Fk_1)

      d1 = self.dim_main
      d2 = self.dim_main_err
      Ck = np.linalg.solve(Pk1_k[:d2,:d2], Fk_1[:d2,:d2].dot(Pk_k[:d2,:d2].T)).T
      xk_n = xk_k
      delta_x = np.zeros((Pk_n.shape[0], 1), dtype=np.float64)
      self.inv_err_function(xk1_k, xk1_n, delta_x)
      delta_x[:d2] = Ck.dot(delta_x[:d2])
      x_new = np.zeros((xk_n.shape[0], 1), dtype=np.float64)
      self.err_function(xk_k, delta_x, x_new)
      xk_n[:d1] = x_new[:d1,0]
      Pk_n = Pk_k
      Pk_n[:d2,:d2] = Pk_k[:d2,:d2] + Ck.dot(Pk1_n[:d2,:d2] - Pk1_k[:d2,:d2]).dot(Ck.T)
      states_smoothed.append(xk_n)
      covs_smoothed.append(Pk_n)

    return np.flipud(np.vstack(states_smoothed)), np.stack(covs_smoothed, 0)[::-1]
