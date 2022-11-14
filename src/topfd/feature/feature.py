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
from topfd.score.compute_envcnn_score import get_envcnn_score
import topfd.score.compute_score_components as component_score

class Feature:
  def __init__(self, env_coll, peak_matrix, model, model_escore, feature_id, snr):
    seed_env = env_coll.seed_env
    spectra_list = peak_matrix.specs
    theo_map = env_coll.get_seed_theo_map(peak_matrix, snr)
    spectrum_noise_levels = peak_matrix.spec_min_inte
    noiseIntensityLevel = sum(spectrum_noise_levels)
    base_spec = env_coll.seed_env.spec_id
    start_spec = env_coll.start_spec_id
    env_set = env_coll.get_seed_env_set()
    self.feature_id = feature_id
    self.min_scan = env_coll.start_spec_id
    self.max_scan = env_coll.end_spec_id
    self.min_charge = env_coll.min_charge
    self.max_charge = env_coll.max_charge
    self.mono_mass = seed_env.mass
    self.rep_charge = seed_env.charge
    self.rep_mz = seed_env.pos
    self.abundance = env_coll.get_intensity(snr, peak_matrix.min_inte)
    self.min_elution_time = spectra_list[env_coll.start_spec_id][2]
    self.max_elution_time = spectra_list[env_coll.end_spec_id][2]
    self.apex_elution_time = spectra_list[seed_env.spec_id][2]
    self.elution_length = self.max_elution_time - self.min_elution_time
    
    self.percent_matched_peaks = component_score.get_matched_peaks_percent(env_set, theo_map)
    self.intensity_correlation = component_score.get_agg_env_corr(env_set)
    self.top3_correlation = component_score.get_3_scan_corr(env_set, base_spec, start_spec)
    self.even_odd_peak_ratios = component_score.get_agg_odd_even_peak_ratio(env_set)
    self.percent_consec_peaks = component_score.get_consecutive_peaks_percent(env_set)
    self.num_theo_peaks = component_score.get_num_theo_peaks(theo_map)
    self.mz_error_sum = component_score.get_mz_errors(env_set)
    self.envcnn_score = get_envcnn_score(model, peak_matrix, env_coll, noiseIntensityLevel)
    self.score = self.get_score(model_escore)
    self.label = 0
    
  def get_score(self, model_escore):
    data = []
    data.append(self.envcnn_score)
    data.append(self.elution_length/60.0)
    data.append(self.percent_matched_peaks)
    data.append(math.log(self.abundance))
    data.append(self.rep_charge)
    data.append(self.top3_correlation)
    data.append((self.max_charge-self.min_charge)/30.0)
    data.append(self.even_odd_peak_ratios)
    ecscore_data = np.expand_dims(data, axis=0)
    return model_escore.predict(ecscore_data, verbose=0)[0][0]    
    
  @staticmethod
  def output_env_coll_list(output_fname, features, sep = ","):
    txt_file = open(output_fname, 'w')
    txt_file.write("FeatureID" + sep)
    txt_file.write("MinScan" + sep)
    txt_file.write("MaxScan" + sep)
    txt_file.write("MinCharge" + sep)
    txt_file.write("MaxCharge" + sep)
    txt_file.write("MonoMass" + sep)
    txt_file.write("RepCharge" + sep)
    txt_file.write("RepMz" + sep)
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
    txt_file.write("NumberTheoreticalPeaks" + sep)
    txt_file.write("MZErrorSum" + sep)
    txt_file.write("Score" + sep)
    txt_file.write("Label" + "\n")
    for fl_idx in range(0, len(features)):
      feature = features[fl_idx]
      txt_file.write(str(feature.feature_id) + sep)  #FeatureID
      txt_file.write(str(feature.min_scan) + sep) #min scan
      txt_file.write(str(feature.max_scan) + sep)   #max scan
      txt_file.write(str(feature.min_charge) + sep) #min charge
      txt_file.write(str(feature.max_charge) + sep) #max charge
      txt_file.write(str(feature.mono_mass) + sep) #mono_mass
      txt_file.write(str(feature.rep_charge) + sep) #RepCharge
      txt_file.write(str(feature.rep_mz) + sep) #RepMz
      txt_file.write(str(feature.abundance) + sep) ## Abundance
      txt_file.write(str(feature.min_elution_time) + sep) ## MinElutionTime
      txt_file.write(str(feature.max_elution_time) + sep) ## MaxElutionTime
      txt_file.write(str(feature.apex_elution_time) + sep) ## ApexElutionTime
      txt_file.write(str(feature.elution_length) + sep) ## ElutionLength
      txt_file.write(str(feature.envcnn_score) + sep) ## EnvCNNScore
      txt_file.write(str(feature.percent_matched_peaks) + sep) ## PercentMatchedPeaks
      txt_file.write(str(feature.intensity_correlation) + sep) ## IntensityCorrelation
      txt_file.write(str(feature.top3_correlation) + sep) ## Top3Correlation
      txt_file.write(str(feature.even_odd_peak_ratios) + sep) ## EvenOddPeakRatios
      txt_file.write(str(feature.percent_consec_peaks) + sep) ## PercentConsecPeaks
      txt_file.write(str(feature.num_theo_peaks) + sep) ## NumberTheoreticalPeaks
      txt_file.write(str(feature.mz_error_sum) + sep) ## MZErrorSum
      txt_file.write(str(feature.score) + sep) ## Score
      txt_file.write(str(feature.label) + "\n") ## Label
    txt_file.close()
