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

from topfd.envelope.seed_envelope import SeedEnvelope

def get_end_index(all_lines, begin_idx):
  idx = begin_idx
  while (idx < len(all_lines) and "ENVELOPE_END" not in all_lines[idx]):
    idx = idx + 1
  return idx

def parse_envelope(spec_lines):
  spec_id = -1
  peak_id = -1
  mono_mz = -1
  mono_mass = -1
  inte = -1
  charge = -1
  distribution = []
  distribution_inte = []
  
  for i in range(len(spec_lines)):
    line = spec_lines[i]
    split_txt = line.split(':')
    if("SPEC_ID" in line):
      spec_id = int(split_txt[1])
    if("PEAK_ID" in line):
      peak_id = int(split_txt[1])
    if("MZ" in line):
      mono_mz = float(split_txt[1])
    if("MASS" in line):
      mono_mass = float(split_txt[1])
    if("INTE" in line[0:4]):
      inte = float(split_txt[1])
    if("CHARGE" in line):
      charge = int(split_txt[1])
    if("THEO_ENV:" in line):
      data = split_txt[1].split('[')
      data = data[1].split(']')
      data = data[0].split(',')
      distribution = [float(i) for i in data]
    if("THEO_ENV_INTE" in line):
      data = split_txt[1].split('[')
      data = data[1].split(']')
      data = data[0].split(',')
      distribution_inte = [float(i) for i in data]
      
  seed_env = SeedEnvelope(spec_id, peak_id, mono_mz, mono_mass, inte, charge, distribution, distribution_inte)
  return seed_env

def read_env_file(env_file):
  file = open(env_file)
  all_lines = file.readlines()
  all_lines = [x.strip() for x in all_lines] 
  file.close()
    
  seed_envelopes = []
  begin_idx = 0
  while (begin_idx < len(all_lines)):
    end_idx = get_end_index(all_lines, begin_idx)
    env_lines = all_lines[begin_idx:end_idx +1]
    begin_idx = end_idx + 1
    if begin_idx >= len(all_lines):
      break
    seed_envelope = parse_envelope(env_lines)
    seed_envelopes.append(seed_envelope)
    
  seed_envelopes.sort(key=lambda x: x.inte, reverse=True)
  return seed_envelopes
