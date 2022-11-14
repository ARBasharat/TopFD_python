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

#!/usr/bin/python3

import sys
import numpy as np
import pandas as pd
import topfd.spectrum_new.peak_matrix as pm

if __name__ == "__main__":
  print("Filter peaks by consecutive peaks")
  input_fname = sys.argv[1]
  neighbor_mass_tole = float(sys.argv[2])
  bin_size = 0.1
  output_fname = sys.argv[3]
  df = pd.read_csv(input_fname, sep = "\t")
  max_spec_id = np.max(df['spec_id'])
  print("bin size", bin_size, "neighbor mass tolerance", neighbor_mass_tole)
  print("Peak number", len(df), "max spec id", max_spec_id)

  peak_matrix = pm.PeakMatrix(df, bin_size)
  peak_matrix.find_all_neighbors(neighbor_mass_tole)
  peak_matrix.write_peaks_with_neighbors(output_fname)
