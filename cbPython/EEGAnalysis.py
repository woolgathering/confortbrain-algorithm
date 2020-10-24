import json
import os
import mne
import numpy as np
from random import random
from cbPython.GraphicEEGFrame import GraphicEEGFrame
from cbPython.EEGElectrodeAnalysis import EEGElectrodeAnalysis

class EEGAnalysis(object):
  """Actually processes the data from a file.

  Usage:
    data_path = './data/test_data.txt'
    a = EEGAnalysis(data_path, overlap=0.5, sr=200, win_size=400)
    a.process()
    a.write_JSON('./data/test_data_ANALYZED.json')
  """

  def __init__(self, file, overlap=0.5, sr=200, win_size=400, electrode_order=None):
    super(EEGAnalysis, self).__init__()
    self._file = file
    self._win_size = win_size
    self._overlap = overlap
    self._band_defs = {
      'Delta': (0.3, 4),
      'Theta': (4, 8),
      'Alpha': (8, 12),
      'Beta': (12, 16),
      'Gamma': (16, 20)
    } # name: (minHz, maxHz)
    self._fft_freqs = np.fft.rfftfreq(win_size, 1/sr) # the freqs of the bins
    self._sr = sr # samplerate
    self._window = np.hamming(win_size) # the window
    if electrode_order is None:
      self._electrode_order = ['Fp1', 'Fp2', 'F7', 'F3', 'FZ', 'F4', 'F8', 'T7', 'C3', 'CZ', 'C4', 'T8', 'P7', 'P3', 'Pz', 'P4'] # 10-20 electrodes
    else:
      self._electrode_order = electrode_order

    self._set_defaults() # set other attributes to None

    # read the data if this is not a random analysis
    if file is not None:
      self._read_data() # read the data in
      self._check_data_mismatch() # check for data channel mismatch


  def _set_defaults(self):
    self._frames = None
    self._electrodes = None

  def _check_data_mismatch(self):
    if len(self._electrode_order) != len(self._data):
      raise TypeError('Number of channels in data do not match number of electrodes: {} != {}'.format(len(self._electrode_order), len(self._data)))
    tss = 0
    for e in self._data:
      tss += len(e)
    if tss != (len(self._data)*len(self._data[0])):
      raise TypeError('Sample mismatch: one or more channels has missing samples.')

  def _read_data(self):
    name, ext = os.path.splitext(self._file)
    ext = ext.lower() # make it lowercase
    supported_filetypes = ['.txt', '.edf'] # supported filetypes
    if ext in supported_filetypes:
      if ext == '.txt':
        self._read_txt()
      elif ext == '.edf':
        self._read_edf()
    else:
      raise TypeError('Not supported filetype: \'{}\''.format(ext))

  def _read_txt(self):
    data = []
    # this will work with any textfile that is space delimted, even when it's inconsistent
    # in terms of the number of spaces
    with open(self._file) as f:
      for i, l in enumerate(f):
        l = l.split(' ')
        arr = []
        for string in l:
          try:
            value = float(string)
            arr.append(value)
          except ValueError:
            pass
        data.append(arr) # append the samples to the data
    self._data = np.array(data).T # make it an np array and transpose it

  def _read_edf(self):
    edf = mne.io.read_raw_edf(self._file, preload=True, verbose=0) # load the file
    self._electrode_order = edf.ch_names # a list of channel names
    self._data = edf.get_data() # get everything for now
    self._sr = edf.info['sfreq'] # samplerate
    self._win_size = int(self._sr*2) # default to an epoch of 2 seconds
    self._edf_info = edf.info # save the info for now
    edf.close() # close it

  def _interpolate(self, bin1, bin2):
    # interpoalte between bins to get freqs between bins
    pass

  # where math-magic happens
  # arrays which are less than the win_size due to not integer iterations are zero-padded
  def process(self):
    advance = int(self._win_size * self._overlap) # advance in samples
    iter = int(len(self._data[0]) / advance)
    self._frames = np.zeros((len(self._data), iter, len(self._fft_freqs))) # initialize space for the magnitudes
    self.electrodes = {}
    for i,e in enumerate(self._data):
      # e is a timeseries from a single electrode
      for j in range(iter):
        start = j*advance
        stop = start+self._win_size
        win = e[start:stop] # get the data
        win = np.pad(win, (0, self._win_size-len(win))) * self._window # pad the data and window it
        mags = np.abs(np.fft.rfft(win)/self._win_size) # analyze and rescale
        self._frames[i][j] = mags # remember all the freqs for now (memory savings to be had...)

      self.electrodes[self._electrode_order[i]] = EEGElectrodeAnalysis(self._electrode_order[i], self._frames[i], self)

  def _collect_to_bands(self):
    if self._frames is None:
      raise ValueError('Analysis has not been run (frames are empty)')

  # write a huge JSON file of the entire analysis
  def write_JSON(self, json_path, indent=None):
    file = open(json_path, 'w')
    file.write('{\n') # opening {
    for name,electrode in self._electrodes.items():
      file.write('\"{}\": '.format(name)) # name of the electrode
      file.write('{\n') # opening {
      for i,f in enumerate(electrode.graphic_frames):
        file.write('\"{}\": '.format(i)) # number of the electode
        file.write(f.to_JSON(indent)) # write the actual data from the frame
        if i<(len(electrode.graphic_frames)-1):
          file.write(',\n')
        else:
          file.write('\n')
      file.write('},\n') # closing }. Leaves a trailing comma for now
    file.write('}') # closing }
    file.close()



  ################################
  ## Properties
  ################################
  def fft_freqs():
      doc = "The fft_freqs property."
      def fget(self):
          return self._fft_freqs
      def fset(self, value):
          self._fft_freqs = value
      return locals()
  fft_freqs = property(**fft_freqs())

  def frames():
      doc = "The frames property."
      def fget(self):
          return self._frames
      def fset(self, value):
          self._frames = value
      return locals()
  frames = property(**frames())

  def electrode_order():
      doc = "The electrode_order property."
      def fget(self):
          return self._electrode_order
      def fset(self, value):
          self._electrode_order = value
      return locals()
  electrode_order = property(**electrode_order())

  def sr():
      doc = "The sr property."
      def fget(self):
          return self._sr
      def fset(self, value):
          self._sr = value
      return locals()
  sr = property(**sr())

  def overlap():
      doc = "The overlap property."
      def fget(self):
          return self._overlap
      def fset(self, value):
          self._overlap = value
      return locals()
  overlap = property(**overlap())

  def win_size():
      doc = "The win_size property."
      def fget(self):
          return self._win_size
      def fset(self, value):
          self._win_size = value
      return locals()
  win_size = property(**win_size())

  def data():
      doc = "The actual data, organized in the shape (num_electrodes, num_samples)."
      def fget(self):
          return self._data
      def fset(self, value):
          self._data = value
      return locals()
  data = property(**data())

  def band_defs():
      doc = "The _band_defs property."
      def fget(self):
          return self._band_defs
      def fset(self, value):
          self._band_defs = value
      return locals()
  band_defs = property(**band_defs())

  def electrodes():
      doc = "The electrodes property."
      def fget(self):
          return self._electrodes
      def fset(self, value):
          self._electrodes = value
      return locals()
  electrodes = property(**electrodes())

  def window():
      doc = "The window property."
      def fget(self):
          return self._window
      def fset(self, value):
          self._window = value
      return locals()
  window = property(**window())

  @classmethod
  def random(cls, num_frames=100, sr=200, win_size=400):
    analysis = cls(None)
    analysis._electrodes = {name:EEGElectrodeAnalysis.random(name, num_frames, analysis) for name in analysis._electrode_order}
    return analysis
