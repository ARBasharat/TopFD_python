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

import numpy as np
import topfd.spectrum.exp_peak as exp_peak

class PeakRow:
  def __init__(self, spec_id, rt,  bin_num):
    self.__spec_id = spec_id
    self.__rt = rt
    self.__row = dict()
    for bin_idx in range(bin_num):
      self.__row[bin_idx] = []

  @property
  def row(self): 
    return self.__row

  @property
  def spec_id(self): 
    return self.__spec_id

  @property
  def rt(self): 
    return self.__rt

  def add_peak(self, idx, peak):
    self.__row[idx].append(peak)
    
  def getRowPeak(self, peak_id):
    return self.__row[peak_id]
