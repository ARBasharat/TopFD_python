#!/usr/bin/python3

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

import math
from scipy.stats import pearsonr
import topfd.score.env_util as env_utils

def get_theo_envelope_peak_intens(env_set):
  peaks = env_set.seed_env.peak_list
  theo_peak_intes = []
  for p in peaks:
    theo_peak_intes.append(p.inte)
  return theo_peak_intes

def get_agg_odd_even_peak_ratio(env_set):
  theo_inte = get_theo_envelope_peak_intens(env_set)
  aggregate_inte = env_utils.get_aggregate_envelopes_inte(env_set)
  normalized_aggregate_inte = []
  for inte in aggregate_inte:
    normalized_aggregate_inte.append(inte/max(aggregate_inte))
  sum_even_peaks = 0
  sum_even_peaks_theo = 0
  sum_odd_peaks = 0
  sum_odd_peaks_theo = 0
  for peak_idx in range(0, len(aggregate_inte)):
    if (peak_idx%2 == 0):
      sum_even_peaks = sum_even_peaks + normalized_aggregate_inte[peak_idx]
      sum_even_peaks_theo = sum_even_peaks_theo + theo_inte[peak_idx]
    else:
      sum_odd_peaks = sum_odd_peaks + normalized_aggregate_inte[peak_idx];
      sum_odd_peaks_theo = sum_odd_peaks_theo + theo_inte[peak_idx];
  inte_ratio = (sum_even_peaks/sum_even_peaks_theo) / (sum_odd_peaks/sum_odd_peaks_theo)
  if (inte_ratio <= 0):
    inte_ratio = 1
  return math.log10(inte_ratio)


def get_num_theo_peaks(theo_map):
  total_peaks = 0
  for scan_intes in theo_map:
    for peak_inte in scan_intes:
      if (peak_inte > 0):
        total_peaks = total_peaks + 1
  return total_peaks

def get_mz_errors(env_set):
  theo_dis = env_set.seed_env.get_pos_list()
  exp_envs = env_set.exp_env_list
  error_sum = 0
  for exp_env in exp_envs:
    peaks = exp_env.peak_list
    num_peaks = len(peaks)
    for peak_idx in range(0, num_peaks):
      peak = peaks[peak_idx]
      if peak is not None:
        cur_err = abs(peak.pos - theo_dis[peak_idx])
        error_sum = error_sum + cur_err
  return error_sum

# def get_agg_env_corr(env_coll):
#   selected_envelope_set = [env_set for env_set in env_coll.env_set_list if env_set.seed_env.charge == env_coll.seed_env.charge]
#   env_set = selected_envelope_set[0]
#   theo_inte = get_theo_envelope_peak_intens(env_set)  
#   aggregate_inte = env_utils.get_aggregate_envelopes_intensity(env_set)
#   normalized_aggregate_inte = [inte/max(aggregate_inte) for inte in aggregate_inte]
#   corr = pearsonr(theo_inte, normalized_aggregate_inte)[0]
#   return corr

def get_agg_env_corr(env_set):
  theo_inte = get_theo_envelope_peak_intens(env_set)
  aggregate_inte = env_utils.get_aggregate_envelopes_inte(env_set)
  max_aggregate_inte = max(aggregate_inte)
  normalized_aggregate_inte = []
  for inte in aggregate_inte:
    normalized_aggregate_inte.append(inte/max_aggregate_inte)
  corr = pearsonr(theo_inte, normalized_aggregate_inte)[0]
  return corr

def count_max_consecutive_peak_num(peaks):
  n = 0
  max_consecutive_peak_num = 0
  for peak in peaks:
    if peak is not None:
      n = n + 1
      if (n > max_consecutive_peak_num):
        max_consecutive_peak_num = n
    else:
      n = 0
  return max_consecutive_peak_num

# def get_consecutive_peaks_percent(env_coll):
#   selected_envelope_set = [env_set for env_set in env_coll.env_set_list if env_set.seed_env.charge == env_coll.seed_env.charge]
#   env_set = selected_envelope_set[0]
#   total_peaks = 0
#   positive_peaks = 0
#   for exp_env in env_set.exp_env_list:
#     total_peaks = total_peaks + sum([1 for i in exp_env.peak_list if i is not None])
#     positive_peaks = positive_peaks + _count_max_consecutive_peak_num(exp_env)
#   percent_matched_peaks = positive_peaks/total_peaks
#   return percent_matched_peaks

def get_consecutive_peaks_percent(env_set):
  total_peaks = 0
  positive_peaks = 0
  exp_envs = env_set.exp_env_list
  for exp_env in exp_envs:
    peaks = exp_env.peak_list
    for p in peaks:
      if p is not None:
        total_peaks = total_peaks + 1
    positive_peaks  = positive_peaks + count_max_consecutive_peak_num(peaks)
  percent_matched_peaks = positive_peaks/total_peaks
  return percent_matched_peaks

# def get_matched_peaks_percent(env_coll):
#   selected_envelope_set = [env_set for env_set in env_coll.env_set_list if env_set.seed_env.charge == env_coll.seed_env.charge]
#   env_set = selected_envelope_set[0]
#   total_peaks = 0
#   positive_peaks = 0
#   for exp_env in env_set.exp_env_list:
#     if sum([1 for i in exp_env.peak_list if i is not None]) <= 2:
#       continue
#     total_peaks = total_peaks + len(exp_env.peak_list)
#     positive_peaks = positive_peaks + sum([1 for i in exp_env.peak_list if i is not None])
#   if total_peaks == 0:
#     percent_matched_peaks = -1
#   else:
#     percent_matched_peaks = positive_peaks/total_peaks
#   return percent_matched_peaks

def get_matched_peaks_percent(env_set, theo_map):
  total_peaks = 0
  positive_peaks = 0
  exp_envs = env_set.exp_env_list
  num_exp_envs = len(exp_envs)
  for i in range(0, num_exp_envs):
    peaks = exp_envs[i].peak_list
    scalled_theo_env = theo_map[i]
    num_peaks = len(scalled_theo_env)
    for peak_id in range(0, num_peaks):
      peak_inte = scalled_theo_env[peak_id]
      if (peak_inte > 0):
        total_peaks = total_peaks + 1
        if peaks[peak_id] is not None:
          positive_peaks = positive_peaks + 1
  percent_matched_peaks = -1
  if (total_peaks > 0):
    percent_matched_peaks = positive_peaks/total_peaks
  return percent_matched_peaks

# def get_3_scan_corr(env_coll):
#   selected_envelope_set = [env_set for env_set in env_coll.env_set_list if env_set.seed_env.charge == env_coll.seed_env.charge]
#   env_set = selected_envelope_set[0]
#   shortlisted_spec = [exp_env for exp_env in env_set.exp_env_list if  env_set.seed_env.spec_id - 1 <= exp_env.spec_id <=  env_set.seed_env.spec_id + 1]  
#   if len(shortlisted_spec) <= 1:
#     scan_3_corr = 0
#   if len(shortlisted_spec) == 2:
#     exp_peaks_base_spec_1 = [peak.inte if peak is not None else 0 for peak in shortlisted_spec[0].peak_list]
#     exp_peaks_base_spec_2 = [peak.inte if peak is not None else 0 for peak in shortlisted_spec[1].peak_list]
#     scan_3_corr = pearsonr(exp_peaks_base_spec_1, exp_peaks_base_spec_2)[0]
#   if len(shortlisted_spec) == 3:
#     exp_peaks_base_spec_1 = [peak.inte if peak is not None else 0 for peak in shortlisted_spec[0].peak_list]
#     exp_peaks_base_spec_2 = [peak.inte if peak is not None else 0 for peak in shortlisted_spec[1].peak_list]
#     exp_peaks_base_spec_3 = [peak.inte if peak is not None else 0 for peak in shortlisted_spec[2].peak_list]
#     corr_sp_12 = pearsonr(exp_peaks_base_spec_1, exp_peaks_base_spec_2)[0]
#     corr_sp_13 = pearsonr(exp_peaks_base_spec_1, exp_peaks_base_spec_3)[0]
#     corr_sp_23 = pearsonr(exp_peaks_base_spec_2, exp_peaks_base_spec_3)[0]
#     scan_3_corr = sum([corr_sp_12, corr_sp_13, corr_sp_23])/3
#   return scan_3_corr

def get_3_scan_corr(env_set, base_spec, start_spec):
  scan_3_corr = 0
  exp_envs = env_set.exp_env_list
  base_spec = max(base_spec - start_spec, 0)

  data_sp = exp_envs[base_spec].get_inte_list()
  data_sp_minus_1 = [0.0] * len(data_sp)
  data_sp_plus_1 = [0.0] * len(data_sp)

  if (base_spec - 1 > 0):
    data_sp_minus_1 = exp_envs[base_spec-1].get_inte_list()
  if (base_spec + 1 < len(exp_envs)):
    data_sp_plus_1 = exp_envs[base_spec+1].get_inte_list()

  sp_sum = sum(data_sp)
  sp_minus_1_sum = sum(data_sp_minus_1)
  sp_plus_1_sum = sum(data_sp_plus_1)

  if (sp_sum > 0 and sp_minus_1_sum > 0 and sp_plus_1_sum > 0):
    corr_sp_12 = pearsonr(data_sp, data_sp_minus_1)[0]
    corr_sp_13 = pearsonr(data_sp, data_sp_plus_1)[0]
    corr_sp_23 = pearsonr(data_sp_minus_1, data_sp_plus_1)[0]
    scan_3_corr = (corr_sp_12 + corr_sp_13 + corr_sp_23)/3.0
  elif (sp_sum > 0 and sp_minus_1_sum > 0 and sp_plus_1_sum == 0):
    scan_3_corr = pearsonr(data_sp, data_sp_minus_1)[0]
  elif (sp_sum > 0 and sp_minus_1_sum == 0 and sp_plus_1_sum > 0):
    scan_3_corr = pearsonr(data_sp, data_sp_plus_1)[0]
  elif (sp_sum == 0 and sp_minus_1_sum > 0 and sp_plus_1_sum > 0):
    scan_3_corr = pearsonr(data_sp_minus_1, data_sp_plus_1)[0]
  else:
    scan_3_corr = 0
  return scan_3_corr

def get_rt_range(env_coll):
  return env_coll.get_max_elution_time() - env_coll.get_min_elution_time()

def get_charge_range(env_coll):
  return env_coll.max_charge - env_coll.min_charge
  
# def _count_max_consecutive_peak_num(exp_env):
#   n = 0
#   max_consecutive_peak_num = 0
#   for peak in exp_env.peak_list:
#     if peak is not None:
#       n = n + 1
#       if (n > max_consecutive_peak_num):
#         max_consecutive_peak_num = n
#     else:
#       n = 0
#   return max_consecutive_peak_num

