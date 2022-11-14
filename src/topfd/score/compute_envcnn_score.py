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
import numpy as np

import topfd.envelope.env_util as env_util

def get_envcnn_score(model, peak_matrix, env_coll, noiseIntensityLevel):
  envcnn_data_matrix = _get_data_matrix_EnvCNN_aggregate_sum(peak_matrix, env_coll, noiseIntensityLevel)
  envcnn_data_matrix = np.expand_dims(envcnn_data_matrix, axis=0)
  envcnn_score = model.predict(envcnn_data_matrix, verbose=0)[0][0]
  return envcnn_score

def _get_data_matrix_EnvCNN_aggregate_sum(peak_matrix, env_coll, noiseIntensityLevel, bin_size = 0.01, mass_tole = 0.02):
  selected_envelope_set = [env_set for env_set in env_coll.env_set_list if env_set.seed_env.charge == env_coll.seed_env.charge]
  env_set = selected_envelope_set[0]
  theo_mz = [i.pos for i in env_set.seed_env.peak_list]
  theo_inte = [i.inte for i in env_set.seed_env.peak_list]

  envcnn_data_matrix = np.zeros(shape=(300, 5))  
  exp_distribution = env_util.get_aggregate_envelopes_mz(env_set)
  exp_inte_distribution = env_util.get_aggregate_envelopes_intensity(env_set)
  inteRatio = env_util.calcInteRatio_scan(theo_inte, exp_inte_distribution)
  scaled_theo_inte = [peak.inte * inteRatio for peak in env_set.seed_env.peak_list]
  normalize_theo_inte = [peak_intensity/max(scaled_theo_inte) for peak_intensity in scaled_theo_inte]
  normalize_epx_inte = [peak_intensity/max(scaled_theo_inte) for peak_intensity in exp_inte_distribution]
  for idx in range(0, len(env_set.seed_env.peak_list)):
    exp_inte = normalize_epx_inte[idx]
    if exp_inte == 0: continue
    mass_diff = abs(theo_mz[idx] - exp_distribution[idx])
    if mass_diff < mass_tole:
      mass_diff_score = (mass_tole - mass_diff)/mass_tole
    else:
      mass_diff_score = 0
    p_idx = _get_index(round(theo_mz[idx], 3), theo_mz[0], bin_size) + 10
    if p_idx >= 300: break
    envcnn_data_matrix[p_idx, 0] = normalize_theo_inte[idx]
    envcnn_data_matrix[p_idx, 1] = exp_inte
    envcnn_data_matrix[p_idx, 2] = mass_diff_score
    envcnn_data_matrix[p_idx, 3] = normalize_theo_inte[idx] - exp_inte
    envcnn_data_matrix[p_idx, 4] = math.log10(max(scaled_theo_inte)/noiseIntensityLevel)

  ######################## Add noise peaks in EnvCNN matrix
  noise_arr = np.zeros(shape=300)
  noise_distribution_list = []
  noise_inte_distribution_list = []
  for spec_id in range(env_coll.start_spec_id, env_coll.end_spec_id+1):
    intv_peak_list = _get_intv_peak_list(peak_matrix, env_set, spec_id)
    noise_distribution_list.append([elem.pos for elem in intv_peak_list])
    noise_inte_distribution_list.append([elem.inte for elem in intv_peak_list])
  for idx in range(0, len(noise_distribution_list)):
    for j_idx in range(0, len(noise_distribution_list[idx])):
      p_idx = _get_index(round(noise_distribution_list[idx][j_idx], 3), theo_mz[0], bin_size) + 10
      if p_idx >= 300: break      
      ## check if peak has been used as the data peak.
      peak_condition = False
      for i in range(0, 3):
        if p_idx + i < 300 and p_idx - i > -1 and envcnn_data_matrix[p_idx][0] == 0: 
          if envcnn_data_matrix[p_idx - i][0] == 0 and envcnn_data_matrix[p_idx + i][0] == 0:
            peak_condition = True
          else:
            peak_condition = False
            break
      if peak_condition == True:
        noise_arr[p_idx] = noise_arr[p_idx] + (noise_inte_distribution_list[idx][j_idx]/max(scaled_theo_inte))
  envcnn_data_matrix[:, 1] = np.add(envcnn_data_matrix[:, 1], noise_arr)
  return envcnn_data_matrix

def _get_index(mz, min_mz, bin_size):
  mz_diff = mz - min_mz
  bin_idx = int(mz_diff /bin_size)
  return bin_idx

def _get_intv_peak_list(peak_matrix, env_set, spec_id):
  min_theo_peak = round(env_set.seed_env.peak_list[0].pos, 3)
  start_idx = peak_matrix.get_index(min_theo_peak - 0.1)
  max_theo_peak = round(env_set.seed_env.peak_list[-1].pos, 3)
  end_idx = peak_matrix.get_index(max_theo_peak + 0.1)
  spec_peaks = peak_matrix.matrix[spec_id]
  intv_peak_list = []
  for peak_idx in range(start_idx, end_idx + 1):
    for peak in spec_peaks.row[peak_idx]:
      if peak.pos >= (min_theo_peak - 0.1) and peak.pos <= (max_theo_peak + 0.1):
        intv_peak_list.append(peak)
  return intv_peak_list
