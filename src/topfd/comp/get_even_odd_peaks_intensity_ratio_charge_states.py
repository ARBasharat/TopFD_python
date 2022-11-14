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

import sys
# sys.path.insert(0, r"C:\Users\Abdul\Documents\GitHub\MS_Feature_Extraction_xwliu\src")
import math
from matplotlib import pyplot as plt

import topfd.plots.generate_feature_plots as gen_plots
import topfd.util.file_util as util

def get_envelope_peaks(env_coll):
  return [(round(i.pos, 4), round(i.inte, 4)) for i in env_coll.seed_env.peak_list]

def get_rt_range(env_coll):
  return (env_coll.get_min_elution_time(), env_coll.get_max_elution_time())

def get_envelope_peak_masses(env_coll):
  return [round(i.pos, 4) for i in env_coll.seed_env.peak_list]

def get_charge_range(env_coll):
  return (env_coll.min_charge, env_coll.max_charge)
  
def get_agg_odd_even_peak_ratio_base_spec(env_coll, coll_idx, mass_tole = 0.01):
  selected_env_set = [es for es in env_coll.env_set_list if es.seed_env.spec_id == env_coll.seed_env.spec_id]
  env_set = selected_env_set[0]
  aggregate_inte = [0] * len(env_set.seed_env.peak_list)
  for spId in range(len(env_set.exp_env_list)):
    for peakId in range(0, len(aggregate_inte)):
      peak = env_set.exp_env_list[spId].peak_list[peakId] 
      if peak is not None:
        aggregate_inte[peakId] = aggregate_inte[peakId] + peak.inte
        
  sum_even_peaks = 0
  sum_odd_peaks = 0
  for peak_idx in range(0, len(aggregate_inte)):
    # print(peak_idx, peak_idx%2, aggregate_inte[peak_idx])
    if peak_idx%2 == 0:
      sum_even_peaks = sum_even_peaks + aggregate_inte[peak_idx]
    else:
      sum_odd_peaks = sum_odd_peaks + aggregate_inte[peak_idx]
  inte_ratio = math.log10(sum_even_peaks/sum_odd_peaks)
  print("Inte Ratio:", coll_idx, sum_even_peaks/sum_odd_peaks, inte_ratio)
  return [abs(inte_ratio)]

def get_aggregate_odd_even_peak_intensity_ratio(env_coll, coll_idx, mass_tole = 0.01):
  inte_ratios = []
  for i in range(len(env_coll.env_set_list)):
    env_set = env_coll.env_set_list[i]
    aggregate_inte = [0] * len(env_set.seed_env.peak_list)
    for spId in range(len(env_set.exp_env_list)):
      for peakId in range(0, len(aggregate_inte)):
        peak = env_set.exp_env_list[spId].peak_list[peakId] 
        if peak is not None:
          aggregate_inte[peakId] = aggregate_inte[peakId] + peak.inte
          
    sum_even_peaks = 0
    sum_odd_peaks = 0
    for peak_idx in range(0, len(aggregate_inte)):
      # print(peak_idx, peak_idx%2, aggregate_inte[peak_idx])
      if peak_idx%2 == 0:
        sum_even_peaks = sum_even_peaks + aggregate_inte[peak_idx]
      else:
        sum_odd_peaks = sum_odd_peaks + aggregate_inte[peak_idx]
    inte_ratio = math.log10(sum_even_peaks/sum_odd_peaks)
    print("Inte Ratio:", inte_ratio)
    inte_ratios.append(abs(inte_ratio))
  return inte_ratios

def get_exp_envelope_odd_even_peak_intensity_ratio(env_coll, coll_idx, mass_tole = 0.01):
  inte_ratios = []
  for i in range(len(env_coll.env_set_list)):
    env_set = env_coll.env_set_list[i]
    experimental_env_intens = [round(p.inte, 4) if p is not None else 0 for p in env_set.exp_env_list.peak_list]
         
    sum_even_peaks = 0
    sum_odd_peaks = 0
    for peak_idx in range(0, len(experimental_env_intens)):
      # print(peak_idx, peak_idx%2, experimental_env_intens[peak_idx])
      if peak_idx%2 == 0:
        sum_even_peaks = sum_even_peaks + experimental_env_intens[peak_idx]
      else:
        sum_odd_peaks = sum_odd_peaks + experimental_env_intens[peak_idx]
    inte_ratio = math.log10(sum_even_peaks/sum_odd_peaks)
    print("Inte Ratio:", coll_idx, sum_even_peaks/sum_odd_peaks, inte_ratio)
    inte_ratios.append(inte_ratio)
  return inte_ratios
  
in_fname = sys.argv[1]
# in_fname = r"C:\Users\Abdul\Documents\GitHub\test_data_xwliu\Rep_1\out_v1.pkl"

## Load pickle file
env_coll_list = util.load_pickle_file_data(in_fname)

wrong_charge_state_features_rep_1 = [215, 361, 438, 882, 3171, 1129, 1415, 1442, 1459, 1493, 1766, 1790, 1836, 1865, 1901, 2203, 3744, 4546, 7030]
inte_ratio_positive = []
inte_ratio_negative = []
for i in range(0, len(env_coll_list)):
  if i in range(0, 100):
    print("\n\nPositive Envelope: ", i)
    env_coll = env_coll_list[i]
    inte_ratio_positive.extend(get_agg_odd_even_peak_ratio_base_spec(env_coll, i))
    # gen_plots.plot_envelope_sets_2d(env_coll, i)
    # gen_plots.plot_aggregate_envelopes(env_coll, i)
  if i in wrong_charge_state_features_rep_1:
    print("\n\nNegative Feature ID:", i)
    env_coll = env_coll_list[i]
    inte_ratio_negative.extend(get_aggregate_odd_even_peak_intensity_ratio(env_coll, i))
    # gen_plots.plot_envelope_sets_2d(env_coll, i)
    # gen_plots.plot_aggregate_envelopes(env_coll, i)
    
plt.Figure()  
plt.hist(inte_ratio_positive, color = 'blue', bins = 20)
plt.hist(inte_ratio_negative, color = 'red', bins = 20)
plt.legend(['+ve Features', '-ve Features'])
plt.show()
plt.close()
