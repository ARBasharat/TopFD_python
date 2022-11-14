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
import io
import pymzml
import pandas as pd

def mzML_to_txt(mzML_fname, txt_fname, MS_Level = 1, min_mz = 0, max_mz = 1000000):
  run = pymzml.run.Reader(mzML_fname, MS1_Precision = 5e-6, MSn_Precision = 20e-6, skip_chromatogram=True)
  spec_count = 0
  peak_count = 0
  txt_file = open(txt_fname, 'w')
  txt_file.write("spec_id" + "\t")
  txt_file.write("scan_num" + "\t")
  txt_file.write("retention_time" + "\t")
  txt_file.write("mz" + "\t")
  txt_file.write("intensity" + "\n")
  for s in run:
    if s.ms_level == MS_Level:
      spec_id = s.ID
      retention_time = s.get("scan start time")
      injection_time = s.get("ion injection time") 
      peaks = s.peaks("raw").tolist()
      peak_count = peak_count + len(peaks)
      for p in peaks:
        if p[0] >= min_mz and p[0] <= max_mz:
          txt_file.write(str(spec_count) + "\t")
          txt_file.write(str(s.ID) + "\t")
          txt_file.write(str(retention_time) + "\t")
          txt_file.write(str(p[0]) + "\t")
          txt_file.write(str(p[1]) + "\n")
      spec_count = spec_count + 1

  txt_file.close()
  print("mzML to txt conversion finished")
  print("spectrum number ", spec_count)
  print("peak number ", peak_count)
  
def mzML_to_df(mzML_fname, MS_Level = 1, min_mz = 0, max_mz = 1000000):
  run = pymzml.run.Reader(mzML_fname, MS1_Precision = 5e-6, MSn_Precision = 20e-6, skip_chromatogram=True)
  spec_count = 0
  peak_count = 0
  
  spec_id = []
  scan_num = []
  retention_time = []
  mz = []
  intensity = []
  for s in run:
    if s.ms_level == MS_Level:
      peaks = s.peaks("raw").tolist()
      peak_count = peak_count + len(peaks)
      for p in peaks:
        if p[0] >= min_mz and p[0] <= max_mz:
          spec_id.append(spec_count)
          scan_num.append(s.ID)
          retention_time.append(s.get("scan start time"))
          mz.append(p[0])
          intensity.append(p[1])
      spec_count = spec_count + 1
  
  d = {'spec_id': spec_id, 'scan_num': scan_num, 'retention_time': retention_time,
       'mz': mz, 'intensity': intensity}
  
  df = pd.DataFrame(d)
  print("spectrum number ", spec_count)
  print("peak number ", peak_count)
  return df
