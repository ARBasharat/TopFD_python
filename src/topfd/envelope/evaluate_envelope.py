##Copyright (c) 2014 - 2021, The Trustees of Indiana University.
##
##Licensed under the Apache License, Version 2.0 (the "License");
##you may not use this file except in compliance with the License.
##You may obtain a copy of the License at
##
##    http://www.apache.org/licenses/LICENSE-2.0
##
##Unless required by applicable law or agreed to in writing, software
##distributed under the License is distributed on an "AS IS" BASIS,
##WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##See the License for the specific language governing permissions and
##limitations under the License.

from scipy.stats import pearsonr
import topfd.env_set.env_set_util as env_set_util
import topfd.score.env_util as env_utils

def preprocess_env(peak_matrix, env, mass_tole, corr_tole, snr):
  min_mz = peak_matrix.min_mz - mass_tole
  max_mz = peak_matrix.max_mz + mass_tole
  env.rm_peaks(min_mz, max_mz)
  env_set_util.comp_peak_start_end_idx(peak_matrix, env, mass_tole)
  valid = evaluate_envelope(peak_matrix, env, mass_tole, corr_tole, snr)
  if (env.spec_id >= peak_matrix.spec_num):
    print("spec id", env.spec_id, "is out of range!")
    valid = False
  return valid

def evaluate_envelope(peak_matrix, env, mass_tole, corr_tole, snr):
  noise_inte = peak_matrix.min_inte
  exp_env = env_set_util.get_match_exp_env(peak_matrix, env, env.spec_id, mass_tole)
  experimental_envelope_inte = exp_env.get_inte_list()
  env_inte = env.get_inte_list()
  num_env_peaks = len(env_inte)
  inte_ratio = env_utils.calcInteRatio_scan(env_inte, experimental_envelope_inte);
  scaled_theo_inte = []
  for i in range(0, num_env_peaks):
    scaled_inte = inte_ratio * env_inte[i]
    if (scaled_inte < snr * noise_inte): break
    scaled_theo_inte.append(scaled_inte)
    
  for j in range(num_env_peaks-1, i-1, -1):
    env.peak_list.pop()
    experimental_envelope_inte.pop()

  if (not test_charge_state(env.charge, scaled_theo_inte)): return False
  return evaluate_envelope_pair(experimental_envelope_inte, scaled_theo_inte, corr_tole)

def test_charge_state(charge, seed_envelope_inte):
  if ((charge == 1 or charge == 2) and len(seed_envelope_inte) < 2):
    return False
  if (charge > 2 and charge < 15 and len(seed_envelope_inte) < 3):
    return False
  if (charge >= 15 and len(seed_envelope_inte) < 5):
    return False
  return True

def evaluate_envelope_pair(experimental_envelope_inte, scaled_theo_inte, tol):
  num_theo_peak = 0
  for i in scaled_theo_inte:
    if (i > 0):
      num_theo_peak = num_theo_peak + 1
  if (num_theo_peak == 0): return False
  corr = pearsonr(experimental_envelope_inte, scaled_theo_inte)
  if (corr[0] < tol): return False
  return True


