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


import sys
from topfd.preprocess.mzml_to_txt import mzML_to_txt

if __name__ == "__main__":
  print("Convert ms1 in an mzML file to a txt file.")
  mzML_fname = sys.argv[1]
  txt_fname = sys.argv[2]
  mzML_to_txt(mzML_fname, txt_fname)
