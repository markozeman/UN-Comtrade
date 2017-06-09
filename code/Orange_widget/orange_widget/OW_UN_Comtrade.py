import sys
import os

import Orange.data
# from Orange.widgets import widget, gui
from Orange.widgets.widget import OWWidget, settings
from Orange.widgets import widget, gui

# from AnyQt import QtCore
from AnyQt.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem, QTreeView, QListView, QAbstractItemView
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import QSize, QSortFilterProxyModel, QRegExp, Qt


dir_path = os.path.dirname(os.path.realpath(__file__))
path = "/".join(dir_path.split('/')[:-2])
sys.path.insert(0, path)
from UNComtrade import UNComtrade
unc = UNComtrade()


current_tree_widget = None


class OW_UN_Comtrade(widget.OWWidget):
    name = "UN Comtrade"
    description = "Gets data from UN Comtrade database"
    icon = "icons/un_comtrade.jpg"
    priority = 10

    outputs = [("API data", Orange.data.Table)]

    info = settings.Setting(0)
    profiles_or_time_series = settings.Setting(0)
    commodities_or_services = settings.Setting(0)
    tf_all = settings.Setting(0)
    tf_import = settings.Setting(0)
    tf_export = settings.Setting(0)
    tf_re_import = settings.Setting(0)
    tf_re_export = settings.Setting(0)
    reporter_filter = settings.Setting('')
    partner_filter = settings.Setting('')
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
        gui.lineEdit(reporters_box, self, 'reporter_filter', 'Filter ', callback=(lambda: self.filter_reporter(reporters_box)), callbackOnType=True, orientation=False)
        self.make_list_view('rep', self.on_item_changed, reporters_box, '')

        partners_box = gui.widgetBox(reporter_partner_box, "Partners")
        gui.lineEdit(partners_box, self, 'partner_filter', 'Filter ', callback=self.filter_partner, callbackOnType=True, orientation=False)
        self.make_list_view('par', self.on_item_changed, partners_box, '')


        years_flows_box = gui.widgetBox(self.controlArea, "", orientation=False)

        years_box = gui.widgetBox(years_flows_box, "Years")
        self.make_list_view('year', self.on_item_changed, years_box, '')

        trade_flows_box = gui.widgetBox(years_flows_box, "Trade")
        tf_first_row = gui.widgetBox(trade_flows_box, "", orientation=False)
        gui.checkBox(tf_first_row, self, 'tf_all', 'All')
        tf_second_row = gui.widgetBox(trade_flows_box, "", orientation=False)
        gui.checkBox(tf_second_row, self, 'tf_import', 'Import')
        gui.checkBox(tf_second_row, self, 'tf_export', 'Export')
        tf_third_row = gui.widgetBox(trade_flows_box, "", orientation=False)
        gui.checkBox(tf_third_row, self, 'tf_re_import', 'Re-import')
        gui.checkBox(tf_third_row, self, 'tf_re_export', 'Re-export')


        commodities_services_box = gui.widgetBox(self.controlArea, "Exchange Type")
        gui.radioButtonsInBox(commodities_services_box, self, 'commodities_or_services', ['Commodities', 'Services'], orientation=False, callback=(lambda: self.change_tree_view(commodities_services_box)))
        gui.lineEdit(commodities_services_box, self, 'comm_ser_filter', 'Filter ', callback=self.filter_comm_ser, callbackOnType=True, orientation=False)
        self.make_tree_view('comm', self.on_item_changed, commodities_services_box)


        button_box = gui.widgetBox(self.controlArea, "")
        gui.button(button_box, self, "Commit", callback=self.commit)


    def make_list_view(self, type, callback, append_to, filter):
        if (type == 'rep'):
            data = unc.reporters()
        elif (type == 'par'):
            data = unc.partners()
        elif (type == 'year'):
            data = unc.years()

        list = QListView()

        model = QStandardItemModel(0, 1)

        for i in range(1, len(data)):
            item = QStandardItem(str(data[i]))
            model.appendRow(item)

        model.itemChanged.connect(callback)
        list.setModel(model)
        list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        list.setSelectionMode(QAbstractItemView.ExtendedSelection)

        proxy_model = QSortFilterProxyModel()
        proxy_model.setSourceModel(model)

        proxy_model.setFilterRegExp(QRegExp(filter))
        proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        proxy_model.setFilterKeyColumn(0)

        list.setModel(proxy_model)
        # list.setSortingEnabled(True)

        # list.setGridSize(QSize(400, 200))

        append_to.layout().addWidget(list)


    def make_tree_view(self, type, callback, append_to):
        if (type == 'comm'):
            data = unc.commodities_HS_all()
        elif (type == 'ser'):
            data = unc.services_all()

        global current_tree_widget
        if (current_tree_widget is not None):
            append_to.layout().removeWidget(current_tree_widget)

        tree = QTreeView()
        model = QStandardItemModel(0, 1)

        model = self.recursive({'children': data}, None, model)

        model.itemChanged.connect(callback)
        tree.setModel(model)

        tree.setHeaderHidden(True)
        tree.expandAll()
        tree.setEditTriggers(QAbstractItemView.NoEditTriggers)

        proxy_model = QSortFilterProxyModel()
        proxy_model.setSourceModel(model)
        tree.setModel(proxy_model)
        # tree.setSortingEnabled(True)

        current_tree_widget = tree

        append_to.layout().addWidget(tree)


    def recursive(self, obj, parent, model):
        if (not obj['children']):
            return model

        for key in obj['children']:
            new_obj = obj['children'][key]

            top_item = QStandardItem(new_obj['text'])
            top_item.setCheckable(True)

            if (parent is not None):
                parent.setChild(parent.rowCount(), top_item)
            else:
                model.setItem(model.rowCount(), top_item)

            self.recursive(new_obj, top_item, model)

        return model


    def on_item_changed(self):
        print('changee')

    def commit(self):
        print('COMMIT')
        print(self.profiles_or_time_series)
        print(self.commodities_or_services)

    def filter_reporter(self, reporter_box):
        print(self.reporter_filter)
        print(reporter_box)

        self.make_list_view('rep', self.on_item_changed, reporter_box, self.reporter_filter)



    def filter_partner(self):
        print(self.partner_filter)

    def filter_comm_ser(self):
        print(self.comm_ser_filter)

    def change_tree_view(self, box):
        cs = self.commodities_or_services
        print(cs)

        if (cs == 0):
            self.make_tree_view('comm', self.on_item_changed, box)
        elif (cs == 1):
            self.make_tree_view('ser', self.on_item_changed, box)



if __name__ == "__main__":
    app = QApplication([])
    w = OW_UN_Comtrade()
    w.show()
    app.exec_()