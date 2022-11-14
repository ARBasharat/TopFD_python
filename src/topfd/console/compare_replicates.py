#!/usr/bin/python3

import os 
import argparse  

from copy import deepcopy
from collections import Counter
from topfd.comp.multiChargeFeatureList import MultiChargeFeatureList
from matplotlib import pyplot as plt

def sort_features(multicharge_features):
  multicharge_features.featureList.sort(key=lambda x: x.Score, reverse=True)
  
def shortlist_features(multicharge_features, n):
  if n == -1:
    return multicharge_features.featureList
  return multicharge_features.featureList[0:n]

def get_common_features(multicharge_features_rep_1, multicharge_features_rep_2, tolerance, time_tol):
  featureList = deepcopy(multicharge_features_rep_1)
  ## Sort features in replicate 2 by mass for binary search
  featureList_2 = deepcopy(multicharge_features_rep_2)
  featureList_2 .sort(key=lambda x: (x is None, x.MonoMass), reverse=False)
  
  ## Get common features based on the RT overlap
  common_features = []
  for feature_idx in range(0, len(featureList)):
    if feature_idx%10000 == 0:
      print("processing feature:", feature_idx)
    feature = featureList[feature_idx]
    if hasattr(feature, 'used'):
      continue
    else:
      tmp_common_features = []
      temp_features = _getMatchedFeaturesIndicesMultiCharge(featureList_2, feature, tolerance)
      overlapping_features = _get_overlapping_featuresMultiCharge(temp_features, feature, time_tol)
      if len(overlapping_features) > 0:
        print ("feature 1 mass", feature.MonoMass, "feature 2 mass", overlapping_features[0].MonoMass)
        coverage = [f.coverage for f in overlapping_features]
        selected_feature = overlapping_features[coverage.index(max(coverage))]
        index = next((i for i, item in enumerate(featureList_2) if item is not None and item.FeatureID == selected_feature.FeatureID), -1)
        featureList_2[index].used = True
        tmp_common_features.append((1, index))
      tmp_common_features.insert(0, (0, feature_idx))
      common_features.append(tmp_common_features)
  return common_features

def _getMatchedFeaturesIndicesMultiCharge(feature_list, feature, tolerance):
  prec_mass = feature.MonoMass
  error_tole = prec_mass * tolerance
  ext_masses = _getExtendMasses(prec_mass)
  min_idx = _binary_search(feature_list, ext_masses[len(ext_masses) - 2] - (2 * error_tole))
  max_idx = _binary_search(feature_list, ext_masses[len(ext_masses) - 1] + (2 * error_tole))
  feature_masses = [feature_list[f_idx] for f_idx in range(min_idx, max_idx) if not hasattr(feature_list[f_idx] , 'used')]
  matched_features_indices = []
  for temp_feature in feature_masses:
    for k in range(0, len(ext_masses)):
      mass_diff = abs(ext_masses[k] - temp_feature.MonoMass)
      if (mass_diff <= error_tole):
        matched_features_indices.append(temp_feature)
        break
  return matched_features_indices

def _get_overlapping_featuresMultiCharge(temp_features, feature, time_tol):
  overlapping = []
  # print(feature.MinElutionTime, feature.MaxElutionTime)
  for feature_idx in range(0, len(temp_features)):
    f = temp_features[feature_idx]
    start_rt, end_rt = _get_overlap(f, feature, time_tol)
    overlapping_rt_range = end_rt - start_rt
    # print(f.MinElutionTime, f.MaxElutionTime, '---', start_rt, end_rt, overlapping_rt_range)
    if overlapping_rt_range > 0:
      min_rt = min(f.MinElutionTime - time_tol, feature.MinElutionTime)
      max_rt = max(f.MaxElutionTime + time_tol, feature.MaxElutionTime)
      overall_rt_range = max_rt - min_rt
      f.coverage = overlapping_rt_range/overall_rt_range
      overlapping.append(f)
  return overlapping

def _getExtendMasses(mass):
  IM = 1.00235
  extend_offsets_ = [0, -IM, IM, 2 * -IM, 2 * IM]  
  result = []
  for i in range(0, len(extend_offsets_)):
    new_mass = mass + extend_offsets_[i]
    result.append(new_mass)
  return result

def _binary_search(feature_list, mass):
  low = 0
  mid = 0
  high = len(feature_list) - 1
  while low <= high:
    mid = (high + low) // 2
    if feature_list[mid].MonoMass < mass:
      low = mid + 1
    elif feature_list[mid].MonoMass > mass:
      high = mid - 1
  return low

def _get_overlap(f, feature, time_tol):
 start_rt = max(feature.MinElutionTime, f.MinElutionTime - time_tol)
 end_rt = min(feature.MaxElutionTime, f.MaxElutionTime + time_tol)
 return (start_rt, end_rt)

def label_features(common, featureList_all):
  for j in range(0, len(featureList_all)):
    featureList_all[j].sort(key=lambda x: (x is None, x.Score), reverse=True)
    for f_idx in range(j + 1, len(featureList_all)):
      featureList_all[f_idx].sort(key=lambda x: (x is None, x.MonoMass), reverse=False)
    for elem in common:
      if elem[0][0] == j:
        for i in elem:
          featureList_all[i[0]][i[1]].Label = len(elem)

def write_Combined_feature_detailed_10(common_features_all, featureList_all, filename):
  featureList_all[0].sort(key=lambda x: x.Score, reverse=True)
  for f_idx in range(1, len(featureList_all)):
    featureList_all[f_idx].sort(key=lambda x: (x is None, x.MonoMass), reverse=False)
  
  file = open(filename, 'w+')
  for feature_idx in common_features_all:
    if len(feature_idx) == len(featureList_all):
      file.write("FEATURE_Begin \n")
      FeatureID = [featureList_all[idx[0]][idx[1]].FeatureID for idx in feature_idx]
      file.write("FEATURE_Idx: " + str(list(FeatureID)) + "\n")
      Replicate = [idx[0]+1 for idx in feature_idx]
      file.write("Replicate: " + str(list(Replicate)) + "\n")
      MinScan = [featureList_all[idx[0]][idx[1]].MinScan for idx in feature_idx]
      file.write("Start_Scan: " + str(list(MinScan)) + "\n")
      MaxScan = [featureList_all[idx[0]][idx[1]].MaxScan for idx in feature_idx]
      file.write("End_Scan: " + str(list(MaxScan)) + "\n")
      MinElutionTime = [featureList_all[idx[0]][idx[1]].MinElutionTime for idx in feature_idx]
      file.write("Start_Retention_Time: " + str(list(MinElutionTime)) + "\n")
      MaxElutionTime = [featureList_all[idx[0]][idx[1]].MaxElutionTime for idx in feature_idx]
      file.write("End_Retention_Time: " + str(list(MaxElutionTime)) + "\n")
      ElutionLength = [featureList_all[idx[0]][idx[1]].ElutionLength for idx in feature_idx]
      file.write("Total_Retention_Time: " + str(list(ElutionLength)) + "\n")
      MinCharge = [featureList_all[idx[0]][idx[1]].MinCharge for idx in feature_idx]
      file.write("Minimum_Charge: " + str(list(MinCharge)) + "\n")
      MaxCharge = [featureList_all[idx[0]][idx[1]].MaxCharge for idx in feature_idx]
      file.write("Maximum_Charge: " + str(list(MaxCharge)) + "\n")
      MonoMass = [featureList_all[idx[0]][idx[1]].MonoMass for idx in feature_idx]
      file.write("Monoisotopic_Mass: " + str(list(MonoMass)) + "\n")
      Abundance = [featureList_all[idx[0]][idx[1]].Abundance for idx in feature_idx]
      file.write("Abundance: " + str(list(Abundance)) + "\n")
      RepMz = [featureList_all[idx[0]][idx[1]].RepMz for idx in feature_idx]
      file.write("Representative_MZ: " + str(list(RepMz)) + "\n")
      RepCharge = [featureList_all[idx[0]][idx[1]].RepCharge for idx in feature_idx]
      file.write("Representative_Charge: " + str(list(RepCharge)) + "\n")
      RepScore = [featureList_all[idx[0]][idx[1]].Score for idx in feature_idx]
      file.write("Score: " + str(list(RepScore)) + "\n")
      file.write("FEATURE_END \n\n")
  file.close()

def plot_distribution_combined(common_features, Label = False):
  labels = [len(i) for i in common_features]
  labels_counter_1 = sorted(Counter(labels).items(), reverse = True)
  print("Label Counter", labels_counter_1)
  
  width = 0.5
  plt.figure()
  plt.bar(Counter(labels).keys(), Counter(labels).values(), width)
  plt.title("Labels")
  plt.xlabel("Feature found in # of replicates")
  plt.savefig("distribution.png", dpi=500)
  plt.close()
  
if __name__ == "__main__":
  print("In main function!!")
  parser = argparse.ArgumentParser(description='Generate data matrix for the mzML data.')
  parser.add_argument("-F", "--replicate1_file", default = "", help="Scored feature CSV file (Replicate 1)")
  parser.add_argument("-f", "--replicate2_file", default = "", help="Scored feature CSV file (Replicate 2)")
  parser.add_argument("-e", "--tolerance", default = 10E-6, help="Mass tolerance (ppm)", type = float)
  parser.add_argument("-t", "--timeTolerance", default = 1.0, help="Time tolerance (minutes)", type = float)
  parser.add_argument("-n", "--NumFeatures", default = -1, help="Used to keep top N features", type = int)
  parser.add_argument("-O", "--outputFile1", default = "output_labeled_1.csv", help="Set the output data file (Replicate 1)")
  parser.add_argument("-o", "--outputFile2", default = "output_labeled_2.csv", help="Set the output data file (Replicate 2)")
  args = parser.parse_args()

  multicharge_features_replicate_1 = MultiChargeFeatureList.get_multiCharge_features_evaluation(args.replicate1_file)
  sort_features(multicharge_features_replicate_1)
  shortlist_features_rep_1 = shortlist_features(multicharge_features_replicate_1, args.NumFeatures)
  
  multicharge_features_replicate_2 = MultiChargeFeatureList.get_multiCharge_features_evaluation(args.replicate2_file)
  sort_features(multicharge_features_replicate_2)
  shortlist_features_rep_2 = shortlist_features(multicharge_features_replicate_2, args.NumFeatures)
  
  

  common_features = get_common_features(shortlist_features_rep_1, shortlist_features_rep_2, args.tolerance, args.timeTolerance)
 
  label_features(common_features, [shortlist_features_rep_1, shortlist_features_rep_2])
  
  MultiChargeFeatureList.print_features(shortlist_features_rep_1, args.outputFile1)
  MultiChargeFeatureList.print_features(shortlist_features_rep_2, args.outputFile2)
  write_Combined_feature_detailed_10(common_features, [shortlist_features_rep_1, shortlist_features_rep_2], "common_features_detailed.txt")
  
  plot_distribution_combined(common_features, True)
