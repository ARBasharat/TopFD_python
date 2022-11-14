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

import os
import pickle
import topfd.envelope.evaluate_envelope as evaluate_envelope
import topfd.score.env_util as env_utils
from topfd.msalign.env_base import EnvBase
from topfd.envelope.seed_envelope import SeedEnvelope

def findLocalMinima(arr):
  n = len(arr)
  minima = []
  for i in range(1, n - 1):
    if ((arr[i - 1] > arr[i]) and (arr[i] < arr[i + 1])):
      if (i - 2 > 0):
        if (arr[i - 2] <= arr[i]):
          continue
      if (i + 2 < n):
        if (arr[i + 2] <= arr[i]):
          continue
      minima.append(i)
  return minima

# def get_half_charge_env(env, even_odd_peak_ratios):
#   return None
  # mass = env.mass
  # charge = env.charge
  # mz = env_utils.get_mz(mass, charge);
  # distribution = env.get_pos_list()

  # if (even_odd_peak_ratios < 0):
  #   mz = mz + (distribution[1] - distribution[0])
  # new_charge = int(charge / 2)
  # if (new_charge == 0): new_charge = new_charge + 1;
  # new_mass = env_utils.get_mass(mz, new_charge)

  # ## get a reference distribution based on the base mass
  # get_env_obj(env_base, new_mass, new_charge, env.intensity, spec_list, i, peak_id, percent_bound)
  # ref_env_ptr = EnvBase.getStaticEnvByMonoMass(new_mass)
  # if (ref_env_ptr == None): return None
  # theo_env_ptr = ref_env_ptr.distrToTheoMono(mz, new_charge)
  # env_peaks_mz = []
  # env_peaks_inte = []
  # for i in range(0, theo_env_ptr.getPeakNum()):
  #   env_peaks_mz.append(theo_env_ptr.getMz(i))
  #   env_peaks_inte.append(theo_env_ptr.getIntensity(i))
  # sp_peak = SeedEnvelope(env.getSpecId(), env.getEnvId(), env.getPos(), new_mass, env.getInte(), new_charge, env_peaks_mz, env_peaks_inte)
  # return sp_peak

def get_half_charge_env(env, env_base, even_odd_peak_ratios):
  mass = env.mass
  charge = env.charge
  mz = round(env_utils.get_mz(mass, charge), 6)
  
  distribution = env.get_pos_list()
  
  if even_odd_peak_ratios < 0:
    mz = mz + (env.peak_list[1].pos - env.peak_list[1].pos)
  new_charge = int(env.charge / 2)
  if new_charge == 0:
    new_charge = new_charge + 1
  new_mass = env_utils.get_mass(mz, new_charge)
  new_env = env_base.get_env_mono_mass(new_mass, new_charge, mz)
  env_peaks_mz = [i.pos for i in new_env.peaks]
  env_peaks_inte = [i.inte for i in new_env.peaks]
  sp_peak = SeedEnvelope(env.spec_id, env.env_id, mz, new_mass, env.inte, new_charge, env_peaks_mz, env_peaks_inte)
  return sp_peak


def test_half_charge_state(peak_matrix, env, top_peak_env_set, even_odd_peak_ratios, mass_tole, env_base, snr):
  half_charge_env = get_half_charge_env(env, env_base, even_odd_peak_ratios)
  valid = evaluate_envelope.preprocess_env(peak_matrix, half_charge_env, mass_tole, 0.5, snr);
  if (not valid): return None
  return half_charge_env
  
def check_neighbors(spectrum_peak, matched_peaks, debug, n_tol = 1):
  ## check if we have matched peaks in neighboring 2 scans on both sides 
  matched_peaks_ids = [i.spId for i in matched_peaks]
  neighbors = sum([1 for i in matched_peaks_ids if i >= spectrum_peak.spId - 3 and i <= spectrum_peak.spId + 3])
  if neighbors <= n_tol:
    debug.write_messages("########## Neighbor not found!!! \n")
    return False
  return True

def chek_output(feature_boundary, xic_data, debug):
  if feature_boundary is None:
    debug.write_messages("********* Null Output!!! \n")
    return False
  temp_y = xic_data[feature_boundary[0]:feature_boundary[1] + 1]
  if sum(temp_y) == 0:
    debug.write_messages("$$$$$$$$$$$ Not enough peak data!!! \n")
    return False
  return True

def check_feature_length(refined_feature_boundary, feature_boundary, xic_data, debug, f_len = 0):
  if refined_feature_boundary is None:
    debug.write_messages("********* Null Output!!! \n")
    return False
  debug.write_messages("Scan Range: [" + str(feature_boundary[0]) + ", " + str(feature_boundary[1]) + "]")
  debug.write_messages("Refined Scan Range: [" + str(refined_feature_boundary[0]) + ", " + str(refined_feature_boundary[1]) + "]")
  temp_y = xic_data[refined_feature_boundary[0]:refined_feature_boundary[1] + 1]
  if sum(temp_y) == 0:
    debug.write_messages("$$$$$$$$$$$ Not enough peak data!!! \n")
    return False
  if refined_feature_boundary[1] - refined_feature_boundary[0] + 1 <= f_len:
    debug.write_messages("$$$$$$$$$$$ Skipping Feature of length " + str(f_len) + " or less!!! \n")
    return False
  return True

def str2bool(v):
  if isinstance(v, bool):
    return v
  if v.lower() in ('yes', 'true', 't', 'y', '1'):
    return True
  elif v.lower() in ('no', 'false', 'f', 'n', '0'):
    return False
  else:
      return False

class Debug:
  def __init__(self, args, debug = False, console = False):
    # self.filename = os.path.join(args.output_dir, "Feature_Detection_Log.txt")
    self.filename = "Feature_Detection_Log.txt"
    self.debug = args.debugOutput
    self.console = args.consoleOutput
    self.file = None
    if args.debugOutput:
      self.open_debug_file()

  def open_debug_file(self):
    if self.debug:
      self.file = open(self.filename, 'a+')
  
  def close_debug_file(self):
    if self.debug:
      self.file.close()
  
  def write_messages(self, message):
    if self.console:
      print(message)
    if self.debug:
      self.file.write(message + "\n")
  
  
# def write_messages(message, args):
#   if args.consoleOutput:
#     print(message)
#   filename = "Feature_Detection_Log.txt"
#   file = open(filename, 'a+') 
#   file.write(message + "\n")
#   file.close() 
