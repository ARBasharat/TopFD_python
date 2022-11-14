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

from topfd.envelope.simple_peak import SimplePeak
 
class ExpEnvelope:
  def __init__(self, spec_id, peak_list):
    self.__spec_id = spec_id
    self.__peak_list = peak_list 

  @property
  def peak_list(self): 
    return self.__peak_list

  @property
  def spec_id(self): 
    return self.__spec_id
  
  def get_peak_num(self):
    return len(self.peak_list)

  def get_match_peak_num(self):
    num = 0
    for p in self.__peak_list:
      if p is not None:
        num = num + 1
    return num

  def get_match_peak_num(self, base_idx):
    total_peaks = len(self.peak_list)
    start_idx = max(base_idx - 1, 0)
    end_idx = min(base_idx + 1, total_peaks - 1)
    num = 0
    for i in range(start_idx, end_idx):
      p = self.peak_list[i]
      if p is not None:
        num = num + 1
    return num

  def get_pos_list(self):
    pos_list = []
    for p in self.peak_list:
      if p is not None:
        pos_list.append(p.pos)
      else:
        pos_list.append(0)
    return pos_list

  def get_inte_list(self):
    inte_list = []
    for p in self.peak_list:
      if p is not None:
        inte_list.append(p.inte)
      else:
        inte_list.append(0)
    return inte_list

  def get_non_empty_pos_list(self):
    pos_list = []
    for p in self.peak_list:
      if p is not None:
        pos_list.append(p.pos)
    return pos_list

  def get_min_max_pos(self, min_pos, max_pos):
    pos_list = self.get_non_empty_pos_list()
    min_pos = min(pos_list)
    max_pos = max(pos_list)

