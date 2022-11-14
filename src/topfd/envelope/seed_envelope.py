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

import copy
from topfd.envelope.simple_peak import SimplePeak
 
class SeedEnvelope:
  def __init__(self, spec_id, env_id, pos, mass, inte, charge, pos_list, inte_list):
    self.spec_id = spec_id
    self.env_id = env_id
    self.pos = pos
    self.mass = mass
    self.inte = inte
    self.charge = charge
    self.peak_list = []
    for i in range(len(pos_list)):
      peak = SimplePeak(pos_list[i], inte_list[i])
      self.peak_list.append(peak)

  def get_pos_list(self):
    pos_list = []
    for p in self.peak_list:
      pos_list.append(p.pos)
    return pos_list

  def get_inte_list(self):
    inte_list = []
    for p in self.peak_list:
      inte_list.append(p.inte)
    return inte_list

  def get_peak_num(self):
    return len(self.peak_list)

  def rm_peaks(self, min_pos, max_pos):
    peak_list = []
    for p in self.peak_list:
      if p.pos >= min_pos and p.pos <= max_pos:
        peak_list.append(p)
    self.peak_list = peak_list

  def keep_top_three(self):
    self.peak_list.sort(key=lambda x: x.inte, reverse=True)
    self.peak_list = self.peak_list[0:3]
    self.peak_list.sort(key=lambda x: x.pos)

  def change_charge(self, new_charge):
    for peak in self.peak_list: 
      new_pos = (peak.pos - self.get_proton_mass()) * self.charge/ new_charge + self.get_proton_mass()
      peak.set_pos(new_pos)
    self.charge = new_charge

  def get_new_charge_env(self, new_charge):
    new_env = copy.deepcopy(self)
    new_env.change_charge(new_charge)
    return new_env

  def remove_low_inte_peaks(self, ratio, base_inte):
    peak_list = [] 
    for peak in self.peak_list:
      if (peak.inte * ratio >= base_inte):
        peak_list.append(peak)
    self.peak_list = peak_list
    
  def get_shifted_seed_envelope(self, env_base, shift_num):
    mass = self.mass + (shift_num * self.get_isotope_mass())
    mz = (mass + (self.charge * self.get_proton_mass())) / self.charge
    env = env_base.get_env_mono_mass(mass, self.charge, mz)
    env_peaks_mz = [i.pos for i in env.peaks]
    env_peaks_inte = [i.inte for i in env.peaks]
    sp_peak = SeedEnvelope(self.spec_id, self.env_id, mz, mass, self.inte, self.charge, env_peaks_mz, env_peaks_inte)
    return sp_peak

  def get_proton_mass(self):
    return 1.007276466879

  def get_isotope_mass(self):
    return 1.00235
  
  def shift(self, shift_num):
    shift_mass = shift_num * self.get_isotope_mass()
    shift_mz = shift_mass/self.charge
    self.pos = self.pos + shift_mz
    self.mass = self.mass + shift_mass
    for p in self.peak_list:
      p.set_pos(p.pos + shift_mz)
