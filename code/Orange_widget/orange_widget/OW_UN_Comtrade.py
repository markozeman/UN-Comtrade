import sys
import os

import Orange.data
# from Orange.widgets import widget, gui
from Orange.widgets.widget import OWWidget, settings
from Orange.widgets import widget, gui

# from AnyQt import QtCore
from AnyQt.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem, QTreeView, QListView
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt


dir_path = os.path.dirname(os.path.realpath(__file__))
path = "/".join(dir_path.split('/')[:-2])
sys.path.insert(0, path)
from UNComtrade import UNComtrade
unc = UNComtrade()

print(unc.reporters())


class OW_UN_Comtrade(widget.OWWidget):
    name = "UN Comtrade"
    description = "Gets data from UN Comtrade database"
    icon = "icons/un_comtrade.jpg"
    priority = 10

    outputs = [("API data", Orange.data.Table)]

    info = settings.Setting(0)
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
        info_box = gui.widgetBox(self.controlArea, "Info")
        self.info_a = gui.widgetLabel(info_box, 'All information.')

        top_box = gui.widgetBox(self.controlArea, "Type of output")
        gui.radioButtonsInBox(top_box, self, 'profiles_or_time_series', ['Profiles', 'Time series'], orientation=False)


        reporter_partner_box = gui.widgetBox(self.controlArea, "", orientation=False)

        reporters_box = gui.widgetBox(reporter_partner_box, "Reporters")
        gui.lineEdit(reporters_box, self, 'reporter_filter', 'Filter ', callback=self.filter_reporter, callbackOnType=True, orientation=False)
        gui.checkBox(reporters_box, self, 'reporter1', 'All')
        gui.checkBox(reporters_box, self, 'reporter2', 'Slovenia')
        gui.checkBox(reporters_box, self, 'reporter3', 'Croatia')

        rep = unc.reporters()
        reporters_tree = QTreeView()

        model = QStandardItemModel(0, 1)
        model.setHeaderData(0, Qt.Horizontal, "Countries")

        item_all = QStandardItem(rep[0])
        item_all.setCheckable(True)

        for i in range(1, len(rep)):
            item = QStandardItem(rep[i])
            item.setCheckable(True)
            item_all.setChild(i-1, item)

        model.setItem(0, item_all)

        model.itemChanged.connect(self.on_item_changed)
        reporters_tree.setModel(model)

        reporters_tree.setHeaderHidden(True)
        reporters_tree.expandAll()
        reporters_box.layout().addWidget(reporters_tree)




        partners_box = gui.widgetBox(reporter_partner_box, "Partners")
        gui.lineEdit(partners_box, self, 'partner_filter', 'Filter ', callback=self.filter_partner, callbackOnType=True, orientation=False)
        gui.checkBox(partners_box, self, 'partner1', 'All')
        gui.checkBox(partners_box, self, 'partner2', 'Slovenia')
        gui.checkBox(partners_box, self, 'partner3', 'Croatia')


        years_flows_box = gui.widgetBox(self.controlArea, "", orientation=False)

        years_box = gui.widgetBox(years_flows_box, "Years")
        gui.lineEdit(years_box, self, 'year_start_filter', 'From ', callback=self.filter_year_start, callbackOnType=True, orientation=False)
        gui.lineEdit(years_box, self, 'year_end_filter', 'To     ', callback=self.filter_year_end, callbackOnType=True, orientation=False)
        gui.checkBox(years_box, self, 'years1', 'All')
        gui.checkBox(years_box, self, 'years2', '2016')
        gui.checkBox(years_box, self, 'years3', '2015')

        trade_flows_box = gui.widgetBox(years_flows_box, "Trade")
        gui.checkBox(trade_flows_box, self, 'trade_flow1', 'All')
        gui.checkBox(trade_flows_box, self, 'trade_flow2', 'Import')
        gui.checkBox(trade_flows_box, self, 'trade_flow3', 'Export')


        commodities_services_box = gui.widgetBox(self.controlArea, "Exchange Type")
        gui.radioButtonsInBox(commodities_services_box, self, 'commodities_or_services', ['Commodities', 'Services'], orientation=False)
        gui.lineEdit(commodities_services_box, self, 'comm_ser_filter', 'Filter ', callback=self.filter_comm_ser, callbackOnType=True, orientation=False)
        gui.checkBox(commodities_services_box, self, 'comm_ser1', 'Item 1')
        gui.checkBox(commodities_services_box, self, 'comm_ser2', 'Subitem 1')
        gui.checkBox(commodities_services_box, self, 'comm_ser3', 'Subitem 2')
        gui.checkBox(commodities_services_box, self, 'comm_ser4', 'Item 2')

        button_box = gui.widgetBox(self.controlArea, "")
        gui.button(button_box, self, "Commit", callback=self.commit)


    def on_item_changed(self):
        print('changee')


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


if __name__ == "__main__":
    app = QApplication([])
    w = OW_UN_Comtrade()
    w.show()
    app.exec_()