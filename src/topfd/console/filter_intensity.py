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

if __name__ == "__main__":
    print("Filter peaks by intensities")
    input_fname = sys.argv[1]
    df = pd.read_csv(input_fname, sep = "\t")
    print("Peak number", len(df))
    inte = df['intensity'].to_numpy()
    best_bin_cnt = len(df)
    best_bin_min = np.min(inte)
    best_bin_max = np.max(inte)
    while best_bin_cnt > 100:
        hist = np.histogram(inte)
        best_bin_idx = np.argmax(hist[0])
        best_bin_cnt = hist[0][best_bin_idx]
        best_bin_min = hist[1][best_bin_idx]
        best_bin_max = hist[1][best_bin_idx+1]
        new_inte = []
        print(best_bin_idx, best_bin_min, best_bin_max)
        for item in inte:
            if item >= best_bin_min and item <= best_bin_max:
                new_inte.append(item)
        print("new intensity size", len(new_inte))
        inte = new_inte
    cutoff = (best_bin_min + best_bin_max)/2
    sn_ratio = float(sys.argv[2])
    print("cutoff", cutoff, "sn_ratio", sn_ratio)
    cutoff = cutoff * sn_ratio 
    df = df.drop(df[df.intensity < cutoff].index)
    print("Peak number after filtering", len(df))

    output_fname = sys.argv[3]
    df.to_csv(output_fname, sep="\t", index=False)
    #np_data = df.to_numpy()
    #file_header = "scan_id" + "\t" + "scan_num" + "\t" + "retention_time" + "\t" + "mz" + "\t" + "intensity"
    #np.savetxt(output_fname, np_data, delimiter = "\t", header = file_header)
