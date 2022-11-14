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

class SimplePeak:
  def __init__(self, pos, inte ):
    self.__pos = pos
    self.__inte = inte
    self.__start_idx = -1
    self.__end_idx = -1

  @property
  def pos(self): 
    return self.__pos

  @property
  def inte(self): 
    return self.__inte

  @property
  def start_idx(self): 
    return self.__start_idx

  @property
  def end_idx(self): 
    return self.__end_idx

  def set_start_idx(self, start_idx):
    self.__start_idx = start_idx

  def set_end_idx(self, end_idx):
    self.__end_idx = end_idx

  def set_pos(self, pos):
    self.__pos = pos
