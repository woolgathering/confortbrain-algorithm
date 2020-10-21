from __future__ import annotations
import json
from random import random
import numpy as np

class GraphicEEGFrame(object):
  """Convenience class for sending frame analysis information the frontend"""

  def __init__(self, num=0, name=None, values=None, analysis=None):
    super(GraphicEEGFrame, self).__init__()
    self._num = num
    self._values = values
    self._analysis = analysis
    self._dict = {name:None for name in analysis._band_defs.keys()} # new dictionary with band names

    if values is not None:
      self._populate_dict() # populate the dictionary with the right values


  def _populate_dict(self, rand=False):
    ###############################
    ## check to make sure that the bands are always returned in order!!
    ## UPDATE: This is true as of 3.6
    ###############################
    ## Can probably get higher performance if we just use the values in EEGElectrodeAnalysis.bands
    ## instead of reconstituting them here. Would require some rewriting
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
          idx = np.argwhere(self._analysis.fft_freqs==freqs[i])[0][0]
          values.append(self._values[idx])
      result = np.array([freqs, values]).T # transpose the array
      for i,arr in enumerate(result):
        dic = {'x': arr[0], 'y': arr[1]}
        self._dict[key].append(dic)

  def _random(self):
    self._values = []
    self._populate_dict(True)
    return self

  # not currently used but can be adapted in the future for better performance
  def _make_val_dict(self):
    pass
    # BEFORE: get frequencies of the bands to pair with the band, then transpose and put into a dictionary
    self._dict = {
      'Delta': parentEEGElectrodeAnalysis[num],
      'Theta': parentEEGElectrodeAnalysis[num],
      'Alpha': parentEEGElectrodeAnalysis[num],
      'Beta': parentEEGElectrodeAnalysis[num],
      'Gamma': parentEEGElectrodeAnalysis[num],
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

  def num():
      doc = "The zero indexed number of the window."
      def fget(self):
          return self._num
      def fset(self, value):
          self._num = value
      def fdel(self):
          del self._num
      return locals()
  num = property(**num())

  @classmethod
  def random(cls, num=0, analysis=None):
    """
    Make and return random values for testing.
    """
    return cls(num=num, analysis=analysis)._random()
