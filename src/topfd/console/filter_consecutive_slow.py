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
    print("Filter peaks by consecutive peaks")
    input_fname = sys.argv[1]
    tolerance = float(sys.argv[2])
    output_fname = sys.argv[3]
    df = pd.read_csv(input_fname, sep = "\t")
    max_scan_id = np.max(df['scan_id'])
    print("Peak number", len(df), "max scan id", max_scan_id)
    
    result = pd.DataFrame(columns = df.columns)
    cur_scan_id = 0
    while cur_scan_id <= max_scan_id:
        print("cur_scan_id", cur_scan_id, "max_scan_id", max_scan_id)
        sele = df.loc[((df['scan_id'] >= cur_scan_id -1) & (df['scan_id'] <= cur_scan_id + 1))]
        
        sele.sort_values(by=['mz'])
        mz_list = sele['mz'].to_numpy()
        scan_id_list = sele['scan_id'].to_numpy()
        peak_num = len(sele)
        #print("peak_num", peak_num)
        cur_idx = 0
        low_idx = 0
        high_idx = 0
        while cur_idx < peak_num:
            if scan_id_list[cur_idx] != cur_scan_id:
                cur_idx = cur_idx + 1
                continue
            #update low_idx
            while low_idx < cur_idx:
                dist = mz_list[cur_idx] - mz_list[low_idx]
                if dist < tolerance:
                    break
                low_idx = low_idx + 1
            #update high_idx
            while high_idx < peak_num:
                dist = mz_list[high_idx] - mz_list[cur_idx]
                if dist > tolerance:
                    break
                high_idx = high_idx + 1
            match = False
            pt = low_idx
            while pt < high_idx:
                pt_id = scan_id_list[pt]
                if pt_id == cur_scan_id -1 or pt_id == cur_scan_id+1:
                    match = True
                    break
                pt = pt + 1
            if (match):
                result.loc[-1] = sele.iloc[cur_idx] 
                result.index = result.index + 1
        #    result.append(df.iloc[cur_idx], ignore_index=True)
        #else:
            #print("Not match", df.iloc[cur_idx])
            cur_idx = cur_idx + 1
        cur_scan_id = cur_scan_id + 1
    print("Filtered peak number", len(result))
    result.sort_values(['scan_id','mz'])
    result.to_csv(output_fname, sep="\t", index=False)
