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

from topfd.envelope.simple_peak import SimplePeak

def get_distr_entry_num(): return 11000
def get_distr_mass_interval(): return 10
def init_base_mass_idx(distr_entry_num, distr_mass_interval, envs):
  base_mass_idxes = [-1] * distr_entry_num
  for i in range(0, distr_entry_num):
    mz = envs[i].mono_mz
    idx = int(mz/distr_mass_interval)
    if idx >= 0 and idx < distr_entry_num:
      base_mass_idxes[idx] = i
  base_mass_idxes[0] = 0
  for i in range(1, distr_entry_num):
    if base_mass_idxes[i] < 0:
      base_mass_idxes[i] = base_mass_idxes[i - 1]
  return base_mass_idxes

class BaseEnvelope:
  def __init__(self, refer_idx, charge, mono_mz, peaks):
    self.refer_idx = refer_idx
    self.charge = charge
    self.mono_mz = mono_mz
    self.peaks = peaks

  @classmethod
  def get_envelope(cls, num, line_list):
    peaks = []
    intens = []
    for i in range(0, num):
      words = line_list[i+1].split(" ")
      mz = float(words[0])
      inte = float(words[1]) / 100
      intens.append(inte)
      peak = SimplePeak(mz, inte)
      peaks.append(peak)
    refer_idx = intens.index(max(intens))
    mono_mz = peaks[0].pos
    charge = 1
    envelope = cls(refer_idx, charge, mono_mz, peaks)
    return envelope
  
  def distrToTheoMono(self, new_mono_mz, new_charge):
    ori_charge = 1
    mass_diff = new_mono_mz * new_charge - self.mono_mz * ori_charge
    return self._convertToTheo(mass_diff, new_charge)
  
  def get_sub_envelope(self, percent_bound):
    self.peaks.sort(key = lambda x: x.inte, reverse=True)
    inte_sum = sum([i.inte for i in self.peaks])

    peak_sum = 0
    peak_idx = 0
    total_peaks = len(self.peaks)
    while (peak_sum / inte_sum < percent_bound):
      if peak_idx == total_peaks:
        break
      peak_sum = peak_sum + self.peaks[peak_idx].inte
      peak_idx = peak_idx + 1
     
    filtered_env_peaks = self.peaks[0:peak_idx]
    filtered_env_peaks.sort(key = lambda x: x.mz)
    self.peaks = filtered_env_peaks
  
  def _convertToTheo(self, mass_diff, new_charge):
    ori_charge = 1
    new_mono_mz = (self.mono_mz * ori_charge + mass_diff) / new_charge
    new_peaks = [0] * len(self.peaks)
    for i in range(0, len(self.peaks)):
      new_mz = (self.peaks[i].pos + mass_diff) / new_charge
      new_peaks[i] = SimplePeak(new_mz, self.peaks[i].inte)
    return BaseEnvelope(self.refer_idx, new_charge, new_mono_mz, new_peaks)
