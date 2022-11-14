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

import os
import statistics

from topfd.env_set.xic import XIC
import topfd.score.env_util as env_utils
import topfd.util.utility_functions as utility_functions

from topfd.env_set.env_set_plot import plot_3d, plot_xic

class EnvSet:
  def __init__(self, seed_env, exp_env_list, start_spec_id, end_spec_id): 
    self.__seed_env = seed_env
    self.__exp_env_list = exp_env_list
    self.__start_spec_id = start_spec_id
    self.__end_spec_id = end_spec_id
    self.__xic = self.init_median_xic()    
  
  @property
  def seed_env(self):
    return self.__seed_env

  @property
  def exp_env_list(self):
    return self.__exp_env_list
  
  @property
  def start_spec_id(self):
    return self.__start_spec_id
  
  @property
  def end_spec_id(self):
    return self.__end_spec_id
  
  @property
  def xic(self):
    return self.__xic

  def get_start_spec_id(self):
    return self.__exp_env_list[0].spec_id

  def get_end_spec_id(self):
    return self.__exp_env_list[len(self.__exp_env_list)-1].spec_id
  
  def setSpecId(self, startSpecId, endSpecId):
    self.__start_spec_id = startSpecId 
    self.__end_spec_id = endSpecId

  def init_median_xic(self):
    theo_envelope_inte = self.seed_env.get_inte_list()
    refer_idx = theo_envelope_inte.index(max(theo_envelope_inte))
    inte_list = []
    for exp_env in self.exp_env_list:
      if exp_env.get_match_peak_num(refer_idx) < 2:
        inte_list.append(0)
        continue
      exp_envelope_inte = exp_env.get_inte_list()
      ratio = env_utils.calcInteRatio_scan(theo_envelope_inte, exp_envelope_inte)
      theoretical_peak_sum = 0
      theoretical_peak_sum = theoretical_peak_sum + (theo_envelope_inte[refer_idx] * ratio)
      if refer_idx - 1 >= 0:
        theoretical_peak_sum = theoretical_peak_sum + (theo_envelope_inte[refer_idx-1] * ratio)
      if refer_idx + 1 < len(theo_envelope_inte):
        theoretical_peak_sum = theoretical_peak_sum + (theo_envelope_inte[refer_idx+1] * ratio)
      inte_list.append(theoretical_peak_sum)
    xic = XIC(self.start_spec_id, self.seed_env.spec_id, inte_list)
    return xic

  def get_coordinates(self):
    x = []
    y = []
    z = []
    for env in self.__exp_env_list:
      for peak in env.peak_list:
        if peak is not None:
          x.append(peak.pos)
          y.append(env.rt)
          z.append(peak.inte)
    return (x,y,z)

  def plot(self):
    x, y, z = self.get_coordinates()
    if (len(x) > 0):
      plot_3d(x, y, z)

  def get_median_ratio(self, env):
    exp_peak_list = env.peak_list
    theo_peak_list = self.__seed_env.peak_list
    #print("exp len", len(exp_peak_list), "theo_len", len(theo_peak_list))
    ratio_list = []
    for i in range(len(theo_peak_list)):
      ratio = 0
      if exp_peak_list[i] is not None:
        ratio = exp_peak_list[i].inte / theo_peak_list[i].inte
        ratio_list.append(ratio)
    ## used in get_median_XIC for handling the empty experimental envelopes
    if sum(ratio_list) == 0:
      return 0
    return statistics.median(ratio_list)

  def get_median_xic(self):
    inte_list = []
    for env in self.__exp_env_list:
      ratio = self.get_median_ratio(env)
      inte_list.append(ratio)
    start_spec_id = self.get_start_spec_id()
    base_spec_id = self.__seed_env.spec_id
    xic = XIC(start_spec_id, base_spec_id, inte_list)
    return xic

  def get_seed_inte_ratio(self):
    idx = self.__seed_env.spec_id - self.get_start_spec_id()
    ratio = self.get_median_ratio(self.__exp_env_list[idx])
    return ratio

  def remove_non_consecutive_peaks(self, i, max_miss_peak):
    # search backward
    idx = self.__seed_env.spec_id - self.get_start_spec_id() 
    miss_num = 0
    while idx >= 0:
      if self.__exp_env_list[idx].peak_list[i] is None:
        miss_num = miss_num + 1
      else:
        miss_num = 0
      if miss_num >= max_miss_peak:
        break
      idx = idx - 1
    while idx >= 0:
      self.__exp_env_list[idx].peak_list[i] = None
      idx = idx - 1

    # search forward
    idx = self.__seed_env.spec_id - self.get_start_spec_id()
    miss_num = 0
    while idx < len(self.__exp_env_list):
      if self.__exp_env_list[idx].peak_list[i] is None:
        miss_num = miss_num + 1
      else:
        miss_num = 0
      if miss_num >= max_miss_peak:
        break
      idx = idx + 1
    while idx < len(self.__exp_env_list):
      self.__exp_env_list[idx].peak_list[i] = None
      idx = idx + 1
      
  def remove_all_non_consecutive_peaks(self, max_miss_peak):
    for i in range(self.__seed_env.get_peak_num()):
      self.remove_non_consecutive_peaks(i, max_miss_peak)

  def remove_matrix_peaks(self, peak_matrix):
    for env in self.__exp_env_list:
      for peak in env.peak_list:
        if peak is not None:
          peak_matrix.remove_peak(peak)

  # def comp_intensity(self):
  #   scalled_intensity = 0
  #   for exp_env in self.__exp_env_list:
  #     if exp_env is not None:
  #       scale_inte = self.get_median_ratio(exp_env)
  #       scalled_envelope_intensity = [i.inte * scale_inte for i in self.__seed_env.peak_list]
  #       scalled_intensity = scalled_intensity  + sum(scalled_envelope_intensity)
  #   return scalled_intensity
  
  def comp_intensity(self, snr, noise_inte):
    _map = self.get_map(snr, noise_inte)
    aggregate_inte = [0] * len(_map[0])
    num_peaks = len(aggregate_inte)
    for sp_map in _map:
      for peakIdx in range(0, num_peaks):
        aggregate_inte[peakIdx] = aggregate_inte[peakIdx] + sp_map[peakIdx]
    abundance = sum(aggregate_inte)
    return abundance
  
  def get_refine_mono_mass(self, mass_tole = 0.01):
    aggregate_mz = [0] * len(self.seed_env.peak_list)
    aggregate_count = [0] * len(self.seed_env.peak_list)
    for spId in range(len(self.exp_env_list)):
      for peakIdx in range(0, len(aggregate_mz)):
        peak = self.exp_env_list[spId].peak_list[peakIdx] 
        if peak is not None:
          aggregate_mz[peakIdx] = aggregate_mz[peakIdx] + peak.pos
          aggregate_count[peakIdx] = aggregate_count[peakIdx] + 1
          
    aggregate_envelope_mz = [aggregate_mz[i]/aggregate_count[i] if aggregate_mz[i] > 0 else 0 for i in range(0, len(aggregate_mz))]
    mz_diff = sum([aggregate_envelope_mz[i] - self.seed_env.peak_list[i].pos if aggregate_envelope_mz[i] > 0 else 0 for i in range(0, len(aggregate_mz))])
    if abs(mz_diff) > mass_tole:
      peaks_to_shift = sum([1 for i in aggregate_count if i > 0])
      shift = mz_diff/peaks_to_shift
      # new_envelope = [self.seed_env.peak_list[i].pos+shift for i in range(0, len(self.seed_env.peak_list))]
      mz = (self.seed_env.mass + (self.seed_env.charge * self.seed_env.get_proton_mass())) / self.seed_env.charge
      refined_mass = ((mz+shift) * self.seed_env.charge) - (self.seed_env.charge * self.seed_env.get_proton_mass())
      # print("Refined Mono Mass: " + str(refined_mass))
      # print("New Seed Envelope: " + str(new_envelope))
      # print("Seed Envelope: " + str([theo_env[i].pos for i in range(0, len(theo_env))]))
      return refined_mass
    else:
      return self.seed_env.mass
  
  def get_left_max(self, pos, y):
    max_val = -100000000
    for i in range(0, pos):
      if (y[i] > max_val):
        max_val = y[i]
    return max_val
  
  def get_right_max(self, pos, y):
    max_val = -100000000
    vec_length = len(y)
    for i in range(pos + 1, vec_length):
      if (y[i] > max_val):
        max_val = y[i]
    return max_val

  def shortlistExpEnvs(self):
    inte_list = self.xic.inte_list
    smoothed_inte_list = self.xic.smoothed_inte_list
    
    num_exp_env = len(self.exp_env_list)
    shortlisted_inte_list = []
    shortlisted_smoothed_inte_list = []
    tmp = []
    for i in range(0, num_exp_env):
      if (self.exp_env_list[i].spec_id >= self.start_spec_id and self.exp_env_list[i].spec_id <= self.end_spec_id):
        tmp.append(self.exp_env_list[i])
        shortlisted_inte_list.append(inte_list[i])
        shortlisted_smoothed_inte_list.append(smoothed_inte_list[i])
    self.__exp_env_list = tmp
    self.__xic = XIC(self.exp_env_list[0].spec_id, self.seed_env.spec_id, shortlisted_inte_list, shortlisted_smoothed_inte_list)
  
  def refine_feature_boundary(self):
    split_feature_intensity_ratio = 0.4
    base_spec = self.seed_env.spec_id - self.start_spec_id
    smoothed_env_xic = self.xic.smoothed_inte_list
    ## Left side
    left_data = smoothed_env_xic[0:base_spec+1]
    minima_left = utility_functions.findLocalMinima(left_data)
    minima_vals_left = []
    for m in minima_left:
      minima_vals_left.append(left_data[m])
    start_split_point = self.start_spec_id
    while (len(minima_vals_left) > 0):
      idx = minima_vals_left.index(min(minima_vals_left))
      pos = minima_left[idx]
      minima_vals_left.pop(idx)
      leftMax = self.get_left_max(pos, left_data)
      if (leftMax == 0): continue
      if (left_data[pos] / leftMax <= split_feature_intensity_ratio):
        start_split_point = start_split_point + pos
        temp_left_data = left_data[pos:len(left_data)+1]
        left_data = temp_left_data
        minima_left = utility_functions.findLocalMinima(left_data)
        minima_vals_left.clear()
        for m in minima_left:
          minima_vals_left.append(left_data[m])
      
    ## Right side
    right_data = smoothed_env_xic[base_spec:len(smoothed_env_xic)+1]
    minima_right = utility_functions.findLocalMinima(right_data)
    minima_vals_right = []
    for m in minima_right:
      minima_vals_right.append(right_data[m])
    end_split_point = -1
    while (len(minima_vals_right) > 0):
      idx = minima_vals_right.index(max(minima_vals_right))
      pos = minima_right[idx]
      minima_vals_right.pop(idx)
      rightMax = self.get_right_max(pos, right_data)
      if (rightMax == 0): continue
      if (right_data[pos] / rightMax <= split_feature_intensity_ratio):
        end_split_point = pos
        temp_right_data = right_data[0:pos]
        right_data = temp_right_data
        minima_right = utility_functions.findLocalMinima(right_data);
        minima_vals_right.clear()
        for m in minima_right:
          minima_vals_right.append(right_data[m])
      
    start = self.start_spec_id
    if (start_split_point > -1):
      start = start_split_point
    end = self.end_spec_id
    if (end_split_point > -1):
      end = self.seed_env.spec_id + end_split_point
  
    self.__start_spec_id = start
    self.__end_spec_id = end
    self.shortlistExpEnvs()

  def get_weight_mz_error(self):
    seed_peak_list = self.seed_env.peak_list
    inte_list = self.xic.inte_list
    num_exp_env = len(self.exp_env_list)
    num_peaks_theo_env = len(seed_peak_list)
    weight_sum = 0
    error_sum = 0
    for exp_env_id in range(0, num_exp_env):
      expEnvelope = self.exp_env_list[exp_env_id]
      if expEnvelope is None:
        continue
      exp_peak_list = expEnvelope.peak_list
      for peak_idx in range(0, num_peaks_theo_env):
        peak = exp_peak_list[peak_idx]
        if peak is not None:
          cur_inte = seed_peak_list[peak_idx].inte * inte_list[exp_env_id]
          cur_err = peak.pos - seed_peak_list[peak_idx].pos
          error_sum = error_sum + (cur_inte * cur_err)
          weight_sum = weight_sum + cur_inte
    return weight_sum, error_sum
          
  def get_map(self, snr, noise_inte):
    _map = []
    for exp_env in self.exp_env_list:
      exp_peaks = exp_env.get_inte_list()
      theo_peaks = self.seed_env.get_inte_list()
      inte_ratio = env_utils.calcInteRatio_scan(theo_peaks, exp_peaks)
      scalled_theo_env = []
      for theo_peak in theo_peaks: 
        scaled_inte = theo_peak * inte_ratio;
        if (scaled_inte > snr * noise_inte):
          scalled_theo_env.append(scaled_inte)
        else:
          scalled_theo_env.append(0)
      _map.append(scalled_theo_env)
    return _map

  def remove_peak_data(self, peak_matrix, snr):
    _map = self.get_map(snr, peak_matrix.min_inte)
    num_exp_env = len(self.exp_env_list)
    for env_id in range(0, num_exp_env):
      exp_env = self.exp_env_list[env_id]
      spec_id = exp_env.spec_id
      if spec_id < 0 or spec_id >= peak_matrix.spec_num:
        continue
      exp_data = exp_env.peak_list
      theo_data = _map[env_id]
      num_peaks_exp_env = len(exp_data)
      for peak_id in range(0, num_peaks_exp_env):
        exp_peak = exp_data[peak_id]
        if exp_peak is None:
          continue
        bin_idx = peak_matrix.get_index(exp_peak.pos)
        peaks = peak_matrix.matrix[spec_id].row[bin_idx]
        theo_peak = theo_data[peak_id]
        other_peaks = []
        for peak in peaks:
          if abs(peak.inte - exp_peak.inte) < 0.0001:
            if peak.inte / theo_peak < 4:
              continue
            else:
              if peak.inte - theo_peak > 0:
                peak.inte.set_inte(peak.inte - theo_peak)
              else:
                peak.set_inte(0)
          other_peaks.append(peak)
        peak_matrix.matrix[spec_id].row[bin_idx] = other_peaks
