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
import copy as copy

import topfd.score.env_util as env_utils
from topfd.env_set.exp_envelope import ExpEnvelope
from topfd.env_set.env_set import EnvSet
from topfd.env_set.env_set_plot import plot_3d, plot_xic

# def pick_exp_peak(row, seed_peak, mass_tol):
#   ## get peaks within mass tolerance
#   result_peak = None 
#   max_inte = -math.inf
#   pos = seed_peak.pos
#   for idx in range(seed_peak.start_idx, seed_peak.end_idx+1):
#     for matrix_peak in row[idx]:
#       if abs(pos - matrix_peak.pos) < mass_tol and matrix_peak.inte > max_inte:
#         result_peak = matrix_peak
#         max_inte = matrix_peak.inte
#   return result_peak

def pick_exp_peak(peak_matrix, seed_peak, sp_id, mass_tole):
  result_peak = None
  max_inte = -1000000
  for idx in range(seed_peak.start_idx, seed_peak.end_idx+1):
    bin_peaks = peak_matrix.matrix[sp_id].getRowPeak(idx)
    for matrix_peak in bin_peaks:
      mass_diff = abs(seed_peak.pos - matrix_peak.pos)
      if mass_diff < mass_tole and matrix_peak.inte > max_inte:
        result_peak = matrix_peak
        max_inte = matrix_peak.inte
  return result_peak

# def get_match_exp_env(peak_row, seed_env, mass_tol):
#   peak_list = []
#   for seed_peak in seed_env.peak_list: 
#     peak = pick_exp_peak(peak_row.row, seed_peak, mass_tol)
#     peak_list.append(peak)
#   exp_env = ExpEnvelope(peak_row.spec_id, peak_row.rt, peak_list)
#   return exp_env

def get_match_exp_env(peak_matrix, env, sp_id, mass_tole):
  peak_list = []
  for seed_peak in env.peak_list:
    if (seed_peak.start_idx > -1 and seed_peak.end_idx > -1):
      peak = pick_exp_peak(peak_matrix, seed_peak, sp_id, mass_tole)
      peak_list.append(peak)
    else:
      peak_list.append(None)
  exp_env = ExpEnvelope(sp_id, peak_list)
  return exp_env

# def comp_peak_start_end_idx(peak_matrix, peak_list, error_tole):
#   for peak in peak_list:
#     mz = peak.pos
#     start_idx = peak_matrix.get_index(mz-error_tole)
#     if start_idx < 0:
#       start_idx = 0
#     end_idx = peak_matrix.get_index(mz+error_tole)
#     if end_idx >= peak_matrix.bin_num:
#       end_idx = peak_matrix.bin_num -1
#     peak.set_start_idx(start_idx)
#     peak.set_end_idx(end_idx)
#     #print("start idx", start_idx, "end idx", end_idx)

def comp_peak_start_end_idx(peak_matrix, env, error_tole):
  peak_list = env.peak_list
  for peak in peak_list:
    mz = peak.pos
    start_idx = peak_matrix.get_index(mz - error_tole)
    if (start_idx < 0): start_idx = 0
    end_idx = peak_matrix.get_index(mz + error_tole)
    if (end_idx >= peak_matrix.bin_num): end_idx = peak_matrix.bin_num - 1
    peak.set_start_idx(start_idx)
    peak.set_end_idx(end_idx)
  env.peak_list = peak_list

def print_env(exp_env, ratio):
  print(exp_env.spec_id, end = " ")
  peak_list = exp_env.peak_list
  for p in peak_list:
    if p is not None:
      print(p.pos, p.inte * ratio, end = " ")
    else:
      print("NONE","NONE", end = " ")
  print("")

def print_env_list(env_list):
  for env in env_list:
    print_env(env, 1)

def preprocess_env(peak_matrix, seed_env, mass_tol):
  env = copy.deepcopy(seed_env)
  min_mz = peak_matrix.min_mz - mass_tol
  max_mz = peak_matrix.max_mz + mass_tol
  env.rm_peaks(min_mz, max_mz)
  # if peak number is low, stop
  valid = True
  if (env.get_peak_num() <= 2):
    valid = False
  if (env.spec_id >= peak_matrix.spec_num):
    print("spec id ", seed_env.spec_id, "is out of range!")
    valid = False
  return [env,valid]

# # check if an envelope set exists or not
# def check_valid_env_set(peak_matrix, seed_env, mass_tol, mactch_peak_num_tole = 3):
#   [env, valid] = preprocess_env(peak_matrix, seed_env, mass_tol)
#   if not valid:
#     return False
#   env.keep_top_three()
#   comp_peak_start_end_idx(peak_matrix, env.peak_list, mass_tol)
#   base_idx = env.spec_id
#   start_idx = max(base_idx-1, 0)
#   end_idx = min(base_idx+1, peak_matrix.spec_num -1)
#   valid = True
  
#   env_list = []
#   for idx in range(start_idx, end_idx + 1):
#     exp_env = get_match_exp_env(peak_matrix.matrix[idx], env, mass_tol)
#     env_list.append(exp_env)
#     ## While checking validity of charge states; we reduce the mactch_peak_num_tole to 2.
#     if exp_env.get_match_peak_num() < mactch_peak_num_tole:
#       valid = False
#   #plot
#   #print("charge", seed_env.charge)
#   env_set = EnvSet(seed_env, env_list)
#   #x, y, z = env_set.get_coordinates()
#   #if (len(x) > 0):
#   #  plot_3d(x, y, z)
#   return valid 

def get_env_set_by_three_peaks(peak_matrix, seed_env, mass_tol, max_miss_env):
  [env, valid] = preprocess_env(peak_matrix, seed_env, mass_tol)
  if not valid:
    return None
  env.keep_top_three()
  comp_peak_start_end_idx(peak_matrix, env.peak_list, mass_tol)
  # search backward
  back_env_list = []
  idx = env.spec_id
  miss_num = 0
  while idx >= 0:
    exp_env = get_match_exp_env(peak_matrix.matrix[idx], env, mass_tol)
    back_env_list.append(exp_env)
    if exp_env.get_match_peak_num() < 2:
      miss_num = miss_num + 1
    else:
      miss_num = 0
    if miss_num >= max_miss_env:
      break
    idx = idx - 1
  remove_non_match_envs(back_env_list)
  #print("Print envelope list after removing")
  #print_env_list(back_env_list)
  # search forward
  forw_env_list = []
  idx = env.spec_id + 1
  miss_num = 0
  while idx < peak_matrix.spec_num:
    exp_env = get_match_exp_env(peak_matrix.matrix[idx], env, mass_tol)
    forw_env_list.append(exp_env)
    if exp_env.get_match_peak_num() < 2:
      miss_num = miss_num + 1
    else:
      miss_num = 0
    if miss_num >= max_miss_env:
      break
    idx = idx + 1
  remove_non_match_envs(forw_env_list)
  #print("Print envelope list after removing")
  #print_env_list(forw_env_list)

  # merge results
  back_env_list.reverse()
  #print_env_list(back_env_list)
  back_env_list = back_env_list + forw_env_list
  if (len(back_env_list) == 0):
    return None
  #print_env_list(back_env_list)
  env_set = EnvSet(env, back_env_list)
  #env_set.plot()
  return env_set
  

# def find_env_set(peak_matrix, seed_env, mass_tol, start_spec_id, end_spec_id):
#   [env, valid] = preprocess_env(peak_matrix, seed_env, mass_tol)
#   if not valid:
#     return None
#   comp_peak_start_end_idx(peak_matrix, env.peak_list, mass_tol)
#   exp_env_list = []
#   for idx in range(start_spec_id, end_spec_id + 1):
#     exp_env = get_match_exp_env(peak_matrix.matrix[idx], env, mass_tol)
#     exp_env_list.append(exp_env)

#   env_set = EnvSet(env, exp_env_list)
#   return env_set
def find_env_set(peak_matrix, env, mass_tole, start_spec_id, end_spec_id, snr):
    noise_inte_level = peak_matrix.min_inte
    theo_envelope_inte = env.get_inte_list()
    num_theo_env_peaks = len(theo_envelope_inte)
    refer_idx = theo_envelope_inte.index(max(theo_envelope_inte))
    base_idx = env.spec_id
    miss_num = 0
    max_miss_env = 2

    back_env_list = []
    for idx in range(base_idx, start_spec_id, -1):
      exp_env = get_match_exp_env(peak_matrix, env, idx, mass_tole)
      experimental_envelope_inte = exp_env.get_inte_list()
      inte_ratio = env_utils.calcInteRatio_scan(theo_envelope_inte, experimental_envelope_inte)
      for i in range(0, num_theo_env_peaks):
        peak_inte = theo_envelope_inte[i]
        if ((inte_ratio * peak_inte) < (noise_inte_level * snr)):
          exp_env.peak_list[i] = None
      back_env_list.append(exp_env)
      if (exp_env.get_match_peak_num(refer_idx) < 2):
        miss_num = miss_num + 1
      else:
        miss_num = 0
      if (miss_num >= max_miss_env): break
    remove_non_match_envs(back_env_list, refer_idx)

    forw_env_list = []
    for idx in range(base_idx + 1, end_spec_id):
      exp_env = get_match_exp_env(peak_matrix, env, idx, mass_tole)
      experimental_envelope_inte = exp_env.get_inte_list()
      inte_ratio = env_utils.calcInteRatio_scan(theo_envelope_inte, experimental_envelope_inte)
      for i in range(0, num_theo_env_peaks):
        peak_inte = theo_envelope_inte[i]
        if ((inte_ratio * peak_inte) < (noise_inte_level * snr)):
          exp_env.peak_list[i] = None
      forw_env_list.append(exp_env)
      if (exp_env.get_match_peak_num(refer_idx) < 2):
        miss_num = miss_num + 1
      else:
        miss_num = 0
      if (miss_num >= max_miss_env): break
    remove_non_match_envs(forw_env_list, refer_idx)
    
    back_env_list.reverse()
    back_env_list = back_env_list + forw_env_list
    if (len(back_env_list) == 0): return None
    start_spec_id = back_env_list[0].spec_id
    end_spec_id = back_env_list[-1].spec_id
    if ((end_spec_id - start_spec_id + 1) < 2): return None
    env_set = EnvSet(env, back_env_list, start_spec_id, end_spec_id)
    return env_set
   
def remove_non_match_envs(env_list, refer_idx):
  idx = len(env_list) -1 
  while (idx >= 0):
    env = env_list[idx]
    if (env.get_match_peak_num(refer_idx) < 2):
      env_list.pop()
    else: return
    idx = idx - 1
    
def get_env_set(peak_matrix, env, mass_tole, max_miss_env, snr):
  noise_inte_level = peak_matrix.min_inte
  theo_envelope_inte = env.get_inte_list()
  num_theo_env_peaks = len(theo_envelope_inte)
  refer_idx = theo_envelope_inte.index(max(theo_envelope_inte))

  ## search backward
  back_env_list = []
  idx = env.spec_id
  miss_num = 0
  while (idx >= 0):
    exp_env = get_match_exp_env(peak_matrix, env, idx, mass_tole)
    experimental_envelope_inte = exp_env.get_inte_list()
    inte_ratio = env_utils.calcInteRatio_scan(theo_envelope_inte, experimental_envelope_inte)
    for i in range(0, num_theo_env_peaks):
      peak_inte = theo_envelope_inte[i]
      if ((inte_ratio * peak_inte) < (noise_inte_level * snr)):
        exp_env.peak_list[i] = None
    back_env_list.append(exp_env)
    if (exp_env.get_match_peak_num(refer_idx) < 2):
      miss_num = miss_num + 1
    else:
      miss_num = 0;
    if (miss_num >= max_miss_env): break
    idx = idx - 1
  remove_non_match_envs(back_env_list, refer_idx)

  ## search forward
  forw_env_list = []
  idx = env.spec_id + 1
  miss_num = 0
  while (idx < peak_matrix.spec_num):
    exp_env = get_match_exp_env(peak_matrix, env, idx, mass_tole)
    experimental_envelope_inte = exp_env.get_inte_list()
    inte_ratio = env_utils.calcInteRatio_scan(theo_envelope_inte, experimental_envelope_inte)
    for i in range(0, num_theo_env_peaks):
      peak_inte = theo_envelope_inte[i]
      if ((inte_ratio * peak_inte) < (noise_inte_level * snr)):
        exp_env.peak_list[i] = None
    forw_env_list.append(exp_env)
    if (exp_env.get_match_peak_num(refer_idx) < 2):
      miss_num = miss_num + 1
    else:
      miss_num = 0
    if (miss_num >= max_miss_env): break
    idx = idx + 1
  remove_non_match_envs(forw_env_list, refer_idx)
  
  ## merge results
  back_env_list.reverse()
  back_env_list = back_env_list + forw_env_list
  if (len(back_env_list) == 0): return None
  start_spec_id = back_env_list[0].spec_id
  end_spec_id = back_env_list[-1].spec_id
  if ((end_spec_id - start_spec_id) < 2): return None
  env_set = EnvSet(env, back_env_list, start_spec_id, end_spec_id)
  return env_set

def check_valid_env_set_seed_env(peak_matrix, env_set):
  theo_envelope_inte = env_set.seed_env.get_inte_list()
  refer_idx = theo_envelope_inte.index(max(theo_envelope_inte))
  base_idx = env_set.xic.base_spec_id
  start_idx = max(base_idx-1, 0)
  end_idx = min(base_idx+1, peak_matrix.spec_num-1)
  env_list = env_set.exp_env_list
  valid = True
  for exp_env in env_list:
    if exp_env.spec_id >= start_idx and exp_env.spec_id <= end_idx:
      if (exp_env.get_match_peak_num(refer_idx) < 2):
        valid = False
  return valid

def check_valid_env_set(peak_matrix, env_set):
  valid = True
  elems = 0
  env_xic = env_set.xic.inte_list
  for inte in env_xic:
    if (inte > 0):
      elems = elems + 1
  if (elems < 2): valid = False
  return valid
