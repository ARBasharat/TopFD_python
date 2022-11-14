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
# sys.path.insert(0, r"C:\Users\Abdul\Documents\GitHub\MS_Feature_Extraction_xwliu\src")

import topfd.util.file_util as util
from topfd.console.get_feature import output_env_coll_list

def check_in_existing_features(feature_list, feature, match_envelope_tolerance, retention_time_overlap):
  featureList_charge_states = [env_set.seed_env.charge for env_set in feature.env_set_list]
  mass_tol = match_envelope_tolerance * feature.seed_env.mass
  IM = 1.00235
  extend_offsets_ = [0, -IM, IM, -2*IM, 2*IM]
  extended_masses = []
  for i in range(0, len(extend_offsets_)):
    new_mass = feature.seed_env.mass + extend_offsets_[i]
    extended_masses.append(new_mass)
  
  ### RT OVERLAPPPPP
  selected_features = []
  for i in range(0, len(feature_list)):
    if feature_list[i] is None:
      continue
    if _check_overlap(feature_list[i], feature, retention_time_overlap):
      min_mass_diff = min([abs(ext_mass - feature_list[i].seed_env.mass) for ext_mass in extended_masses])
      if min_mass_diff < mass_tol:
        selected_features.append(i)
        
  for f_idx in selected_features:
    f = feature_list[f_idx]
    parent_charge_states = [env_set.seed_env.charge for env_set in f.env_set_list]
    status = True
    for charge_state in featureList_charge_states:
      ## if charge state reported; dont merge
      if charge_state in parent_charge_states:
        status = False
      ## if charge state is more than 2 charges away; dont report
      min_charge_diff = 10000000
      for parent_charge_state in parent_charge_states:
        charge_diff = abs(charge_state - parent_charge_state)
        if charge_diff < min_charge_diff:
          min_charge_diff = charge_diff
      if min_charge_diff > 2:
        status = False
    if status:
      for env_set in feature.env_set_list:
        f.env_set_list.append(env_set)
      print("Feature with charge states", featureList_charge_states,"merged to Feature", selected_features[0], "with mass",  feature_list[selected_features[0]].seed_env.mass, "to obtain charge states:", [env_set.seed_env.charge for env_set in feature_list[selected_features[0]].env_set_list])
      return True
  return False

def _check_overlap(f, feature, time_tol):
  start_spec_id = f.start_spec_id
  end_spec_id = f.end_spec_id
  
  start = -1
  if start_spec_id <= feature.start_spec_id:
    ## f start before feature starts 
    start = feature.start_spec_id
  else:
    ## f start after feature starts 
    start = start_spec_id

  end = -1  
  if start > -1:
    if end_spec_id <= feature.end_spec_id:
      ## f ends before feature ends
      end = end_spec_id
    else:
      ## f ends after feature ends
      end = feature.end_spec_id

  status = False
  if end > - 1:
    overlapping_rt_range = end - start
    if overlapping_rt_range > 0:
      feature_rt_range = feature.end_spec_id - feature.start_spec_id
      feature_coverage = feature_rt_range/overlapping_rt_range
      if feature_coverage > time_tol: ## 80% coverage
        status = True
  return status

in_fname = sys.argv[1]
# in_fname = r"C:\Users\Abdul\Documents\GitHub\test_data_xwliu\Rep_2\out_v1.pkl"
output_fname = in_fname.split('.')[0] + "_charge_combined.csv"

print("Filenames:", in_fname, output_fname)
env_coll_list = util.load_pickle_file_data(in_fname)
match_envelope_tolerance = 10E-6
retention_time_overlap = 0.8

for env_col_idx in range(1, len(env_coll_list)):
  feature = env_coll_list[env_col_idx]
  feature_list = env_coll_list[0:env_col_idx+1]
  status = check_in_existing_features(feature_list, feature, match_envelope_tolerance, retention_time_overlap)
  if status:
    env_coll_list[env_col_idx] = None

shortlisted_env_collections = [i for i in env_coll_list if i is not None]    
print("Orginal envelope collections number", len(env_coll_list), "and env collection number", len(shortlisted_env_collections))

output_env_coll_list(output_fname, shortlisted_env_collections)
util.save_object(shortlisted_env_collections, output_fname.split(',')[0] + '.pkl')
