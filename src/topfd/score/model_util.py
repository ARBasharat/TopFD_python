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
from matplotlib import pyplot as plt

from topfd.score.compute_envcnn_score import get_envcnn_score
import topfd.score.compute_score_components as scorer

def get_model_features(peak_matrix, env_coll_list, labeled_features_list, envcnn_model, noise_intensity_level, replicate_count_for_label):
  for i in range(0, len(env_coll_list)):
    if i%100 == 0: print("Computing Score for Envelope collection:", i)
    env_coll = env_coll_list[i]
    env_coll.envcnn_score = get_envcnn_score(envcnn_model, peak_matrix, env_coll, noise_intensity_level)
    env_coll.even_odd_ratio = scorer.get_agg_odd_even_peak_ratio(env_coll)
    env_coll.agg_env_corr = scorer.get_agg_env_corr(env_coll)
    env_coll.consec_peak_percent = scorer.get_consecutive_peaks_percent(env_coll)
    env_coll.matched_peak_percent = scorer.get_matched_peaks_percent(env_coll)
    env_coll.top_3_scan_corr = scorer.get_3_scan_corr(env_coll)
    env_coll.rt_range = scorer.get_rt_range(env_coll)
    env_coll.charge_range = scorer.get_charge_range(env_coll)
    env_coll.Label = 0
    if labeled_features_list[i].Label == replicate_count_for_label:
      env_coll.Label = 1

def get_model_features_list(env_coll_list):
  envcnn_scores = []
  even_odd_peak_intens_ratios = []
  agg_env_corrs = []
  consec_peak_percents = []
  matched_peak_percent = []
  top_3_scan_corrs = []
  rt_ranges = []
  charge_ranges = []
  labels = []
  for i in range(0, len(env_coll_list)):
    env_coll = env_coll_list[i]
    print("Computing Score for Envelope collection:", i, env_coll.envcnn_score, env_coll.even_odd_ratio, env_coll.agg_env_corr, env_coll.consec_peak_percent, env_coll.matched_peak_percent, env_coll.rt_range, env_coll.charge_range, env_coll.Label)
    envcnn_scores.append(env_coll.envcnn_score)
    even_odd_peak_intens_ratios.append(env_coll.even_odd_ratio)
    agg_env_corrs.append(env_coll.agg_env_corr)
    consec_peak_percents.append(env_coll.consec_peak_percent)
    matched_peak_percent.append(env_coll.matched_peak_percent)
    top_3_scan_corrs.append(env_coll.top_3_scan_corr)
    rt_ranges.append(env_coll.rt_range)
    charge_ranges.append(env_coll.charge_range)
    labels.append(env_coll.Label)

def plot_score_distribution(test_scores_EnvCNN, y_test, test_scores):
  y_p = [test_scores[i] for i in range(len(test_scores_EnvCNN)) if y_test[i] == 1]
  y_n = [test_scores[i] for i in range(len(test_scores_EnvCNN)) if y_test[i] == 0]
  bin_size = 0.01
  n = math.ceil((max(y_n) - min(y_n))/bin_size)
  p = math.ceil((max(y_p) - min(y_p))/bin_size)
  plt.Figure()  
  plt.hist(y_n, color = 'red', bins = n, alpha = 0.5)
  plt.hist(y_p, color = 'blue', bins = p, alpha = 0.5)
  plt.legend(['-ve Features', '+ve Features'])
  plt.title("Scoring Distribution (Logistic Regression Model)")
  plt.show()
  plt.close()
  
  y_envcnn_p = [test_scores_EnvCNN[i] for i in range(len(test_scores_EnvCNN)) if y_test[i] == 1]
  y_envcnn_n = [test_scores_EnvCNN[i] for i in range(len(test_scores_EnvCNN)) if y_test[i] == 0]
  bin_size = 0.01
  n = math.ceil((max(y_envcnn_n) - min(y_envcnn_n))/bin_size)
  p = math.ceil((max(y_envcnn_p) - min(y_envcnn_p))/bin_size)
  plt.Figure()  
  plt.hist(y_envcnn_n, color = 'red', bins = n, alpha = 0.5)
  plt.hist(y_envcnn_p, color = 'blue', bins = p, alpha = 0.5)
  plt.legend(['-ve Features', '+ve Features'])
  plt.title("Scoring Distribution (EnvCNN Model)")
  plt.show()
  plt.close() 

def plot_rank_performance(env_coll_list):
  x_OG = []
  y_OG = []
  bin_size = 100
  for i in range(0, len(env_coll_list), bin_size):
    y_OG.append(sum([env_coll_list[i].Label if i < len(env_coll_list) else 0 for i in range(i, i+bin_size)]))
    x_OG.append(i)
    
  env_coll_list.sort(key=lambda x: x.envcnn_score, reverse=True) 
  x_EnvCNN = []
  y_EnvCNN = []
  bin_size = 100
  for i in range(0, len(env_coll_list), bin_size):
    y_EnvCNN.append(sum([env_coll_list[i].Label if i < len(env_coll_list) else 0 for i in range(i, i+bin_size)]))
    x_EnvCNN.append(i)
    
    
  env_coll_list.sort(key=lambda x: x.score, reverse=True) 
  x_LR = []
  y_LR = []
  bin_size = 100
  for i in range(0, len(env_coll_list), bin_size):
    y_LR.append(sum([env_coll_list[i].Label if i < len(env_coll_list) else 0 for i in range(i, i+bin_size)]))
    x_LR.append(i)
  
  plt.Figure()  
  plt.plot(x_OG, y_OG)
  plt.plot(x_EnvCNN, y_EnvCNN)
  plt.plot(x_LR, y_LR)
  plt.xlabel("Features")
  plt.ylabel("Positive Features in 100 feature bins")
  plt.title("Number of positive features in 100 feature bins")
  plt.legend(['Feature ID', 'EnvCNN Score', 'Logistic Regression Model'])
  plt.show()
  plt.close()  

def score_env_coll(env_coll_list, model):
  for i in range(0, len(env_coll_list)):
    env_coll = env_coll_list[i]
    X = (env_coll.envcnn_score, env_coll.rt_range, env_coll.charge_range, env_coll.even_odd_ratio, env_coll.agg_env_corr, env_coll.consec_peak_percent)
    env_coll.score = model.predict_proba([X])[0][1]
  
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
  txt_file.write("ShiftNum" + sep)
  txt_file.write("Abundance" + sep)
  txt_file.write("MinElutionTime" + sep)
  txt_file.write("MaxElutionTime" + sep)
  txt_file.write("ApexElutionTime" + sep)
  txt_file.write("ElutionLength" + sep)
  txt_file.write("EnvCNNScore" + sep)
  txt_file.write("PercentMatchedPeaks" + sep)
  txt_file.write("IntensityCorrelation" + sep)
  txt_file.write("Top3Correlation" + sep)
  txt_file.write("EvenOddPeakRatios" + sep)
  txt_file.write("PercentConsecPeaks" + sep)
  txt_file.write("Score" + sep)
  txt_file.write("Label" + "\n")
  for coll_idx in range(0, len(env_coll_list)):
    coll = env_coll_list[coll_idx]
    txt_file.write(str(coll_idx+1) + sep)
    txt_file.write(str(coll.start_spec_id) + sep) #min scan
    txt_file.write(str(coll.end_spec_id) + sep)   #max scan
    txt_file.write(str(coll.min_charge) + sep) #min charge
    txt_file.write(str(coll.max_charge) + sep) #max charge
    txt_file.write(str(coll.get_mono_mass()) + sep) #mono_mass
    txt_file.write(str(coll.get_refined_mono_mass()) + sep) #mono_mass
    txt_file.write(str(0) + sep) #mono_mass
    txt_file.write(str(coll.get_intensity()) + sep) ## Abundance
    txt_file.write(str(coll.get_min_elution_time()) + sep) ## MinElutionTime
    txt_file.write(str(coll.get_max_elution_time()) + sep) ## MaxElutionTime
    txt_file.write(str(coll.get_apex_elution_time()) + sep) ## ApexElutionTime
    txt_file.write(str(coll.get_elution_length()) + sep) ## ElutionLength
    txt_file.write(str(coll.envcnn_score) + sep) ## EnvCNNScore
    txt_file.write(str(coll.matched_peak_percent) + sep) ## PercentMatchedPeaks
    txt_file.write(str(coll.agg_env_corr) + sep) ## IntensityCorrelation
    txt_file.write(str(coll.top_3_scan_corr) + sep) ## Top3Correlation
    txt_file.write(str(coll.even_odd_ratio) + sep) ## EvenOddPeakRatios
    txt_file.write(str(coll.consec_peak_percent) + sep) ## PercentConsecPeaks
    txt_file.write(str(coll.score) + sep) ## Score
    txt_file.write(str(coll.Label) + "\n") ## Label
  txt_file.close()