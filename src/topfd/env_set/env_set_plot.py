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

import matplotlib.pyplot as plt
import numpy as np

def plot_3d(x, y, z):
  fig, ax = plt.subplots(subplot_kw=dict(projection='3d'))
  ax.stem(x, y, z)
  plt.show()

def plot_xic(y1, y2):
  plt.plot(y1)
  plt.plot(y2)
  plt.show()
