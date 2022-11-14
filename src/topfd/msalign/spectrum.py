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

class SpecHeader:
  def __init__(self, spec_id, spec_scan, retention_time, 
               activation, ms_one_id, ms_one_scan, mono_mz, 
               charge, mono_mass, inte, base_inte):
    self.spec_id = spec_id
    self.spec_scan = spec_scan
    self.retention_time = retention_time
    self.activation = activation
    self.ms_one_id = ms_one_id
    self.ms_one_scan = ms_one_scan
    self.mono_mz = mono_mz
    self.charge = charge
    self.mono_mass = mono_mass
    self.inte = inte
    self.base_inte = base_inte
  
  @classmethod
  def get_header(cls, spec_id, spec_scan, retention_time, 
               activation, ms_one_id, ms_one_scan, mono_mz, 
               charge, mono_mass, inte, base_inte):
    return cls(spec_id, spec_scan, retention_time, 
               activation, ms_one_id, ms_one_scan, mono_mz, 
               charge, mono_mass, inte, base_inte)
  
class SpecPeak:
  def __init__(self, mass, intensity, charge, distribution, distribution_inte):
    self.mass = mass
    self.intensity = intensity
    self.charge = charge
    self.distribution = distribution
    self.distribution_inte = distribution_inte
    
  @classmethod
  def get_peak(cls, mass, intensity, charge):
    distribution = None
    distribution_inte = None
    return cls(mass, intensity, charge, distribution, distribution_inte)

class Spectrum:
  def __init__(self, header, peak_list):
    self.header = header
    self.peak_list = peak_list

  @classmethod
  def get_spec(cls, header, peak_list):
    return cls(header, peak_list)
