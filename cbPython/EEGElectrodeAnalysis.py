import numpy as np
from cbPython.GraphicEEGFrame import GraphicEEGFrame

class EEGElectrodeAnalysis(object):
  """
  An analyzed electrode. Contains all the frames from the electrode. Mostly for convenice.
  """

  def __init__(self, name=None, frames=None, analysis=None):
    super(EEGElectrodeAnalysis, self).__init__()
    self._name = name
    self._frames = frames
    self._analysis = analysis
    self._graphic_frames = []
    self._bands = None

    if frames is not None:
      self._as_bands()
      self._get_graphic_frames()

  def __repr__(self):
    return '{}({}, frames: {})'.format(self.__class__.__name__, self._name, len(self._frames))

  def _get_graphic_frames(self):
    for i,f in enumerate(self._frames):
      gf = GraphicEEGFrame(i, self._name, f, self._analysis)
      self._graphic_frames.append(gf)

  def _as_bands(self):
    self._bands = {name:[] for name in self._analysis.band_defs.keys()} # prepare the dictionary
    band_idxs = self._get_idxs() # the indicies in each frame where we find what we're looking for
    for w in self._frames:
      for i,band in enumerate(self._bands.keys()): # bands in window
        vals = w[band_idxs[i]]
        self._bands[band].append(vals)
    self._bands = {name:np.array(value) for name,value in self._bands.items()}

  # get the indexes for the frequencies we actually want
  # then we just use that to select relevant bins from the analysis windows
  def _get_idxs(self):
    idxs = []
    for key,defin in self._analysis.band_defs.items():
      f_idxs = []
      freqs = self._analysis.fft_freqs[(self._analysis.fft_freqs>=defin[0]) & (self._analysis.fft_freqs<defin[1])]
      for f in freqs:
        f_idxs.append((np.argwhere(self._analysis.fft_freqs==f)[0][0]))
      idxs.append(f_idxs)
    return idxs

  @classmethod
  def random(cls, name, num_frames=100, analysis=None):
    this = cls(name, analysis=analysis)
    graphic_frames = []
    frames = []
    for i in range(num_frames):
      g_rand = GraphicEEGFrame.random(i, analysis)
      frames.append(g_rand.values)
      graphic_frames.append(g_rand)
    this._frames = np.array(frames)
    this._graphic_frames = graphic_frames
    return this

  ################################
  ## Properties
  ################################
  def frames():
      doc = "The frames of the analysis."
      def fget(self):
          return self._frames
      return locals()
  frames = property(**frames())

  def name():
      doc = "The name of the electrode. Unsettable except upon instantiation."
      def fget(self):
          return self._name
      return locals()
  name = property(**name())

  def bands():
      doc = "The names and analytic values of the bands as a Dictionary."
      def fget(self):
          return self._bands
      def fset(self, value):
          self._bands = value
      return locals()
  bands = property(**bands())

  def graphic_frames():
      doc = "The GraphicEEGFrames in an array, one for each frame of analysis."
      def fget(self):
          return self._graphic_frames
      return locals()
  graphic_frames = property(**graphic_frames())
