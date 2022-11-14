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

class ExpPeak:
  def __init__(self, peak_id, peak):
    self.__peak_id = peak_id
    self.__spec_id = peak[0]
    self.__scan_num = peak[1]
    self.__rt = peak[2]
    self.__pos = peak[3]
    self.__inte = peak[4]
    self.__ori_inte = peak[4]
    #self.__start_idx = -1
    #self.__end_idx = -1
    self.__neighbor = False

  @property
  def peak_id(self): 
    return self.__peak_id

  @property
  def spec_id(self): 
    return self.__spec_id

  @property
  def scan_num(self): 
    return self.__scan_num

  @property
  def rt(self): 
    return self.__rt

  @property
  def pos(self): 
    return self.__pos

  @property
  def inte(self): 
    return self.__inte

  @property
  def rt(self): 
    return self.__rt

  @property
  def neighbor(self): 
    return self.__neighbor
  
  def set_neighbor(self, neighbor): 
    self.__neighbor = neighbor

  def set_pos(self, pos): 
    self.__pos = pos
    
  def set_inte(self, inte): 
    self.__inte = inte

  def set_start_idx(self, start_idx):
    self.__start_idx = start_idx

  def set_end_idx(self, end_idx):
    self.__end_idx = end_idx
