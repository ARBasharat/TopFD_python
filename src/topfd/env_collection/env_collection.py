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
import statistics

class EnvCollection():
  def __init__(self, seed_env, env_set_list, min_charge, max_charge,
      start_spec_id, end_spec_id):
    self.__seed_env = seed_env
    self.__env_set_list = env_set_list
    self.__min_charge = min_charge
    self.__max_charge = max_charge
    self.__start_spec_id = start_spec_id
    self.__end_spec_id = end_spec_id

  @property
  def min_charge(self): 
    return self.__min_charge

  @property
  def max_charge(self): 
    return self.__max_charge

  @property
  def start_spec_id(self): 
    return self.__start_spec_id

  @property
  def end_spec_id(self): 
    return self.__end_spec_id

  @property
  def seed_env(self): 
    return self.__seed_env
  
  @property
  def env_set_list(self): 
    return self.__env_set_list

  def get_mono_mass(self):
    return self.__seed_env.mass
  
  def get_refined_mono_mass(self):
    refined_mono_mass = []
    for env_set in self._EnvCollection__env_set_list:
      refined_mono_mass.append(env_set.get_refine_mono_mass())
    return statistics.mean(refined_mono_mass)
  
  def get_intensity(self, snr, noise_inte):
    inte = 0
    for env_set in self.__env_set_list:
      if env_set is not None:
        inte = inte + env_set.comp_intensity(snr, noise_inte)
    return inte
  
  def get_min_elution_time(self):
    return self.__env_set_list[0].exp_env_list[0].rt
  
  def get_max_elution_time(self):
    return self.__env_set_list[0].exp_env_list[-1].rt
  
  def get_apex_elution_time(self):
    seed_env_charge = self.seed_env.charge
    apex_rt = -1
    max_inte = -1
    for env_set in self.__env_set_list:
      if env_set.seed_env.charge == seed_env_charge:
        for exp_peak in env_set.exp_env_list:
          inte = sum([p.inte for p in exp_peak.peak_list if p is not None])
          if inte > max_inte:
            max_inte = inte
            apex_rt = exp_peak.rt
    return apex_rt
  
  def get_elution_length(self):
    return self.get_max_elution_time() - self.get_min_elution_time()
  
  def remove_matrix_peaks(self, peak_matrix):
    for env_set in self.__env_set_list:
      if env_set is not None:
        env_set.remove_matrix_peaks(peak_matrix)
        
  def refine_mono_mass(self):
    weight = 0
    weight_mz_error = 0
    for env_set in self.env_set_list:
      cur_weight, cur_weight_mz_error = env_set.get_weight_mz_error()
      weight = weight + cur_weight
      weight_mz_error = weight_mz_error + cur_weight_mz_error
    if weight > 0:
      mz_error = weight_mz_error / weight
      self.seed_env.shift(mz_error * self.seed_env.charge)
    else:
     print("ERROR 0 weight in refine_mono_mass")
     
  def get_seed_env_set(self):
    env_set = None
    for es in self.env_set_list:
      es_seed_env = es.seed_env
      if es_seed_env.charge == self.seed_env.charge:
        env_set = es
    return env_set
     
  def get_seed_theo_map(self, peak_matrix, snr):
    noise_inte = peak_matrix.min_inte
    env_set = self.get_seed_env_set()
    _map = env_set.get_map(snr, noise_inte)
    return _map

  def remove_peak_data(self, peak_matrix, snr):
    for env_set in self.__env_set_list:
      if env_set is not None:
        env_set.remove_peak_data(peak_matrix, snr)
  