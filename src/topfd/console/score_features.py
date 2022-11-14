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
sys.path.insert(0, r"C:\Users\Abdul\Documents\GitHub\MS_Feature_Extraction_xwliu\src")

import keras
import pickle
import pandas as pd
from sklearn.metrics import balanced_accuracy_score

import topfd.util.file_util as util
import topfd.spectrum.peak_matrix as pm
from topfd.comp.multiChargeFeatureList import MultiChargeFeatureList
import topfd.plots.generate_eval_plots as eval_plots
from topfd.score.model_util import get_model_features, score_env_coll, output_env_coll_list, plot_score_distribution, plot_rank_performance

def test_model_performance(env_coll_list):
  labels = [env_coll.Label for env_coll in env_coll_list]
  envcnn_score = [env_coll.envcnn_score for env_coll in env_coll_list]
  envcnn_predictions = [round(i) for i in envcnn_score]
  lr_score = [env_coll.score for env_coll in env_coll_list]
  lr_predictions = [round(i) for i in lr_score]

  balanced_accuracy = balanced_accuracy_score(labels, lr_predictions, adjusted=False)
  balanced_accuracy_EnvCNN = balanced_accuracy_score(labels, envcnn_predictions, adjusted=False)
  print("Model Accuracy - LR:", balanced_accuracy, "and EnvCNN:", balanced_accuracy_EnvCNN)
  
  plot_score_distribution(envcnn_score, labels, lr_score)
  eval_plots.generate_roc_plots(labels, lr_score)
  eval_plots.generate_roc_plots(labels, envcnn_score)
  plot_rank_performance(env_coll_list)  
  

######
if __name__ == "__main__":
  in_fname = sys.argv[1]
  labeled_csv_file = sys.argv[2]
  peak_matrix_fname = sys.argv[3]
  envcnn_model_file = sys.argv[4]
  model_fname = sys.argv[5]
  noise_intensity_level = float(sys.argv[6])
  replicate_count_for_label = int(sys.argv[7])
  
  # in_fname = r"C:\Users\Abdul\Documents\GitHub\test_data_xwliu\Rep_1\out_v1.pkl"
  # # labeled_csv_file = r"C:\Users\Abdul\Documents\GitHub\test_data_xwliu\Rep_1\Baseline_fixed_labeling\Rep1_output_labeled.csv"
  # labeled_csv_file = r"C:\Users\Abdul\Documents\GitHub\test_data_xwliu\Rep_1\Baseline\Rep_2_out_v1_labeled.csv"
  # peak_matrix_fname = r"C:\Users\Abdul\Documents\GitHub\test_data_xwliu\Rep_1\ot_rep_1_intens_consec.txt"
  
  # envcnn_model_file = r"C:\Users\Abdul\Documents\GitHub\MS_Feature_Extraction_v1\model\model.h5"
  # model_fname = r"C:\Users\Abdul\Documents\GitHub\test_data_xwliu\Rep_1\LogisticRegression.sav"
  # noise_intensity_level = 180
  # replicate_count_for_label = 2
  
  output_csv_fname = in_fname.split('.')[0] + "_scored.csv"
  
  ######
  print("Filenames:", in_fname, output_csv_fname)
  env_coll_list = util.load_pickle_file_data(in_fname)
  envcnn_model = keras.models.load_model(envcnn_model_file)
  model = pickle.load(open(model_fname, 'rb'))
  df = pd.read_csv(peak_matrix_fname, sep = "\t")
  peak_matrix = pm.PeakMatrix(df, bin_size = 0.1)
  print("Peak matrix peak number", peak_matrix.get_peak_num())
  labeled_features_list = MultiChargeFeatureList.get_multiCharge_features_evaluation(labeled_csv_file)
  labeled_features_list.featureList.sort(key=lambda x: x.FeatureID, reverse=False)
  
  # # ######
  get_model_features(peak_matrix, env_coll_list, labeled_features_list, envcnn_model, noise_intensity_level, replicate_count_for_label)
  score_env_coll(env_coll_list, model)
  test_model_performance(env_coll_list)
  output_env_coll_list(output_csv_fname, env_coll_list)
 
