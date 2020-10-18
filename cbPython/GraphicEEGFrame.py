from __future__ import annotations
import json
from random import random
import numpy as np
# from EEGAnalysis import EEGAnalysis

class GraphicEEGFrame(object):
  """Convenience class for sending frame analysis information the frontend"""

  def __init__(self, num=0, start_time=0, electrode=None, values=None, analysis=None):
    super(GraphicEEGFrame, self).__init__()
    self._num = num
    self._values = values
    self._dict = {name:None for name in analysis._band_defs.keys()} # new dictionary with band names
    self._analysis = analysis

    if values is not None:
      self._populate_dict() # populate the dictionary with the right values

  def _populate_dict(self, rand=False):
    count = 0
    ###############################
    ## check to make sure that the bands are always returned in order!!
    ## UPDATE: This is true as of 3.6
    ###############################
    for key,defin in self._analysis._band_defs.items():
      freqs = self._analysis._fft_freqs[(self._analysis._fft_freqs>=defin[0]) & (self._analysis._fft_freqs<defin[1])] # get the frequencies
      self._dict[key] = []
      values = []
      for i in range(len(freqs)):
        if rand:
          r = random()
          values.append(r) # give a random value
          self._values.append(r)
        else:
          values.append(self._values[count])
          count += 1 # count it up
      result = np.array([freqs, values]).T # transpose the array
      for i,arr in enumerate(result):
        dic = {'x': arr[0], 'y': arr[1]}
        self._dict[key].append(dic)

  def _random(self):
    # for key,defin in self._analysis._band_defs.items():
    #   freqs = self._analysis._fft_freqs[(self._analysis._fft_freqs>=defin[0]) & (self._analysis._fft_freqs<defin[1])] # get the frequencies
    #   values = []
    #   self._dict[key] = []
    #   for i in range(len(freqs)):
    #     values.append(random()) # give a random value
    #   result = np.array([freqs, values]).T # transpose the array
    #   for i,arr in enumerate(result):
    #     dic = {'x': arr[0], 'y': arr[1]}
    #     self._dict[key].append(dic)
    self._values = []
    self._populate_dict(True)

    return self


  def _make_val_dict(self):
    self._dict = {
      'Delta': self._values[0],
      'Theta': self._values[1],
      'Alpha': self._values[2],
      'Beta': self._values[3],
      'Gamma': self._values[4],
    }

  def to_JSON(self, indent=None):
    return json.dumps(self._dict, indent=indent)

  def values():
      doc = "The values property."
      def fget(self):
          return self._values
      def fset(self, value):
          self._values = value
      def fdel(self):
          del self._values
      return locals()
  values = property(**values())

  def band_names():
      doc = "The band_names property."
      def fget(self):
          return self._band_names
      def fset(self, value):
          self._band_names = value
      def fdel(self):
          del self._band_names
      return locals()
  band_names = property(**band_names())

  @classmethod
  def random(cls, num=0, analysis=None):
    """
    Make and return random values for testing.
    """
    return cls(num=num, analysis=analysis)._random()
