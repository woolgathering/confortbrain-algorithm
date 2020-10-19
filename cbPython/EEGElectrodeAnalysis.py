import numpy as np
from cbPython.GraphicEEGFrame import GraphicEEGFrame

class EEGElectrodeAnalysis(object):
  """docstring for EEGElectrodeAnalysis."""

  def __init__(self, name=None, data=None, analysis=None):
    super(EEGElectrodeAnalysis, self).__init__()
    self._name = name
    self._data = data
    self._analysis = analysis
    self._frames = None
    self._graphic_frames = None

  def __repr__(self):
    return '{}({}, frames: {})'.format(self.__class__.__name__, self._name, len(self._frames))

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


  def data():
      doc = "The data property."
      def fget(self):
          return self._data
      def fset(self, value):
          self._data = value
      return locals()
  data = property(**data())

  def name():
      doc = "The name of the electrode. Unsettable except upon instantiation."
      def fget(self):
          return self._name
      return locals()
  name = property(**name())

  def frames():
      doc = "The frames property."
      def fget(self):
          return self._frames
      return locals()
  frames = property(**frames())

  def graphic_frames():
      doc = "The graphic_frames property."
      def fget(self):
          return self._graphic_frames
      return locals()
  graphic_frames = property(**graphic_frames())
