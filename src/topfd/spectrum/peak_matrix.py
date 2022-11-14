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
import topfd.spectrum.peak_row as peak_row
from topfd.util.noise_inten_util import compute_noise

class PeakMatrix:
  def __init__(self, df, bin_size):
    self.__df = df
    self.__peaks = []
    self.__min_mz = np.min(df['mz'])
    self.__max_mz = np.max(df['mz'])
    self.__min_inte = 0
    self.__spec_min_inte = 0
    self.__bin_size = bin_size
    self.__spec_num = np.max(self.__df['spec_id']) + 1
    self.__bin_num = int((self.__max_mz - self.__min_mz)/self.__bin_size) + 1
    self.get_noise_intensities()
    self.get_spec_list()
    self.init_matrix()

  def __len__(self):
    return len(self.__df.shape[0])
  
  @property
  def matrix(self): 
    return self.__matrix

  def peaks(self): 
    return self.__peaks

  def get_peak_num(self):
    return len(self.__peaks)

  @property
  def df(self): 
    return self.__df

  @property
  def bin_num(self): 
    return self.__bin_num

  @property
  def min_mz(self): 
    return self.__min_mz
  
  @property
  def max_mz(self): 
    return self.__max_mz

  @property
  def min_inte(self): 
    return self.__min_inte
  
  @property
  def spec_min_inte(self): 
    return self.__spec_min_inte

  @property
  def spec_num(self): 
    return self.__spec_num
  
  @property
  def specs(self): 
    return self.__specs
  
  def get_spec_list(self):
    spec_id = np.unique(self.df['spec_id'])
    scan_num = np.unique(self.df['scan_num'])
    rt = np.unique(self.df['retention_time'])
    spec_list = []
    for i in range(0, len(rt)):
      spec_list.append((spec_id[i], scan_num[i], rt[i]))
    self.__specs = spec_list
  
  def init_matrix(self):
    ## Initialize peak matrix
    peak_matrix = dict()
    for spec_id in range(self.__spec_num):
      if spec_id%500 == 0:
        print("Init matrix processing peaks in spectrum", spec_id, "out of", self.__spec_num)

      ## Fill the peak matrix
      spec_peak_list = self.__df.loc[(self.__df['spec_id'] == spec_id)].to_numpy()
      spec_rt = 0
      if len(spec_peak_list) > 0:
        peak = exp_peak.ExpPeak(0, spec_peak_list[0])
        spec_rt = peak.rt
        #print("rt", spec_rt)
      peak_matrix[spec_id] = peak_row.PeakRow(spec_id, spec_rt, self.__bin_num) 
      
      exp_peak_list = []
      for p in spec_peak_list:
        peak_id = len(self.__peaks)
        new_peak = exp_peak.ExpPeak(peak_id, p)
        #print(peak_id)
        exp_peak_list.append(new_peak)
        self.__peaks.append(new_peak)
      for cur_peak in exp_peak_list:
        bin_idx = self.get_index(cur_peak.pos)
        peak_matrix[spec_id].add_peak(bin_idx, cur_peak)
    self.__matrix = peak_matrix
    print("peak matrix size", len(self.__matrix), "peak num", len(self.__peaks))
    
  def get_noise_intensities(self):
    print("Compute Noise Intensity Levels!")
    #### Set the noise intensity to 300 --- ####################
    # peak_intens = self.df['intensity'].to_numpy()
    # noise_inte = compute_noise(peak_intens)
    # self.__min_inte = noise_inte
    self.__min_inte = 300
    ##########################
    spectrum_noise_levels = []
    for spec_id in range(self.spec_num):
      data = self.df.loc[(self.df['spec_id'] == spec_id)].to_numpy()
      intes = [i[4] for i in data]
      noise = compute_noise(intes)
      spectrum_noise_levels.append(noise)
    self.__spec_min_inte = spectrum_noise_levels

  def get_bin_peak(self, sp_id, peak_id):
    self.matrix[sp_id].getRowPeak(peak_id)

  def get_index(self, mz):
    mz_diff = mz - self.__min_mz
    bin_idx = int(mz_diff /self.__bin_size)
    return bin_idx

  def find_all_neighbors(self, mass_tol):
    search_bin_num = int(mass_tol/self.__bin_size) + 1 
    for spec_id in range(self.__spec_num - 1):
      cur_row = self.__matrix[spec_id]
      next_row = self.__matrix[spec_id+1]
      self.find_pair_neighbors(cur_row, next_row, search_bin_num, mass_tol)
  
  def find_pair_neighbors(self, first_row, second_row, search_bin_num, mass_tol):
    first_bin_list = first_row.row
    second_bin_list = second_row.row
    for bin_idx in range(self.__bin_num):
      start = max(0, bin_idx - search_bin_num)
      end = min(bin_idx + search_bin_num, self.__bin_num - 1)
      for first_peak in first_bin_list[bin_idx]:
        for second_idx in range(start, end + 1):
          for second_peak in second_bin_list[second_idx]:
            mass_diff = abs(first_peak.pos - second_peak.pos) 
            if mass_diff <= mass_tol:
              first_peak.set_neighbor(True)
              second_peak.set_neighbor(True)

  def write_peaks_with_neighbors(self, fname):
    peak_count = 0
    txt_file = open(fname, 'w')
    txt_file.write("spec_id" + "\t")
    txt_file.write("scan_num" + "\t")
    txt_file.write("retention_time" + "\t")
    txt_file.write("mz" + "\t")
    txt_file.write("intensity" + "\n")
    for p in self.__peaks:
      if p.neighbor:
        txt_file.write(str(int(p.spec_id)) + "\t")
        txt_file.write(str(int(p.scan_num)) + "\t")
        txt_file.write(str(p.rt) + "\t")
        txt_file.write(str(p.pos) + "\t")
        txt_file.write(str(p.inte) + "\n")
        peak_count = peak_count + 1
    txt_file.close()
    print("Write peaks with neighbors finished")
    print("peak number ", peak_count)

  def remove_peak(self, peak):
    spec_id = peak.spec_id
    bin_idx = self.get_index(peak.pos)
    bin_peaks = self.__matrix[spec_id].row[bin_idx]
    #print("size before removing", len(bin_peaks))
    for bin_peak in bin_peaks:
      if bin_peak.peak_id == peak.peak_id:
        bin_peaks.remove(bin_peak)
        #print("size after removing", len(self.__matrix[spec_id].row[bin_idx]))
        break
