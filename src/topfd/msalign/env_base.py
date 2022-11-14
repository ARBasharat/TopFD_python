# -*- coding: utf-8 -*-
"""
Created on Fri Feb 11 15:17:36 2022

@author: abbash
"""
# Copyright (c) 2014 - 2021, The Trustees of Indiana University.
##
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
##
# http://www.apache.org/licenses/LICENSE-2.0
##
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#!/usr/bin/python3

import topfd.msalign.env_base_util as env_base_utils

class EnvBase:
  def __init__(self, file_name, entry_num, mass_interval, envs, base_mass_idxes):
    self.file_name = file_name
    self.entry_num = entry_num  # number of distribution entries
    # the mass interval between two neighboring entries
    self.mass_interval = mass_interval
    self.envs = envs  # the list of distribution envelopes ## EnvelopePtrVec
    # mapping distribution envelopes to the mass value of base peak ## vector<int>
    self.base_mass_idxes = base_mass_idxes

  @classmethod
  def init_base(cls, theo_patt_file):
    f = open(theo_patt_file, "r")
    lines = f.readlines()
    f.close()

    distr_entry_num = env_base_utils.get_distr_entry_num()
    distr_mass_interval = env_base_utils.get_distr_mass_interval()
    envs = []
    for i in range(0, distr_entry_num):
      peak_num = 0
      line_list = []
      for idx in range(0, len(lines)):
        line = lines.pop(0)
        if line == "\n":
          break
        peak_num = peak_num + 1
        line_list.append(line)
      envs.append(env_base_utils.BaseEnvelope.get_envelope(peak_num - 1, line_list))
    env_base = cls(theo_patt_file, distr_entry_num,
                   distr_mass_interval, envs, None)
    return env_base
  
  def get_env_mono_mass(self, mass, charge, mz):
    idx = int(mass/self.mass_interval)
    if idx < 0:
      print("Invalid mass")
      return None
    if idx >= self.entry_num:
      print("mass out of bound")
      return None
    env = self.envs[idx]
    return env.distrToTheoMono(mz, charge)
    
  def get_env_base_mass(self, mass):
    distr_entry_num = env_base_utils.get_distr_entry_num()
    distr_mass_interval = env_base_utils.get_distr_mass_interval()
    base_mass_idxes = env_base_utils.init_base_mass_idx(distr_entry_num, distr_mass_interval, self.envs)
    idx = int(mass/self.mass_interval)
    if idx < 0:
      print("Invalid mass")
      return None
    if idx >= self.entry_num:
      print("mass out of bound")
      return None
    return self.envs[base_mass_idxes[idx]]
