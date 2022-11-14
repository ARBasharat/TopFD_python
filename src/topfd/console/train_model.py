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

import os
import keras
import pickle
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score

import topfd.score.model_util as model_util
import topfd.util.file_util as util
import topfd.spectrum.peak_matrix as pm
import topfd.plots.generate_eval_plots as eval_plots
from topfd.comp.multiChargeFeatureList import MultiChargeFeatureList


def get_training_data(env_coll_list):
  X = []
  Y = []
  for i in range(0, len(env_coll_list)):
    env_coll = env_coll_list[i]
    X.append((env_coll.envcnn_score, env_coll.rt_range, env_coll.charge_range, env_coll.even_odd_ratio, env_coll.agg_env_corr, env_coll.consec_peak_percent))
    Y.append(env_coll.Label)
  return X, Y

def train_model(env_coll_list, output_model_fname):
  X, Y = get_training_data(env_coll_list)
  X_train, X_test, y_train, y_test, = train_test_split(X, Y, test_size=0.33, shuffle=True, random_state=42)
  model = LogisticRegression(random_state=0).fit(X_train, y_train)
  
  print("Total Features:", len(Y), "Positive:", sum(Y), "Negative:", len(Y)-sum(Y))
  print("Train Features:", len(y_train), "Positive:", sum(y_train), "Negative:", len(y_train)-sum(y_train))
  print("Test Features:", len(y_test), "Positive:", sum(y_test), "Negative:", len(y_test)-sum(y_test))

  test_scores = [model.predict_proba([i])[0][1] for i in X_test]  
  test_scores_EnvCNN = [i[0] for i in X_test]
  test_predictions = [round(i) for i in test_scores]
  test_predictions_EnvCNN = [round(i) for i in test_scores_EnvCNN]

  balanced_accuracy = balanced_accuracy_score(y_test, test_predictions, adjusted=False)
  balanced_accuracy_EnvCNN = balanced_accuracy_score(y_test, test_predictions_EnvCNN, adjusted=False)
  print("Model Accuracy - LR:", balanced_accuracy, "and EnvCNN:", balanced_accuracy_EnvCNN)
  
  model_util.plot_score_distribution(test_scores_EnvCNN, y_test, test_scores)
  eval_plots.generate_roc_plots(y_test, test_scores)
  eval_plots.generate_roc_plots(y_test, test_scores_EnvCNN)
  return model
  
######
if __name__ == "__main__":
  in_fname = sys.argv[1]
  labeled_csv_file = sys.argv[2]
  peak_matrix_fname = sys.argv[3]
  envcnn_model_file = sys.argv[4]
  noise_intensity_level = float(sys.argv[5])
  replicate_count_for_label = int(sys.argv[6])
  
  
  # in_fname = r"C:\Users\Abdul\Documents\GitHub\test_data_xwliu\Rep_1\out_v1.pkl"
  # labeled_csv_file = r"C:\Users\Abdul\Documents\GitHub\test_data_xwliu\Rep_1\Baseline_fixed_labeling\Rep1_output_labeled.csv"
  # peak_matrix_fname = r"C:\Users\Abdul\Documents\GitHub\test_data_xwliu\Rep_1\ot_rep_1_intens_consec.txt"
  # envcnn_model_file = r"C:\Users\Abdul\Documents\GitHub\MS_Feature_Extraction_v1\model\model.h5"
  # noise_intensity_level = 180
  # replicate_count_for_label = 2
    
  output_csv_fname = in_fname.split('.')[0] + "_scored.csv"
  output_model_fname = os.path.join(os.path.dirname(in_fname.split('.')[0]), "LogisticRegression_newLabel.sav")
  
  ######
  print("Filenames:", in_fname, output_csv_fname, output_model_fname)
  env_coll_list = util.load_pickle_file_data(in_fname)
  model = keras.models.load_model(envcnn_model_file)
  df = pd.read_csv(peak_matrix_fname, sep = "\t")
  peak_matrix = pm.PeakMatrix(df, bin_size = 0.1)
  print("Peak matrix peak number", peak_matrix.get_peak_num())
  labeled_features_list = MultiChargeFeatureList.get_multiCharge_features_evaluation(labeled_csv_file)
  
  ######
  model_util.get_model_features(peak_matrix, env_coll_list, labeled_features_list, model, noise_intensity_level, replicate_count_for_label)
  model = train_model(env_coll_list, output_model_fname)
  pickle.dump(model, open(output_model_fname, 'wb'))
    
  model_util.score_env_coll(env_coll_list, model)
  model_util.plot_rank_performance(env_coll_list)
  model_util.output_env_coll_list(output_csv_fname, env_coll_list) 
 
