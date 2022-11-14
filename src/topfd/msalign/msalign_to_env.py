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

import topfd.msalign.read_msalign as read_msalign
from topfd.envelope.seed_envelope import SeedEnvelope

def get_mz(mass, charge):
  proton = 1.00727
  return (mass + (charge * proton)) / charge
  
def get_mass(mz, charge):
  proton = 1.00727
  return (mz * charge) - (charge * proton)

def get_env_obj(env_base, mass, charge, intensity, spec_list, i, peak_id, percent_bound):
  mz = round(get_mz(mass, charge), 6)
  env = env_base.get_env_mono_mass(mass, charge, mz)
  if percent_bound < 1.0:
    print("percent_bound", percent_bound)
    env.get_sub_envelope(percent_bound)
  env_peaks_mz = [i.pos for i in env.peaks]
  env_peaks_inte = [i.inte for i in env.peaks]
  sp_peak = SeedEnvelope(i, peak_id, mz, mass, intensity, charge, env_peaks_mz, env_peaks_inte)
  return sp_peak

def is_exist(spec_envs, mass, ppm, min_tole):
  tole = mass * ppm/1000000
  if (tole < min_tole):
    tole = min_tole
  for env in spec_envs:
    env_mass = env.mass
    error = abs(env_mass - mass)
    if error <= tole:
      return True
    prev_mass = env_mass - env.get_isotope_mass() 
    error = abs(prev_mass - mass)
    if error <= tole:
      return True
    next_mass = env_mass + env.get_isotope_mass() 
    error = abs(next_mass - mass)
    if error <= tole:
      return True
  return False


def get_envelopes_from_msalign(msalign_file, env_base, percent_bound = 1.0):
  spec_list = read_msalign.read_spec_file(msalign_file)
  all_envs = []
  ppm = 15
  min_tole = 0.01
  for i in range(0, len(spec_list)):
    if i%500 == 0:
      print("Processing Spectrum:", i, "out of", len(spec_list)-1)
    peaklist = spec_list[i].peak_list
    peaklist.sort(key=lambda x: x.intensity, reverse=True)
    spec_envs = []
    for env_id in range(0, len(peaklist)):
      peak_data = peaklist[env_id]
      mass = peak_data.mass
      exist = is_exist(spec_envs, mass, ppm, min_tole)
      if not exist:
        sp_env = get_env_obj(env_base, mass, peak_data.charge, peak_data.intensity, spec_list, i, env_id, percent_bound)
        spec_envs.append(sp_env)
    all_envs.extend(spec_envs)
  all_envs.sort(key=lambda x: x.inte, reverse=True)
  return all_envs


def save_to_txt(all_envs, filename):
  file = open(filename, 'w+')
  for peak in all_envs:
    file.write("ENVELOPE_BEGIN \n")
    file.write("SPEC_ID: " + str(peak.spec_id) + "\n")
    file.write("ENV_ID: " + str(peak.env_id) + "\n")
    file.write("MZ: " + str(peak.pos) + "\n")
    file.write("MASS: " + str(peak.mass) + "\n")
    file.write("INTE: " + str(peak.inte) + "\n")
    file.write("CHARGE: " + str(peak.charge) + "\n")
    file.write("THEO_ENV: " + str(peak.get_pos_list()) + "\n")
    file.write("THEO_ENV_INTE: " + str(peak.get_inte_list()) + "\n")
    file.write("ENVELOPE_END \n\n")
  file.close()
