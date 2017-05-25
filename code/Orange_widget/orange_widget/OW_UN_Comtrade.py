import sys
import numpy

import Orange.data
from Orange.widgets import widget, gui

class OWDataSamplerA(widget.OWWidget):
    name = "Data Sampler"
    description = "Randomly selects a subset of instances from the data set"
    icon = "icons/DataSamplerA.svg"
    priority = 10

    inputs = [("Data", Orange.data.Table, "set_data")]
    outputs = [("Sampled Data", Orange.data.Table)]

    want_main_area = False

    def __init__(self):
        super().__init__()

        # GUI
        box = gui.widgetBox(self.controlArea, "Info")
        self.infoa = gui.widgetLabel(box, 'No data on input yet, waiting to get something.')
        self.infob = gui.widgetLabel(box, '')


    def set_data(self, dataset):
        if dataset is not None:
            self.infoa.setText('%d instances in input data set' % len(dataset))
            indices = numpy.random.permutation(len(dataset))
            indices = indices[:int(numpy.ceil(len(dataset) * 0.5))]
            sample = dataset[indices]
            self.infob.setText('%d sampled instances' % len(sample))
            self.send("Sampled Data", sample)
        else:
            self.infoa.setText('No data on input yet, waiting to get something.')
            self.infob.setText('')
            self.send("Sampled Data", None)