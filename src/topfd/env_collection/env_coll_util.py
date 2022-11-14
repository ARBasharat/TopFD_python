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
import topfd.score.compute_score_components as component_score
import topfd.util.utility_functions as utility_functions
from topfd.env_collection.env_collection import EnvCollection


def get_charge_range(peak_matrix, seed_env, mass_tole, max_miss_num, para_max_charge):
  valid = env_set_util.check_valid_env_set(peak_matrix, seed_env, mass_tole)
  base_charge = seed_env.charge
  if not valid:
    return [base_charge, base_charge]

  # search backward
  min_charge = seed_env.charge
  charge = seed_env.charge - 1
  miss_num = 0
  while charge >= 1:
    env = seed_env.get_new_charge_env(charge)
    valid = env_set_util.check_valid_env_set(peak_matrix, env, mass_tole, 2)
    if not valid: 
      miss_num = miss_num + 1
    else:
      miss_num = 0
      min_charge = charge
    if miss_num >= max_miss_num:
      break
    # print("charge", charge, "miss_num", miss_num)
    # print([(p.pos, p.inte) for p in env.peak_list])
    charge = charge - 1
  # search forward
  max_charge = seed_env.charge
  charge = seed_env.charge + 1
  while charge <= para_max_charge:
    env = seed_env.get_new_charge_env(charge)
    valid = env_set_util.check_valid_env_set(peak_matrix, env, mass_tole, 2)
    if not valid: 
      miss_num = miss_num + 1
    else:
      miss_num = 0
      max_charge = charge
    if miss_num >= max_miss_num:
      break
    charge = charge + 1
  #print("min charge", min_charge, "base_charge", seed_env.charge, "max charge", max_charge)
  return [min_charge, max_charge]


def select_best_seed_envelope(peak_matrix, seed_env, mass_tole, env_base):
  selected_envelope = None
  max_corr = 0.5
  for shift_num in range(-2, 3):
    s_env = seed_env.get_shifted_seed_envelope(env_base, shift_num)
    valid = env_set_util.check_valid_env_set(peak_matrix, s_env, mass_tole)
    if valid:
      env_set_util.comp_peak_start_end_idx(peak_matrix, s_env.peak_list, mass_tole)
      exp_env = env_set_util.get_match_exp_env(peak_matrix.matrix[s_env.spec_id], s_env, mass_tole)
      exp_inte = [p.inte if p is not None else 0 for p in exp_env.peak_list]
      exp_inte = [i/max(exp_inte) for i in exp_inte]
      theo_inte = [p.inte if p is not None else 0 for p in s_env.peak_list]
      corr = pearsonr(exp_inte, theo_inte)[0]
      if corr >= max_corr:
        selected_envelope  = s_env
        max_corr = corr
  return selected_envelope
    
def find_env_collection(peak_matrix, seed_env, mass_tole, max_miss_env, max_miss_charge, 
    max_miss_peak, para_max_charge, ratio_multi, env_base):
  
  env = select_best_seed_envelope(peak_matrix, seed_env, mass_tole, env_base)
  if env is None:
    return None
  [min_charge, max_charge] = get_charge_range(peak_matrix, env, mass_tole, max_miss_charge, para_max_charge)
  #print("min charge", min_charge, "base charge", env.charge, "max charge", max_charge)
  top_peak_env_set = env_set_util.get_env_set_by_three_peaks(peak_matrix, env, mass_tole, max_miss_env)
  if top_peak_env_set is None:
    return None
  start_spec_id = top_peak_env_set.get_start_spec_id()
  end_spec_id = top_peak_env_set.get_end_spec_id()
  #print("start spec_id", start_spec_id, "end spec_id", end_spec_id)

  inte_ratio = top_peak_env_set.get_seed_inte_ratio() * ratio_multi
  base_inte = peak_matrix.min_inte
  #env_set_util.print_env(env, inte_ratio)
  env.remove_low_inte_peaks(inte_ratio, base_inte)
  #print("ratio", inte_ratio, "base_inte", base_inte)
  #env_set_util.print_env(env, inte_ratio)
  env_set_list = []
  for charge in range(min_charge, max_charge + 1):
    cur_env = env.get_new_charge_env(charge)    
    env_set = env_set_util.find_env_set(peak_matrix, cur_env, mass_tole, start_spec_id, end_spec_id)
    #env_set.plot()
    if env_set is not None:
      env_set.remove_all_non_consecutive_peaks(max_miss_peak)
    #env_set.plot()
      env_set_list.append(env_set)
  if len(env_set_list) == 0:
    return None
  env_coll = EnvCollection(env, env_set_list, min_charge, max_charge, start_spec_id, end_spec_id) 
  return env_coll

def get_charge_env_list(peak_matrix, env, top_peak_env_set, para_max_charge,
                        mass_tole, max_miss_peak, max_miss_charge, max_miss_env, snr):
  start_spec_id = top_peak_env_set.start_spec_id
  end_spec_id = top_peak_env_set.end_spec_id
  env_set_list = []
  charge = env.charge - 1
  miss_num = 0
  while (charge >= 1):
    cur_env = env.get_new_charge_env(charge)
    env_set_util.comp_peak_start_end_idx(peak_matrix, cur_env, mass_tole);
    env_set = env_set_util.find_env_set(peak_matrix, cur_env, mass_tole, start_spec_id, end_spec_id, snr)
    charge = charge - 1;
    if env_set is None:
      miss_num = miss_num + 1
    else:
      env_set.refine_feature_boundary()
      if (not env_set_util.check_valid_env_set(peak_matrix, top_peak_env_set)):
        miss_num = miss_num + 1
      else:
        miss_num = 0
        env_set_list.append(env_set)
    if (miss_num >= max_miss_charge): break

  miss_num = 0
  charge = env.charge + 1
  while (charge <= para_max_charge):
    cur_env = env.get_new_charge_env(charge);
    env_set_util.comp_peak_start_end_idx(peak_matrix, cur_env, mass_tole)
    env_set = env_set_util.find_env_set(peak_matrix, cur_env, mass_tole, start_spec_id, end_spec_id, snr)
    charge = charge + 1
    if env_set is None:
      miss_num = miss_num + 1
    else:
      env_set.refine_feature_boundary()
      if (not env_set_util.check_valid_env_set(peak_matrix, env_set)):
        miss_num = miss_num + 1
      else:
        miss_num = 0
        env_set_list.append(env_set)
    if (miss_num >= max_miss_charge): break
  
  env_set_list.sort(key=lambda x: x.seed_env.charge, reverse=False)
  return env_set_list
                                              
def find_env_collection(peak_matrix, env, mass_tole, max_miss_env, max_miss_charge, max_miss_peak,
                        para_max_charge, ratio_multi, match_peak_tole, env_base, snr):
    top_peak_env_set = env_set_util.get_env_set(peak_matrix, env, mass_tole, max_miss_env, snr)
    if top_peak_env_set is None: return None
    
    top_peak_env_set.refine_feature_boundary();
    if (not env_set_util.check_valid_env_set_seed_env(peak_matrix, top_peak_env_set)): return None
    even_odd_peak_ratios = component_score.get_agg_odd_even_peak_ratio(top_peak_env_set)
    if abs(even_odd_peak_ratios) > 0.4:
      env = utility_functions.test_half_charge_state(peak_matrix, env, top_peak_env_set, even_odd_peak_ratios, mass_tole, env_base, snr)
      if env is None: return None
      tmp_peak_env_set = env_set_util.get_env_set(peak_matrix, env, mass_tole, max_miss_env, snr)
      if tmp_peak_env_set is not None:
        top_peak_env_set = tmp_peak_env_set
        top_peak_env_set.refine_feature_boundary()
        if (not env_set_util.check_valid_env_set_seed_env(peak_matrix, top_peak_env_set)): return None
      else:
        return None

    start_spec_id = top_peak_env_set.start_spec_id
    end_spec_id = top_peak_env_set.end_spec_id
    env_set_list = get_charge_env_list(peak_matrix, env, top_peak_env_set, para_max_charge, mass_tole, max_miss_peak, max_miss_charge, ratio_multi, snr);
    env_set_list.append(top_peak_env_set)
    
    env_set_list.sort(key=lambda x: x.seed_env.charge, reverse=False)
    min_charge = env_set_list[0].seed_env.charge
    max_charge = env_set_list[-1].seed_env.charge
    if len(env_set_list) == 0: return None
    env_coll = EnvCollection(env, env_set_list, min_charge, max_charge, start_spec_id, end_spec_id)
    return env_coll

def merge_overlapping_charge_features(f, env_coll):
  parent_charge_states = [es.seed_env.charge for es in f.env_set_list]
  for feature in env_coll.env_set_list:
    if (sum([1 for i in parent_charge_states if i == feature.seed_env.charge]) > 0):
      f.env_set_list.append(feature)
  
def check_charge_state_distance(parent_charge_states, charge_state):
  min_charge_diff = 10000000
  for parent_charge_state in parent_charge_states:
    charge_diff = abs(charge_state - parent_charge_state)
    if (charge_diff < min_charge_diff):
      min_charge_diff = charge_diff
  if (min_charge_diff > 2):
    return False
  return True
    
def check_overlap(spectra_list, f, feature_start_rt, feature_end_rt, time_tol):
  start_rt = spectra_list[f.start_spec_id][2]
  end_rt = spectra_list[f.end_spec_id][2]
  start = -1
  if (start_rt <= feature_start_rt):
    start = feature_start_rt
  else:
    start = start_rt
  end = -1
  if (start > -1):
    if (end_rt <= feature_end_rt):
      end = end_rt
    else:
      end = feature_end_rt

  status = False
  if (end > - 1):
    overlapping_rt_range = end - start
    if (overlapping_rt_range > 0):
      feature_rt_range = feature_end_rt - feature_start_rt
      feature_coverage = overlapping_rt_range / feature_rt_range
      if (feature_coverage > time_tol):
        status = True
  return status

def check_in_existing_features(peak_matrix, env_coll, env_coll_list, match_envelope_tolerance, time_tol):
  mass_tol = match_envelope_tolerance * env_coll.seed_env.mass
  neighborFeatureList_charge_states = [es.seed_env.charge for es in env_coll.env_set_list]
  extended_masses = [env_coll.seed_env.mass - 1.00235, env_coll.seed_env.mass, env_coll.seed_env.mass + 1.00235]
  num_env_colls = len(env_coll_list)
  spectra_list = peak_matrix.specs
  feature_start_rt = spectra_list[env_coll.start_spec_id][2]
  feature_end_rt = spectra_list[env_coll.end_spec_id][2]

  ### RT OVERLAPPPPP
  selected_features = []
  for i in range(0, num_env_colls):
    if (check_overlap(spectra_list, env_coll_list[i], feature_start_rt, feature_end_rt, time_tol)):
      min_mass_diff = 100000000
      for ext_mass in extended_masses:
        mass_diff = abs(ext_mass - env_coll_list[i].seed_env.mass)
        if (mass_diff < min_mass_diff):
          min_mass_diff = mass_diff
      if (min_mass_diff < mass_tol):
        selected_features.append(i)
    
  status = True
  overlap_charge = False
  for f_idx in selected_features:
    f = env_coll_list[f_idx]
    parent_charge_states = [es.seed_env.charge for es in f.env_set_list]
    for charge_state in neighborFeatureList_charge_states:
      status = check_charge_state_distance(parent_charge_states, charge_state)
      if (sum([1 for i in parent_charge_states if i == charge_state]) > 0):
        overlap_charge = True

    if status and (not overlap_charge):
      for feature in env_coll.env_set_list:
        f.env_set_list.append(feature)
        return True

    if status and overlap_charge:
      merge_overlapping_charge_features(f, env_coll)
      return True
  return False
