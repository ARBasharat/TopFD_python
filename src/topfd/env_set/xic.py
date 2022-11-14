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

import os
import numpy as np
import statistics
from scipy.signal import savgol_filter

class XIC:
  def __init__(self, start_spec_id, base_spec_id, inte_list, smoothed_inte_list = None): 
    self.__start_spec_id = start_spec_id
    self.__base_spec_id = base_spec_id
    self.__inte_list = inte_list
    if smoothed_inte_list is None:
      self.moving_avg(2)
    else:
      self.__smoothed_inte_list = smoothed_inte_list

  @property
  def start_spec_id(self): 
    return self.__start_spec_id

  @property
  def base_spec_id(self): 
    return self.__base_spec_id

  @property
  def inte_list(self): 
    return self.__inte_list

  @property
  def smoothed_inte_list(self): 
    return self.__smoothed_inte_list

  # def moving_avg(self, n):
  #   intes = self.inte_list
  #   # intes = self.xic.inte_list
  #   l = len(intes)
  #   padding_len = (n -1) // 2
  #   left_padding = [intes[0]] * padding_len
  #   right_padding = [intes[l-1]] * padding_len
  #   extend_intes = left_padding + intes + right_padding
  #   weights = np.ones(n)/n
  #   self.__smoothed_inte_list = np.convolve(extend_intes, weights, mode = "valid")

  def moving_avg(self, size):
    data = self.inte_list
    # data = self.xic.inte_list
    data.insert(0, 0)
    num_spec = len(data)
    sum_val = 0.0
    cnt = 0
    self.__smoothed_inte_list = []
    for i in range(0, num_spec):
      sum_val = sum_val + data[i]
      cnt = cnt + 1
      if (cnt >= size):
        self.__smoothed_inte_list.append(sum_val/size)
        sum_val = sum_val - data[cnt - size]
    data.pop(0)
