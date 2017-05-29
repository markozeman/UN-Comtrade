import sys
import os

import Orange.data
# from Orange.widgets import widget, gui
from Orange.widgets.widget import OWWidget, settings
from Orange.widgets import widget, gui

dir_path = os.path.dirname(os.path.realpath(__file__))
path = "/".join(dir_path.split('/')[:-2])
sys.path.insert(0, path)

from UNComtrade import UNComtrade

unc = UNComtrade()


class OW_UN_Comtrade(widget.OWWidget):
    name = "UN Comtrade"
    description = "Gets data from UN Comtrade database"
    icon = "icons/un_comtrade.jpg"
    priority = 10

    outputs = [("API data", Orange.data.Table)]

    profiles_or_time_series = settings.Setting(0)
    commodities_or_services = settings.Setting(0)
    reporter1 = settings.Setting(0)
    reporter2 = settings.Setting(0)
    reporter3 = settings.Setting(0)
    partner1 = settings.Setting(0)
    partner2 = settings.Setting(0)
    partner3 = settings.Setting(0)
    years1 = settings.Setting(0)
    years2 = settings.Setting(0)
    years3 = settings.Setting(0)
    trade_flow1 = settings.Setting(0)
    trade_flow2 = settings.Setting(0)
    trade_flow3 = settings.Setting(0)
    comm_ser1 = settings.Setting(0)
    comm_ser2 = settings.Setting(0)
    comm_ser3 = settings.Setting(0)
    comm_ser4 = settings.Setting(0)
    reporter_filter = settings.Setting('')
    partner_filter = settings.Setting('')
    year_start_filter = settings.Setting(2013)
    year_end_filter = settings.Setting(2015)
    comm_ser_filter = settings.Setting('')

    want_main_area = False

    def __init__(self):
        super().__init__()

        # GUI
        top_box = gui.widgetBox(self.controlArea, "Type of output")
        gui.radioButtonsInBox(top_box, self, 'profiles_or_time_series', ['Profiles', 'Time series'])

        reporters_box = gui.widgetBox(self.controlArea, "Reporters")
        gui.lineEdit(reporters_box, self, 'reporter_filter', 'Filter ', callback=self.filter_reporter, callbackOnType=True)
        gui.checkBox(reporters_box, self, 'reporter1', 'All')
        gui.checkBox(reporters_box, self, 'reporter2', 'Slovenia')
        gui.checkBox(reporters_box, self, 'reporter3', 'Croatia')

        partners_box = gui.widgetBox(self.controlArea, "Partners")
        gui.lineEdit(partners_box, self, 'partner_filter', 'Filter ', callback=self.filter_partner, callbackOnType=True)
        gui.checkBox(partners_box, self, 'partner1', 'All')
        gui.checkBox(partners_box, self, 'partner2', 'Slovenia')
        gui.checkBox(partners_box, self, 'partner3', 'Croatia')

        years_box = gui.widgetBox(self.controlArea, "Years")
        gui.lineEdit(years_box, self, 'year_start_filter', 'From ', callback=self.filter_year_start, callbackOnType=True)
        gui.lineEdit(years_box, self, 'year_end_filter', 'To ', callback=self.filter_year_end, callbackOnType=True)
        gui.checkBox(years_box, self, 'years1', 'All')
        gui.checkBox(years_box, self, 'years2', '2016')
        gui.checkBox(years_box, self, 'years3', '2015')

        trade_flows_box = gui.widgetBox(self.controlArea, "Trade")
        gui.checkBox(trade_flows_box, self, 'trade_flow1', 'All')
        gui.checkBox(trade_flows_box, self, 'trade_flow2', 'Import')
        gui.checkBox(trade_flows_box, self, 'trade_flow3', 'Export')

        commodities_services_box = gui.widgetBox(self.controlArea, "Exchange Type")
        gui.radioButtonsInBox(commodities_services_box, self, 'commodities_or_services', ['Commodities', 'Services'])
        gui.lineEdit(commodities_services_box, self, 'comm_ser_filter', 'Filter ', callback=self.filter_comm_ser, callbackOnType=True)
        gui.checkBox(commodities_services_box, self, 'comm_ser1', 'Item 1')
        gui.checkBox(commodities_services_box, self, 'comm_ser2', 'Subitem 1')
        gui.checkBox(commodities_services_box, self, 'comm_ser3', 'Subitem 2')
        gui.checkBox(commodities_services_box, self, 'comm_ser4', 'Item 2')

        gui.button(commodities_services_box, self, "Commit", callback=self.commit)



    def commit(self):
        print('COMMIT')

    def filter_reporter(self):
        print(self.reporter_filter)

    def filter_partner(self):
        print(self.partner_filter)

    def filter_year_start(self):
        print(self.year_start_filter)

    def filter_year_end(self):
        print(self.year_end_filter)

    def filter_comm_ser(self):
        print(self.comm_ser_filter)