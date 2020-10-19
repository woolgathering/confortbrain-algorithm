import json
import numpy as np
from random import random
from GraphicEEGFrame import GraphicEEGFrame
from cbPython.EEGElectrodeAnalysis import EEGElectrodeAnalysis

class EEGAnalysis(object):
  """Actually processes the data from a file."""

  def __init__(self, file, overlap=0.5, sr=200, win_size=400, electrode_order=None):
    super(EEGAnalysis, self).__init__()
    self._file = file
    self._win_size = win_size
    self._overlap = overlap
    self._band_defs = {
      'Delta': (0.3, 2),
      'Theta': (6, 8),
      'Alpha': (8, 12),
      'Beta': (12, 16),
      'Gamma': (16, 20)
    } # name: (minHz, maxHz)
    self._fft_freqs = np.fft.rfftfreq(win_size, 1/sr) # the freqs of the bins

    if sr is not None:
      self._sr = sr
    if electrode_order is None:
      self._electrode_order = ['Fp1', 'Fp2', 'F7', 'F3', 'FZ', 'F4', 'F8', 'T7', 'C3', 'CZ', 'C4', 'T8', 'P7', 'P3', 'Pz', 'P4', 'P8', 'O1', 'O2'] # 10-20 electrodes
    else:
      self._electrode_order = electrode_order


  def _get_data(self):
    # get the data from the file
    pass

  def _interpolate(self, bin1, bin2):
    # interpoalte between bins to get freqs between bins
    pass

  def write_JSON(self, json_path, indent):
    file = open(path, 'w')
    file.write('{\n')
    for name,electrode in analysis.electrodes.items():
      file.write('\"{}\": '.format(name))
      file.write('{\n')
      for i,f in enumerate(electrode.graphic_frames):
        file.write('\"{}\": '.format(i))
        file.write(f.to_JSON(indent))
        if i<(len(electrode.graphic_frames)-1):
          file.write(',\n')
        else:
          file.write('\n')
      file.write('},\n') # leaves a trailing comma for now

    file.write('}')
    file.close()



  ################################
  ## Properties
  ################################
  def frames():
      doc = "The frames property."
      def fget(self):
          return self._frames
      def fset(self, value):
          self._frames = value
      def fdel(self):
          del self._frames
      return locals()
  frames = property(**frames())

  def graphic_frames():
      doc = "The graphic_frames property."
      def fget(self):
          return self._graphic_frames
      def fset(self, value):
          self._graphic_frames = value
      def fdel(self):
          del self._graphic_frames
      return locals()
  graphic_frames = property(**graphic_frames())

  def electrode_order():
      doc = "The electrode_order property."
      def fget(self):
          return self._electrode_order
      def fset(self, value):
          self._electrode_order = value
      def fdel(self):
          del self._electrode_order
      return locals()
  electrode_order = property(**electrode_order())

  def sr():
      doc = "The sr property."
      def fget(self):
          return self._sr
      def fset(self, value):
          self._sr = value
      def fdel(self):
          del self._sr
      return locals()
  sr = property(**sr())

  def overlap():
      doc = "The overlap property."
      def fget(self):
          return self._overlap
      def fset(self, value):
          self._overlap = value
      def fdel(self):
          del self._overlap
      return locals()
  overlap = property(**overlap())

  def win_size():
      doc = "The win_size property."
      def fget(self):
          return self._win_size
      def fset(self, value):
          self._win_size = value
      def fdel(self):
          del self._win_size
      return locals()
  win_size = property(**win_size())

  def data():
      doc = "The data property."
      def fget(self):
          return self._data
      def fset(self, value):
          self._data = value
      def fdel(self):
          del self._data
      return locals()
  data = property(**data())

  def _band_defs():
      doc = "The _band_defs property."
      def fget(self):
          return self.__band_defs
      def fset(self, value):
          self.__band_defs = value
      def fdel(self):
          del self.__band_defs
      return locals()
  _band_defs = property(**_band_defs())

  def electrodes():
      doc = "The electrodes property."
      def fget(self):
          return self._electrodes
      def fset(self, value):
          self._electrodes = value
      def fdel(self):
          del self._electrodes
      return locals()
  electrodes = property(**electrodes())

  @classmethod
  def random(cls, num_frames=100, sr=200, win_size=400):
    analysis = cls(None)
    analysis._electrodes = {name:EEGElectrodeAnalysis.random(name, num_frames, analysis) for name in analysis._electrode_order}

    # graphic_frames = []
    # frames = []
    # for i in range(num_frames):
    #   g_rand = GraphicEEGFrame.random(i, analysis)
    #   frames.append(g_rand.values)
    #   graphic_frames.append(g_rand)
    #
    # analysis._graphic_frames = graphic_frames # just set it once. More memory but fine for now
    # analysis._frames = np.array(frames) # keep things consistent, even if they're random
    return analysis
