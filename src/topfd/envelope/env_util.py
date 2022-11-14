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

def get_mz(mass, charge):
  proton = 1.00727
  return (mass + (charge * proton)) / charge
  
def get_mass(mz, charge):
  proton = 1.00727
  return (mz * charge) - (charge * proton)

def getExtendMasses(mass):
  IM = 1.00235
  extend_offsets_ = [0, -IM, IM]
  result = []
  for i in range(0, len(extend_offsets_)):
    new_mass = mass + extend_offsets_[i]
    result.append(new_mass)
  return result

def get_aggregate_envelopes_intensity(env_set):
  aggregate_inte = [0] * len(env_set.seed_env.peak_list)
  for spId in range(len(env_set.exp_env_list)):
    for peakIdx in range(0, len(aggregate_inte)):
      peak = env_set.exp_env_list[spId].peak_list[peakIdx] 
      if peak is not None:
        aggregate_inte[peakIdx] = aggregate_inte[peakIdx] + peak.inte
  return aggregate_inte

def get_aggregate_envelopes_mz(env_set):
  aggregate_mz = [0] * len(env_set.seed_env.peak_list)
  for peakIdx in range(0, len(aggregate_mz)):
    counter = 0
    for spId in range(len(env_set.exp_env_list)):
      peak = env_set.exp_env_list[spId].peak_list[peakIdx] 
      if peak is not None:
        aggregate_mz[peakIdx] = aggregate_mz[peakIdx] + peak.pos
        counter = counter + 1
    if counter > 0:
      aggregate_mz[peakIdx] = aggregate_mz[peakIdx]/counter
  return aggregate_mz

def calcInteRatio_scan(theo_envelope_inte, exp_envelope_inte):
  theo_sum = 0
  obs_sum = 0
  refer_idx = theo_envelope_inte.index(max(theo_envelope_inte))
  theo_sum = theo_sum + theo_envelope_inte[refer_idx]
  obs_sum = obs_sum + exp_envelope_inte[refer_idx]
  if (refer_idx - 1 >= 0):
    theo_sum = theo_sum + theo_envelope_inte[refer_idx - 1]
    obs_sum = obs_sum + exp_envelope_inte[refer_idx - 1]
  if (refer_idx + 1 < len(theo_envelope_inte)):
    theo_sum = theo_sum + theo_envelope_inte[refer_idx + 1]
    obs_sum = obs_sum + exp_envelope_inte[refer_idx - 1]
  if (theo_sum == 0):
    return 1.0
  elif (obs_sum == 0):
    return 1.0
  else:
    return obs_sum / theo_sum



