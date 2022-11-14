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

#!/usr/bin/python3

import sys
import numpy as np
import pandas as pd
import topfd.spectrum.peak_matrix as pm
import topfd.envelope.env_reader as env_reader
import topfd.env_set.env_set_util as env_set_util
import topfd.env_collection.env_coll_util as env_coll_util
import topfd.util.file_util as util

from topfd.env_set.env_set_plot import plot_3d, plot_xic

def filter_envs(peak_matrix, seed_envs, mass_tole):
  result_envs = []
  for env in seed_envs:
    valid = env_set_util.check_valid_env_set(peak_matrix, env, mass_tole)
    if valid:
      result_envs.append(env)
  return result_envs

def output_env_coll_list(output_fname, env_coll_list):
  txt_file = open(output_fname, 'w')
  sep = ","
  txt_file.write("FeatureID" + sep)
  txt_file.write("MinScan" + sep)
  txt_file.write("MaxScan" + sep)
  txt_file.write("MinCharge" + sep)
  txt_file.write("MaxCharge" + sep)
  txt_file.write("MonoMass" + sep)
  txt_file.write("RefinedMonoMass" + sep)
  txt_file.write("Abundance" + sep)
  txt_file.write("MinElutionTime" + sep)
  txt_file.write("MaxElutionTime" + sep)
  txt_file.write("ApexElutionTime" + sep)
  txt_file.write("ElutionLength" + "\n")
  for coll_idx in range(0, len(env_coll_list)):
    coll = env_coll_list[coll_idx]
    txt_file.write(str(coll_idx+1) + sep)
    txt_file.write(str(coll.start_spec_id) + sep) #min scan
    txt_file.write(str(coll.end_spec_id) + sep)   #max scan
    txt_file.write(str(coll.min_charge) + sep) #min charge
    txt_file.write(str(coll.max_charge) + sep) #max charge
    txt_file.write(str(coll.get_mono_mass()) + sep) #mono_mass
    txt_file.write(str(coll.get_refined_mono_mass()) + sep) #mono_mass
    txt_file.write(str(coll.get_intensity()) + sep) ## Abundance
    txt_file.write(str(coll.get_min_elution_time()) + sep) ## MinElutionTime
    txt_file.write(str(coll.get_max_elution_time()) + sep) ## MaxElutionTime
    txt_file.write(str(coll.get_apex_elution_time()) + sep) ## ApexElutionTime
    txt_file.write(str(coll.get_elution_length()) + "\n") ## ElutionLength
  txt_file.close()

if __name__ == "__main__":
  print("Get features")
  input_fname = sys.argv[1]
  mass_tole = float(sys.argv[2])
  env_fname = sys.argv[3]
  base_env_fname = sys.argv[4]
  output_fname = sys.argv[5]
    
  df = pd.read_csv(input_fname, sep = "\t")
  max_spec_id = np.max(df['spec_id'])
  print("Peak number", len(df), "max spec id", max_spec_id)
  bin_size = 0.1
  print("bin size", bin_size)
  peak_matrix = pm.PeakMatrix(df, bin_size)
  print("Peak matrix peak number", peak_matrix.get_peak_num())

  seed_envs = env_reader.read_env_file(env_fname)
  print("Env number", len(seed_envs))

  env_base = util.load_pickle_file_data(base_env_fname)
  
  mass_tole = 0.01
  max_miss_env = 2
  max_miss_charge = 2
  max_miss_peak = 2
  para_max_charge = 30
  ratio_multi = 2

  print("mass tolerance", mass_tole, "max miss env", max_miss_env, "max miss charge", max_miss_charge)
  print("para max chrage", para_max_charge, "max miss peak", max_miss_peak, "ratio_multi", ratio_multi)

  print("original envelope number", len(seed_envs))
  #seed_envs = filter_envs(peak_matrix, seed_envs, mass_tole)

  seed_num = len(seed_envs)
  env_coll_num = 0
  env_coll_list = []
  #for env in seed_envs:
  for i in range(seed_num):
    env = seed_envs[i]
    if i%1000 == 0:
      print("start env", i, seed_num, "env collection num:", env_coll_num)
    env_coll = env_coll_util.find_env_collection(peak_matrix, env, mass_tole, 
      max_miss_env, max_miss_charge, max_miss_peak, para_max_charge, ratio_multi, env_base)
    if env_coll is not None:
      env_coll.remove_matrix_peaks(peak_matrix)
      env_coll_list.append(env_coll)
      env_coll_num = env_coll_num + 1
  print("env collection number", env_coll_num)
  output_env_coll_list(output_fname, env_coll_list)
