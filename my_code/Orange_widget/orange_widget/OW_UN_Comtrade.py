import sys
import os

import Orange.data
# from Orange.widgets import widget, gui
from Orange.widgets.widget import OWWidget, settings
from Orange.widgets import widget, gui

# from AnyQt import QtCore
from AnyQt.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem, QTreeView, QListView, QAbstractItemView, \
    QSizePolicy
from PyQt5.QtCore import QItemSelectionModel
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
    tf_import = settings.Setting(0)
    tf_export = settings.Setting(0)
    tf_re_import = settings.Setting(0)
    tf_re_export = settings.Setting(0)
    reporter_filter = settings.Setting('')
    partner_filter = settings.Setting('')
    years_filter = settings.Setting('')
    comm_ser_filter = settings.Setting('')

    want_main_area = False

    def __init__(self):
        super().__init__()

        whole_box = gui.widgetBox(self.controlArea, "", orientation=False)
        left_box = gui.widgetBox(whole_box, "")
        right_box = gui.widgetBox(whole_box, "")

        # GUI
        info_box = gui.widgetBox(left_box, "Info")
        self.info = gui.widgetLabel(info_box, 'No reporters, no partners, no commodities/services')

        size_policy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Minimum)
        top_box = gui.widgetBox(left_box, "Type of output")
        gui.radioButtonsInBox(top_box, self, 'profiles_or_time_series', ['Profiles', 'Time series'],
                              orientation=False, sizePolicy=size_policy)

        reporter_partner_years_box = gui.widgetBox(left_box, "", orientation=False)

        size_policy.setHorizontalStretch(2)
        reporters_box = gui.widgetBox(reporter_partner_years_box, "Reporters", sizePolicy=size_policy)
        gui.lineEdit(reporters_box, self, 'reporter_filter', 'Filter ', callback=self.filter_reporter, callbackOnType=True, orientation=False)
        self.list_model_reporter = self.make_list_view('rep', self.on_item_changed, reporters_box)

        size_policy.setHorizontalStretch(2)
        partners_box = gui.widgetBox(reporter_partner_years_box, "Partners", sizePolicy=size_policy)
        gui.lineEdit(partners_box, self, 'partner_filter', 'Filter ', callback=self.filter_partner, callbackOnType=True, orientation=False)
        self.list_model_partner = self.make_list_view('par', self.on_item_changed, partners_box)

        size_policy.setHorizontalStretch(1)
        years_box = gui.widgetBox(reporter_partner_years_box, "Years", sizePolicy=size_policy)
        gui.lineEdit(years_box, self, 'years_filter', 'Filter ', callback=self.filter_years, callbackOnType=True, orientation=False)
        self.list_model_years = self.make_list_view('year', self.on_item_changed, years_box)

        trade_flows_box = gui.widgetBox(left_box, "Trade", orientation=False)
        gui.checkBox(trade_flows_box, self, 'tf_import', 'Import', callback=self.on_item_changed)
        exp = gui.checkBox(trade_flows_box, self, 'tf_export', 'Export', callback=self.on_item_changed)
        exp.setCheckState(Qt.Checked)
        gui.checkBox(trade_flows_box, self, 'tf_re_import', 'Re-import', callback=self.on_item_changed)
        gui.checkBox(trade_flows_box, self, 'tf_re_export', 'Re-export', callback=self.on_item_changed)

        commodities_services_box = gui.widgetBox(right_box, "Exchange Type")
        gui.radioButtonsInBox(commodities_services_box, self, 'commodities_or_services', ['Commodities', 'Services'],
                              orientation=False, sizePolicy=size_policy, callback=(lambda: self.change_tree_view(commodities_services_box)))
        gui.lineEdit(commodities_services_box, self, 'comm_ser_filter', 'Filter ', callback=self.filter_comm_ser, callbackOnType=True, orientation=False)
        self.tree_model_cs = self.make_tree_view('comm', self.on_item_changed, commodities_services_box)

        button_box = gui.widgetBox(left_box, "")
        self.commit_button = gui.button(button_box, self, "Commit", callback=self.commit)
        self.commit_button.setEnabled(False)

        # activate filters
        self.filter_reporter()
        self.filter_partner()
        self.filter_years()
        self.filter_comm_ser()


    def make_list_view(self, type, callback, append_to):
        if (type == 'rep'):
            data = unc.reporters()
        elif (type == 'par'):
            data = unc.partners()
        elif (type == 'year'):
            data = unc.years()

        list = QListView()
        list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        model = QStandardItemModel(0, 1)

        for i in range(1, len(data)):
            item = QStandardItem(str(data[i]))
            model.appendRow(item)

        model.itemChanged.connect(callback)
        list.setModel(model)
        list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        list.setSelectionMode(QAbstractItemView.ExtendedSelection)

        proxy_model = FindFilterProxyModel()
        proxy_model.setSourceModel(model)
        proxy_model.setFilterKeyColumn(-1)
        list.setModel(proxy_model)
        list.selectionModel().selectionChanged.connect(callback)

        append_to.layout().addWidget(list)

        return [list, proxy_model]


    def make_tree_view(self, type, callback, append_to):
        if (type == 'comm'):
            data = unc.commodities_HS_all()
        elif (type == 'ser'):
            data = unc.services_all()

        global current_tree_widget
        if (current_tree_widget is not None):
            append_to.layout().removeWidget(current_tree_widget)

        class TreeView(QTreeView):
            def sizeHint(self):
                return QSize(700, 600)

        tree = TreeView(sizePolicy=QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))
        model = QStandardItemModel(0, 1)

        model = self.recursive({'children': data}, None, model)

        model.itemChanged.connect(callback)
        tree.setModel(model)

        tree.setHeaderHidden(True)
        tree.expandAll()
        tree.setEditTriggers(QAbstractItemView.NoEditTriggers)

        proxy_model = FindFilterProxyModel()
        proxy_model.setSourceModel(model)
        proxy_model.setFilterKeyColumn(-1)
        tree.setModel(proxy_model)

        tree.expandAll()

        current_tree_widget = tree

        append_to.layout().addWidget(tree)

        return [tree, proxy_model]

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

        if not hasattr(self, 'tree_model_cs'):
            return

        rep_num, par_num, tree_num = self.set_info_string()

        number_of_all_selected = 0
        if (rep_num == 254):
            number_of_all_selected += 1
        if (par_num == 292):
            number_of_all_selected += 1
        selected_years = [year.data(0) for year in self.list_model_years[0].selectedIndexes()]
        if (len(selected_years) == 55):
            number_of_all_selected += 1

        selected_trade = self.get_checked_trades()

        self.validate_commit(number_of_all_selected, rep_num, par_num, len(selected_years), len(selected_trade), tree_num)


    def set_info_string(self):
        rep_num = len(self.list_model_reporter[0].selectedIndexes())
        par_num = len(self.list_model_partner[0].selectedIndexes())

        tree_model = self.tree_model_cs[1]
        top_item = tree_model.index(0, 0)
        checked_items = tree_model.match(top_item, Qt.CheckStateRole, Qt.Checked, -1, Qt.MatchRecursive)
        tree_num = len(checked_items)

        if (rep_num > 1):
            rep_str = str(rep_num) + ' reporters'
        elif (rep_num == 1):
            rep_str = str(rep_num) + ' reporter'
        elif (rep_num == 0):
            rep_str = 'no reporters'

        if (par_num > 1):
            par_str = str(par_num) + ' partners'
        elif (par_num == 1):
            par_str = str(par_num) + ' partner'
        elif (par_num == 0):
            par_str = 'no partners'

        if (tree_num > 1):
            tree_str = str(tree_num) + ' commodities/services'
        elif (tree_num == 1):
            tree_str = str(tree_num) + ' commodity/service'
        elif (tree_num == 0):
            tree_str = 'no commodities/services'

        s = 'Input: ' + rep_str + ', ' + par_str + ', ' + tree_str

        self.info.setStyleSheet("QLabel { color : black; }")
        self.info.setText(s)

        return [rep_num, par_num, tree_num]


    def filter_reporter(self):
        list_view, proxy_model = self.list_model_reporter
        # selection = list_view.selectionModel().selection()

        # print('selection model', list_view.selectionModel())
        # print('selection', selection)
        # print('indexes', [item.data(0) for item in list_view.selectionModel().selectedIndexes()])
        # print()

        proxy_model.setFilterRegExp(QRegExp(self.reporter_filter, Qt.CaseInsensitive))

        # print('indexes middle', [item.data(0) for item in list_view.selectionModel().selectedIndexes()])

        # list_view.selectionModel().select(selection, QItemSelectionModel.Select)

        # print('selection model.selection() after', list_view.selectionModel().selection())
        # print('indexes after', [item.data(0) for item in list_view.selectionModel().selectedIndexes()])
        # print('-------------------------------------\n')


    def filter_partner(self):
        list_view, proxy_model = self.list_model_partner
        proxy_model.setFilterRegExp(QRegExp(self.partner_filter, Qt.CaseInsensitive))

    def filter_years(self):
        list_view, proxy_model = self.list_model_years
        proxy_model.setFilterRegExp(QRegExp(self.years_filter, Qt.CaseInsensitive))

    def filter_comm_ser(self):
        tree_view, proxy_model = self.tree_model_cs
        proxy_model.setFilterRegExp(QRegExp(self.comm_ser_filter, Qt.CaseInsensitive))

    def change_tree_view(self, box):
        cs = self.commodities_or_services
        if (cs == 0):
            self.tree_model_cs = self.make_tree_view('comm', self.on_item_changed, box)
        elif (cs == 1):
            self.tree_model_cs = self.make_tree_view('ser', self.on_item_changed, box)

        tree_view, proxy_model = self.tree_model_cs
        proxy_model.setFilterRegExp(QRegExp(self.comm_ser_filter, Qt.CaseInsensitive))


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
        selected_years.sort()
        if (len(selected_years) == 55):
            selected_years = 'All'
            number_of_all_selected += 1

        selected_trade = self.get_checked_trades()

        tree_model = self.tree_model_cs[1]
        top_item = tree_model.index(0, 0)
        checked_items = tree_model.match(top_item, Qt.CheckStateRole, Qt.Checked, -1, Qt.MatchRecursive)
        tree_selection = [item.data(0) for item in checked_items]

        print('COMMIT')
        print(self.profiles_or_time_series)
        print(self.commodities_or_services)
        print(selected_reporters)
        print(selected_partners)
        print(selected_years)
        print(selected_trade)
        print(tree_selection)

        validation = self.validate_commit(number_of_all_selected, len(selected_reporters), len(selected_partners), len(selected_years), len(selected_trade), len(tree_selection))
        if (not validation):
            return

        self.info.setStyleSheet("QLabel { color : black; }")
        self.info.setText('Retrieving data...')
        self.info.repaint()


        if (self.commodities_or_services == 0):
            tree_type = 'C'
        elif (self.commodities_or_services == 1):
            tree_type = 'S'

        res = unc.get_data(selected_reporters, selected_partners, selected_years, selected_trade, type=tree_type, commodities=tree_selection)
        # print(res)

        if (self.profiles_or_time_series == 0):
            output_table = unc.table_profiles(res, selected_years)
        elif (self.profiles_or_time_series == 1):
            output_table = unc.table_time_series(res)
        print(output_table)

        if (output_table is not None):
            self.send("API data", output_table)

            instance_s = ' data instance' if len(output_table) == 1 else ' data instances'
            s = 'Output: ' + str(len(output_table)) + instance_s

            self.info.setStyleSheet("QLabel { color : green; }")
            self.info.setText(s)
        else:
            self.info.setStyleSheet("QLabel { color : black; }")
            self.info.setText('No data for selected query.')


    def validate_commit(self, number_all_selected, rep_len, par_len, years_len, trade_len, tree_len):
        """
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
        """

        if (number_all_selected > 1 or rep_len == 0 or par_len == 0 or years_len == 0 or trade_len == 0 or tree_len == 0):
            self.commit_button.setEnabled(False)
            return False

        self.commit_button.setEnabled(True)
        return True


    def get_checked_trades(self):
        selected_trade = []
        if (self.tf_import):
            selected_trade.append('Import')
        if (self.tf_export):
            selected_trade.append('Export')
        if (self.tf_re_import):
            selected_trade.append('re-Import')
        if (self.tf_re_export):
            selected_trade.append('re-Export')
        return selected_trade


if __name__ == "__main__":
    app = QApplication([])
    w = OW_UN_Comtrade()
    w.show()
    app.exec_()