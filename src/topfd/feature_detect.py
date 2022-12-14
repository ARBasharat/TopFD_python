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

import os
import sys
import argparse
import numpy as np
import pandas as pd
import tensorflow
from tensorflow.keras.models import load_model

import topfd.msalign.msalign_to_env as msalign
import topfd.spectrum.peak_matrix as pm
import topfd.envelope.env_reader as env_reader
import topfd.envelope.evaluate_envelope as evaluate_envelope
import topfd.preprocess.mzml_to_txt as mzml_reader
import topfd.env_set.env_set_util as env_set_util
import topfd.env_collection.env_coll_util as env_coll_util
import topfd.util.file_util as util
from topfd.feature.feature import Feature

if __name__ == "__main__":
  console_dir =  os.path.realpath(__file__)
  base_dir = console_dir.split("src")[0]
  print("Get features - In main function!!")
  parser = argparse.ArgumentParser(description='Extract the proteoform features.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("-M", "--inputFname", default = r"C:\Users\Abdul\Documents\GitHub\TopFD_python\data\CPTAC_Intact_rep1_15Jan15_Bane_C2-14-08-02RZ.mzML", help="mzML data file")
  parser.add_argument("-m", "--envFname", default = r"C:\Users\Abdul\Documents\GitHub\TopFD_python\data\CPTAC_Intact_rep1_15Jan15_Bane_C2-14-08-02RZ_ms1.msalign", help="Seed Envelope File generated by MS1 msalign file")
  parser.add_argument("-b", "--baseEnvFname", default = os.path.join(base_dir, "base_data/theo_patt.pkl"), help="Seed Envelope File generated by MS1 msalign file")
  parser.add_argument("-e", "--envcnnModelFile", default = os.path.join(base_dir, "model/model.h5"), help="EnvCNN Model file (model.py)")
  parser.add_argument("-s", "--ecscoreModelFile", default = os.path.join(base_dir, "model/ecscore_model.h5"), help="ECScore Model file (model.py)")
  parser.add_argument("-v", "--ecscore_cutoff", default = 0.5, help="ECScore cutoff (0-1)", type=float)
  parser.add_argument("-O", "--outputFile", default = "output.csv", help="Set the output data file")
  args = parser.parse_args()
  
  input_fname = args.inputFname
  env_fname = args.envFname
  base_env_fname = args.baseEnvFname
  output_fname = args.outputFile
 
  bin_size = 0.1
  neighbor_mass_tole = 0.01
  mass_tole = 0.008
  corr_tole = 0.05
  max_miss_env = 2
  max_miss_charge = 2
  max_miss_peak = 2
  para_max_charge = 30
  ratio_multi = 2.0
  match_peak_tole = 3
  match_envelope_tolerance = 10E-6
  time_overlap_tol = 0.8
  percent_bound = 1.0
  snr = 3.0
  
  ## Read envelope file
  env_base = util.load_pickle_file_data(base_env_fname)
  seed_envs = msalign.get_envelopes_from_msalign(env_fname, env_base, percent_bound)
  print("Number of base peaks: " + str(len(seed_envs)) + "\n")
  
  ### Read mzML file
  df = mzml_reader.mzML_to_df(input_fname)
  peak_matrix = pm.PeakMatrix(df, bin_size)
  print("Peak matrix peak number", peak_matrix.get_peak_num())
  
  ### Load models
  model = load_model(args.envcnnModelFile)
  model.compile(loss = "binary_crossentropy", metrics=['accuracy'], optimizer=tensorflow.keras.optimizers.Adam())
  model_escore = load_model(args.ecscoreModelFile)
  model_escore.compile(loss = "binary_crossentropy", metrics=['accuracy'], optimizer=tensorflow.keras.optimizers.Adam())
  

  seed_num = len(seed_envs)
  env_coll_num = 0
  env_coll_list = []
  features = []
  seed_env_idx = 0
  for seed_env_idx in range(0, seed_num):
    if seed_env_idx%1000 == 0:
      print("Processing", seed_env_idx, "of", seed_num, "and env collection num:", env_coll_num)
    env = seed_envs[seed_env_idx]      
    valid = evaluate_envelope.preprocess_env(peak_matrix, env, mass_tole, corr_tole, snr)
    if (not valid): continue
  
    env_coll = env_coll_util.find_env_collection(peak_matrix, env, mass_tole, max_miss_env, max_miss_charge, max_miss_peak,
                            para_max_charge, ratio_multi, match_peak_tole, env_base, snr)
    if env_coll is not None:
      if env_coll_util.check_in_existing_features(peak_matrix, env_coll, env_coll_list, match_envelope_tolerance, time_overlap_tol):
        continue
      env_coll.refine_mono_mass()
      feature = Feature(env_coll, peak_matrix, model, model_escore, env_coll_num, snr)
      if feature.score < args.ecscore_cutoff:
        continue
      env_coll.remove_matrix_peaks(peak_matrix)
      env_coll_list.append(env_coll)
      features.append(feature)
      env_coll_num = env_coll_num + 1
  print("env collection number", env_coll_num)
  Feature.output_env_coll_list(output_fname, features)
  