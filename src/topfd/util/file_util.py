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

import os
import pickle

def create_directory(base_direc, target_directory_name):
  target_directory = os.path.join(base_direc, target_directory_name)
  if not os.path.exists(target_directory ):
    os.mkdir(target_directory )
  return target_directory

def save_object(obj, filename):
  print("output filename", filename)
  with open(filename, 'wb') as output:
    pickle.dump(obj, output, -1)

def load_pickle_file_data(filename):
  with open(filename, 'rb') as pickle_file:
    return pickle.load(pickle_file)


