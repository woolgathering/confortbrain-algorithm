import os
import mne
import numpy as np
from sklearn.decomposition import FastICA
from cbPython.GraphicEEGFrame import GraphicEEGFrame
from cbPython.EEGElectrodeAnalysis import EEGElectrodeAnalysis

class EEGAnalysis(object):
  """Actually processes the data from a file.

  Usage:
    data_path = './data/test_data.txt'
    a = EEGAnalysis(data_path, overlap=0.5, sr=200, win_size=400)
    a.process_spectral(epoch=2, overlap=0.5, ica=True)
    a.write_JSON('./data/test_data_ANALYZED.json')

  Also works with EDF and EDF+ files.
  """

  def __init__(self, file, sr=200, electrode_order=None):
    super(EEGAnalysis, self).__init__()
    self._file = file
    self._band_defs = {
      'Delta': (0.3, 4),
      'Theta': (4, 8),
      'Alpha': (8, 12),
      'Beta': (12, 16),
      'Gamma': (16, 20)
    } # name: (minHz, maxHz)
    self._sr = sr # samplerate
    if electrode_order is None:
      self._electrode_order = ['Fp1', 'Fp2', 'F3', 'F4', 'C3', 'C4', 'P3', 'P4', 'O1', 'O2', 'F7', 'F8', 'T3', 'T4', 'T5', 'T6'] # default order from Dr. Moises Aguilar
    else:
      self._electrode_order = electrode_order

    self._set_defaults() # set other attributes to None
    self._ica_done = False # ICA has not been performed yet
    self._verbose = 0 # no verbosity

    # read the data if this is not a random analysis
    if file is not None:
      self._read_data() # read the data in
      self._validate_data() # check for data channel mismatch

  def _set_defaults(self):
    self._frames = None
    self._electrodes = None

  def _validate_data(self):
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
    """
    This will work with any textfile that is space delimted, even when it's inconsistent
    in terms of the number of spaces.
    """
    data = []
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
    self._make_raw(self._data)

  def _read_edf(self):
    edf = mne.io.read_raw_edf(self._file, preload=True, verbose=self._verbose) # load the file
    self._raw = edf # keep the raw instance
    self._electrode_order = edf.ch_names # a list of channel names
    self._data = edf.get_data() # get everything for now
    self._sr = edf.info['sfreq'] # samplerate
    self._edf_info = edf.info # save the info for now
    # edf.close() # close it

  def _interpolate(self, freq):
    """
    Method placeholder that will allow one to ask for the magnitude of some frequency.
    """
    pass

  # where math-magic happens
  # arrays which are less than the win_size due to not integer iterations are zero-padded
  def process_spectral(self, epoch=2, overlap=0.5, ica=False):
    """
    The heart of analysis.

    - epoch is in seconds such that the window is samplrerate*epoch
    - overlap is just as it sounds.
    - if ica is true, then source separation is performed. Otherwise not. If ICA has been
      performed already, a flag is set and it is not done again.
    """
    if ica & (self._ica_done==False):
      self.process_ica() # process the ICA as a RawArray
    self._win_size = self._sr*epoch # remember
    self._overlap = overlap # remember
    self._fft_freqs = np.fft.rfftfreq(self._win_size, 1/self._sr) # the freqs of the bins
    window = np.hamming(self._win_size) # the window (adjustable??)
    advance = int(self._win_size * self._overlap) # advance in samples
    iter = int(len(self._data[0]) / advance)
    self._frames = np.zeros((len(self._data), iter, len(self._fft_freqs))) # initialize space for the magnitudes
    self.electrodes = {}
    for i,e in enumerate(self._data):
      # e is a timeseries from a single electrode, i is the number of the electrode
      for j in range(iter):
        start = j*advance
        stop = start+self._win_size
        win = e[start:stop] # get the data
        win = np.pad(win, (0, self._win_size-len(win))) * window # pad the data and window it
        mags = np.abs(np.fft.rfft(win)/self._win_size) # analyze and rescale
        self._frames[i][j] = mags # remember all the freqs for now (memory savings to be had...)

      self.electrodes[self._electrode_order[i]] = EEGElectrodeAnalysis(self._electrode_order[i], self._frames[i], self)

  # process ICA manually (when working with TXT files)
  def process_ica_manually(self):
    """
    This method replaces self._data with the sources as found by ICA

    The sklearn documentation is a bit confusing: it's not clear if the unmixing
    matrix is applied when the sources are returned. Calling fit_transform()
    does not return the same results as calling fit(), then transform().
    """
    ica = FastICA(n_components=len(self._electrode_order), random_state=0, max_iter=50000, tol=0.001)
    U = ica.fit_transform(self._data.T) # find sources
    self._mixing_matrix = ica.mixing_ # the (inverted??) mixing matrix
    # self._data = (self._data.dot(self._mixing_matrix)).T # transform it back for the FFT
    self._data = np.dot(self._data, np.linalg.pinv(self._mixing_matrix)).T # transform it back for the FFT
    self._ica_done = True # remember we did ICA

  def process_ica(self):
    """
    This method replaces self._data with the sources as found by ICA
    """
    if self._ica_done:
      print ('ICA has already been performed... Skipping.')
    else:
      self._ica = mne.preprocessing.ICA(n_components=len(self._electrode_order), verbose=self._verbose)
      self._ica.fit(self._raw) # fit it
      self._data = self._ica.get_sources(self._raw).get_data() # retrieve the data itself
      self._ica_done = True

  def _make_raw(self, data):
    """
    Make a RawArray from TXT data. If the montage can be provided, a lot more info can be gleaned.
    """
    info = mne.create_info(ch_names=self._electrode_order, sfreq=self._sr, ch_types=['eeg']*len(self._electrode_order))
    self._raw = mne.io.RawArray(data, info, verbose=self._verbose)

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
  def verbose():
    doc = "Verbosity."
    def fget(self):
      return self._verbose
    def fset(self, value):
      self._verbose = value
    return locals()
  verbose = property(**verbose())

  def fft_freqs():
    doc = "An array of the edge freqencies of the bins in the analysis."""
    def fget(self):
      return self._fft_freqs
    def fset(self, value):
      self._fft_freqs = value
    return locals()
  fft_freqs = property(**fft_freqs())

  def frames():
    doc = "The frames of the analysis. Before analysis is run, this is None."
    def fget(self):
      return self._frames
    def fset(self, value):
      self._frames = value
    return locals()
  frames = property(**frames())

  def electrode_order():
    doc = "The electrode order. Purely for labeling in the JSON and has no effect on the analytic process."
    def fget(self):
      return self._electrode_order
    def fset(self, value):
      self._electrode_order = value
    return locals()
  electrode_order = property(**electrode_order())

  def sr():
    doc = "The samplerate of the data. Defaults to 200Hz"
    def fget(self):
      return self._sr
    def fset(self, value):
      self._sr = value
    return locals()
  sr = property(**sr())

  def overlap():
    doc = "The overlap of the analysis. Defaults to 0.5."
    def fget(self):
      return self._overlap
    def fset(self, value):
      self._overlap = value
    return locals()
  overlap = property(**overlap())

  def data():
    doc = "The actual data, organized in the shape (num_electrodes, num_samples)."
    def fget(self):
      return self._data
    def fset(self, value):
      self._data = value
    return locals()
  data = property(**data())

  def band_defs():
    doc = "The edge frequencies for the bands as a Dictionary. Delinations are abitrary and there can be an arbitarary number of bands."
    def fget(self):
      return self._band_defs
    def fset(self, value):
      self._band_defs = value
    return locals()
  band_defs = property(**band_defs())

  def electrodes():
    doc = "Dictionary that holds the EEGElectrodeAnalysis objects. Before analysis, this is None."
    def fget(self):
      return self._electrodes
    def fset(self, value):
      self._electrodes = value
    return locals()
  electrodes = property(**electrodes())

  @classmethod
  def random(cls, num_frames=100):
    """
    Make a random analysis (for testing). Uses default everything.
    """
    analysis = cls(None)
    analysis._electrodes = {name:EEGElectrodeAnalysis.random(name, num_frames, analysis) for name in analysis._electrode_order}
    return analysis
