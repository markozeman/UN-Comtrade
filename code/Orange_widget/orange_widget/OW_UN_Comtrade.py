import sys
import os

import Orange.data
# from Orange.widgets import widget, gui
from Orange.widgets.widget import OWWidget, settings
from Orange.widgets import widget, gui

# from AnyQt import QtCore
from AnyQt.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem, QTreeView, QListView, QAbstractItemView
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import QSize, QSortFilterProxyModel, QRegExp, Qt, QModelIndex, QVariant


dir_path = os.path.dirname(os.path.realpath(__file__))
path = "/".join(dir_path.split('/')[:-2])
sys.path.insert(0, path)
from UNComtrade import UNComtrade
unc = UNComtrade()


current_tree_widget = None


class FindFilterProxyModel(QSortFilterProxyModel):
    def filterAcceptsRow(self, source_row, source_parent):
        if (self.filterAcceptsRowItself(source_row, source_parent)):
            return True

        if (self.hasAcceptedChildren(source_row, source_parent)):
            return True

        return False

    def filterAcceptsRowItself(self, source_row, source_parent):
        return super(FindFilterProxyModel, self).filterAcceptsRow(source_row, source_parent)

    def hasAcceptedChildren(self, source_row, source_parent):
        model = self.sourceModel()
        sourceIndex = model.index(source_row, 0, source_parent)
        if not (sourceIndex.isValid()):
            return False

        childCount = model.rowCount(sourceIndex)
        if (childCount == 0):
            return False

        for i in range (childCount):
            if (self.filterAcceptsRowItself(i, sourceIndex)):
                return True

            if (self.hasAcceptedChildren(i, sourceIndex)):
                return True

        return False



class OW_UN_Comtrade(widget.OWWidget):
    name = "UN Comtrade"
    description = "Gets data from UN Comtrade database"
    icon = "icons/un_comtrade.jpg"
    priority = 10

    outputs = [("API data", Orange.data.Table)]

    # info = settings.Setting(0)
    profiles_or_time_series = settings.Setting(0)
    commodities_or_services = settings.Setting(0)
    tf_all = settings.Setting(0)
    tf_import = settings.Setting(0)
    tf_export = settings.Setting(0)
    tf_re_import = settings.Setting(0)
    tf_re_export = settings.Setting(0)
    reporter_filter = settings.Setting('')
    partner_filter = settings.Setting('')
    years_filter = settings.Setting('')
    comm_ser_filter = settings.Setting('')

    want_main_area = True

    def __init__(self):
        super().__init__()

        # GUI
        info_box = gui.widgetBox(self.controlArea, "Info")
        self.info = gui.widgetLabel(info_box, 'Select fields in all the boxes and then press Commit.')

        top_box = gui.widgetBox(self.controlArea, "Type of output")
        gui.radioButtonsInBox(top_box, self, 'profiles_or_time_series', ['Profiles', 'Time series'], orientation=False)


        reporter_partner_box = gui.widgetBox(self.controlArea, "", orientation=False)

        reporters_box = gui.widgetBox(reporter_partner_box, "Reporters")
        gui.lineEdit(reporters_box, self, 'reporter_filter', 'Filter ', callback=self.filter_reporter, callbackOnType=True, orientation=False)
        self.list_model_reporter = self.make_list_view('rep', self.on_item_changed, reporters_box)

        partners_box = gui.widgetBox(reporter_partner_box, "Partners")
        gui.lineEdit(partners_box, self, 'partner_filter', 'Filter ', callback=self.filter_partner, callbackOnType=True, orientation=False)
        self.list_model_partner = self.make_list_view('par', self.on_item_changed, partners_box)


        years_flows_box = gui.widgetBox(self.controlArea, "", orientation=False)

        years_box = gui.widgetBox(years_flows_box, "Years")
        gui.lineEdit(years_box, self, 'years_filter', 'Filter ', callback=self.filter_years, callbackOnType=True, orientation=False)
        self.list_model_years = self.make_list_view('year', self.on_item_changed, years_box)

        trade_flows_box = gui.widgetBox(years_flows_box, "Trade")
        tf_first_row = gui.widgetBox(trade_flows_box, "", orientation=False)
        gui.checkBox(tf_first_row, self, 'tf_all', 'All', callback=self.all_trade_flows)
        tf_second_row = gui.widgetBox(trade_flows_box, "", orientation=False)
        gui.checkBox(tf_second_row, self, 'tf_import', 'Import')
        gui.checkBox(tf_second_row, self, 'tf_export', 'Export')
        tf_third_row = gui.widgetBox(trade_flows_box, "", orientation=False)
        gui.checkBox(tf_third_row, self, 'tf_re_import', 'Re-import')
        gui.checkBox(tf_third_row, self, 'tf_re_export', 'Re-export')


        commodities_services_box = gui.widgetBox(self.mainArea, "Exchange Type")
        gui.radioButtonsInBox(commodities_services_box, self, 'commodities_or_services', ['Commodities', 'Services'], orientation=False, callback=(lambda: self.change_tree_view(commodities_services_box)))
        gui.lineEdit(commodities_services_box, self, 'comm_ser_filter', 'Filter ', callback=self.filter_comm_ser, callbackOnType=True, orientation=False)
        self.tree_model_cs = self.make_tree_view('comm', self.on_item_changed, commodities_services_box)


        button_box = gui.widgetBox(self.controlArea, "")
        gui.button(button_box, self, "Commit", callback=self.commit)


    def make_list_view(self, type, callback, append_to):
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
        # list.setGridSize(QSize(400, 200))

        append_to.layout().addWidget(list)

        return [list, model]


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
        tree.setSelectionMode(QAbstractItemView.ExtendedSelection)      # TODO delete?

        current_tree_widget = tree

        append_to.layout().addWidget(tree)

        return [tree, model]

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

    def all_trade_flows(self):
        if (self.tf_all):
            self.tf_import = True
            self.tf_export = True
            self.tf_re_import = True
            self.tf_re_export = True

    def filter_reporter(self):
        l = self.list_model_reporter[0]
        m = self.list_model_reporter[1]
        self.use_proxy_filter(l, m, self.reporter_filter, False)

    def filter_partner(self):
        l = self.list_model_partner[0]
        m = self.list_model_partner[1]
        self.use_proxy_filter(l, m, self.partner_filter, False)

    def filter_years(self):
        l = self.list_model_years[0]
        m = self.list_model_years[1]
        self.use_proxy_filter(l, m, self.years_filter, False)

    def filter_comm_ser(self):
        t = self.tree_model_cs[0]
        m = self.tree_model_cs[1]
        self.use_proxy_filter(t, m, self.comm_ser_filter, True)

    def change_tree_view(self, box):
        cs = self.commodities_or_services
        if (cs == 0):
            self.tree_model_cs = self.make_tree_view('comm', self.on_item_changed, box)
        elif (cs == 1):
            self.tree_model_cs = self.make_tree_view('ser', self.on_item_changed, box)

        t = self.tree_model_cs[0]
        m = self.tree_model_cs[1]
        self.use_proxy_filter(t, m, self.comm_ser_filter, True)

    def use_proxy_filter(self, list_or_tree, model, filter, bool_tree):
        proxy_model = FindFilterProxyModel()
        proxy_model.setSourceModel(model)

        proxy_model.setFilterRegExp(QRegExp(filter))
        proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        proxy_model.setFilterKeyColumn(-1)

        list_or_tree.setModel(proxy_model)

        if (bool_tree):
            list_or_tree.expandAll()


    def commit(self):
        number_of_all_selected = 0

        selected_reporters = [rep.data(0) for rep in self.list_model_reporter[0].selectedIndexes()]
        if (len(selected_reporters) == 254):
            selected_reporters = 'All'
            number_of_all_selected += 1

        selected_partners = [par.data(0) for par in self.list_model_partner[0].selectedIndexes()]
        if (len(selected_partners) == 292):
            selected_partners = 'All'
            number_of_all_selected += 1

        selected_years = [year.data(0) for year in self.list_model_years[0].selectedIndexes()]
        if (len(selected_years) == 55):
            selected_years = 'All'
            number_of_all_selected += 1

        selected_trade = []
        if (self.tf_all):
            selected_trade.append('All')
        else:
            if (self.tf_import):
                selected_trade.append('Import')
            if (self.tf_export):
                selected_trade.append('Export')
            if (self.tf_re_import):
                selected_trade.append('re-Import')
            if (self.tf_re_export):
                selected_trade.append('re-Export')


        tree_selected = [item.data(0) for item in self.tree_model_cs[0].selectedIndexes()]
        print(tree_selected)

        print('COMMIT')
        print(self.profiles_or_time_series)
        print(self.commodities_or_services)
        print(selected_reporters)
        print(selected_partners)
        print(selected_years)
        print(selected_trade)

        validation = self.validate_commit(number_of_all_selected, len(selected_reporters), len(selected_partners), len(selected_years), len(selected_trade), len(tree_selected))
        if (not validation):
            return

        print('Getting....')
        self.info.setStyleSheet("QLabel { color : black; }")
        self.info.setText('Retrieving data...')
        self.info.repaint()



        if (self.commodities_or_services == 0):
            tree_type = 'C'
        elif (self.commodities_or_services == 1):
            tree_type = 'S'

        res = unc.get_data(selected_reporters, selected_partners, selected_years, selected_trade, type=tree_type, commodities=tree_selected)
        # print(res)

        if (self.profiles_or_time_series == 0):
            output_table = unc.table_profiles(res, selected_years)
        elif (self.profiles_or_time_series == 1):
            output_table = unc.table_time_series(res)
        print(output_table)

        # output = Orange.data.Table(output_table)
        #
        # self.send("API data", output)

        self.info.setStyleSheet("QLabel { color : green; }")
        self.info.setText('Data is ready as Orange Data Table.')


    def validate_commit(self, number_all_selected, rep_len, par_len, years_len, trade_len, tree_len):
        self.info.setStyleSheet("QLabel { color : #dd0000; }")

        if (number_all_selected > 1):
            self.info.setText('Only one of reporters, partners and years can have all items selected.')
            return False
        if (rep_len == 0):
            self.info.setText('You have to choose at least one reporter.')
            return False
        if (par_len == 0):
            self.info.setText('You have to choose at least one partner.')
            return False
        if (years_len == 0):
            self.info.setText('You have to choose at least one year.')
            return False
        if (trade_len == 0):
            self.info.setText('You have to choose at least one trade flow.')
            return False
        if (tree_len == 0):
            self.info.setText('You have to choose at least one commodity or service.')
            return False

        return True



if __name__ == "__main__":
    app = QApplication([])
    w = OW_UN_Comtrade()
    w.show()
    app.exec_()