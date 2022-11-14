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

import pymzml

class IntvDens:
  def __init__(self, bgn, end, num, perc):
    self.bgn = bgn
    self.end = end
    self.num = num
    self.perc = perc

def get_noise_intensity(mzML_file):
  print("Computing Noise intensity level ...")
  experimental_data = pymzml.run.Reader(mzML_file, MS1_Precision = 5e-6, MSn_Precision = 20e-6, skip_chromatogram=True)
  inte = []
  mass = []
  for s in experimental_data:
    if s.ms_level == 1:
      peaks = s.peaks("raw").tolist()
      temp_mass = [p[0] for p in peaks]
      temp_inte = [p[1] for p in peaks]
      inte.extend(temp_inte)
      mass.extend(temp_mass)
  noise_intensity = compute_noise(inte)
  return noise_intensity

def compute_noise(inte):
  inte = sorted(inte, reverse = False)
  max_inte = inte[-1]
  min_inte = inte[0]
  max_pos = -1
  dens = []
  while True:
    dens = get_density(inte, max_inte, min_inte)
    max_pos = get_max_position(dens)
    # print(max_pos, max_inte, min_inte)
    if (max_pos == 0):
      max_inte = dens[max_pos].end
    if (max_pos > 0):
      break
  return (dens[max_pos].end + dens[max_pos].bgn) / 2


    
def get_density(inte, max_inte, min_inte):
  intv_width = 10
  if (max_inte > 10000):
    intv_width = max_inte / 1000
  elif (max_inte < 100):
    intv_width = max_inte / 100
  
  total_num = len(inte)
  intv_num = int(max_inte / intv_width) + 1
  dens = []
  for i in range(0, intv_num):
    bgn = i * intv_width
    end = (i + 1) * intv_width
    num = sum(1 for j in inte if bgn < j <= end)
    cur_den = IntvDens(bgn, end, num, num / total_num)
    dens.append(cur_den)
  return dens

    
# def get_density(inte, max_inte, min_inte):
#   intv_width = 10
#   if (max_inte > 10000):
#     intv_width = max_inte / 1000
#   elif (max_inte < 100):
#     intv_width = max_inte / 100
  
#   intv_inte = min_inte + 10*intv_width
#   last_idx = binary_search(inte, intv_inte)
#   inte_window = inte[0:last_idx]
  
#   total_num = len(inte)
#   intv_num = round(max_inte / intv_width) + 1
#   dens = []
#   # counter = 0
#   for i in range(0, intv_num):
#     bgn = i * intv_width
#     end = (i + 1) * intv_width
#     # if end < min_inte:
#     #   continue  
#     num = sum(1 for j in inte_window if bgn < j <= end)
#     cur_den = IntvDens(bgn, end, num, num / total_num)
#     dens.append(cur_den)
#     # counter = counter + 1
#     # if counter == 5:
#     #   break
#   return dens

def get_max_position(dens):
  max_pos = -1;
  max_num = -1;
  for i in range(0, len(dens)):
    if (dens[i].num > max_num):
      max_num = dens[i].num
      max_pos = i
  return max_pos

def binary_search(inte, max_inte):
  low = 0
  mid = 0
  high = len(inte) - 1
  while low <= high:
    mid = (high + low) // 2
    if inte[mid] < max_inte:
      low = mid + 1
    elif inte[mid] > max_inte:
      high = mid - 1
  return low