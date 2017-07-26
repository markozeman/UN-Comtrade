import unittest
from unittest.mock import patch, MagicMock

import re

import Orange
from Orange.widgets.tests.base import WidgetTest
from PyQt5.QtCore import QModelIndex, Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QApplication, QLabel
from Orange.widgets import gui

from orangecontrib.uncomtrade.widget.owuncomtrade import OWUNComtrade, FindFilterProxyModel, ContinentCountries


class TestContinentCountries(unittest.TestCase):
    cc = ContinentCountries()

    def test_number_of_countries(self):
        self.assertEqual(len(self.cc.EU_rep), 52)
        self.assertEqual(len(self.cc.EU_par), 54)

        self.assertEqual(len(self.cc.AF_rep), 62)
        self.assertEqual(len(self.cc.AF_par), 64)

        self.assertEqual(len(self.cc.AS_rep), 66)
        self.assertEqual(len(self.cc.AS_par), 69)

        self.assertEqual(len(self.cc.AU_rep), 19)
        self.assertEqual(len(self.cc.AU_par), 26)

        self.assertEqual(len(self.cc.NA_rep), 43)
        self.assertEqual(len(self.cc.NA_par), 49)

        self.assertEqual(len(self.cc.SA_rep), 14)
        self.assertEqual(len(self.cc.SA_par), 15)


class TestFindFilterProxyModel(unittest.TestCase):

    def test_filter_proxy_model(self):
        ffpm = FindFilterProxyModel()
        t_f = ffpm.filterAcceptsRow(0, QModelIndex())
        self.assertIsInstance(ffpm, FindFilterProxyModel)
        self.assertTrue(t_f)

        with patch('orangecontrib.uncomtrade.widget.owuncomtrade.FindFilterProxyModel.filterAcceptsRowItself',
                   MagicMock(return_value=False)):
            with patch('orangecontrib.uncomtrade.widget.owuncomtrade.FindFilterProxyModel.hasAcceptedChildren',
                       MagicMock(return_value=False)):
                t_f = ffpm.filterAcceptsRow(0, QModelIndex())
        self.assertFalse(t_f)

        with patch('orangecontrib.uncomtrade.widget.owuncomtrade.FindFilterProxyModel.filterAcceptsRowItself',
                   MagicMock(return_value=False)):
            with patch('orangecontrib.uncomtrade.widget.owuncomtrade.FindFilterProxyModel.hasAcceptedChildren',
                       MagicMock(return_value=True)):
                t_f = ffpm.filterAcceptsRow(0, QModelIndex())
        self.assertTrue(t_f)


class TestWidget(unittest.TestCase):
    app = QApplication([])
    widget = OWUNComtrade()

    cc = ContinentCountries()

    commodities_services_box = gui.widgetBox(widget.controlArea, "Exchange Type")

    def test_init(self):
        self.assertEqual(self.widget.name, 'UN Comtrade')
        self.assertEqual(self.widget.priority, 10)
        self.assertFalse(self.widget.want_main_area)

    def test_tree_view(self):
        tree_model = self.widget.make_tree_view('ser', self.widget.on_item_changed, self.commodities_services_box)
        self.assertEqual(len(tree_model), 3)

    def test_item_changed(self):
        r = self.widget.on_item_changed()
        self.assertEqual(r, 0)

        with patch('orangecontrib.uncomtrade.widget.owuncomtrade.OWUNComtrade.checked_tree_items',
                   MagicMock(return_value=[1])):
            r = self.widget.on_item_changed()
        self.assertEqual(r, 0)

        with patch('orangecontrib.uncomtrade.widget.owuncomtrade.OWUNComtrade.checked_tree_items',
                   MagicMock(return_value=[1, 2])):
            r = self.widget.on_item_changed()
        self.assertEqual(r, 0)

        with patch('orangecontrib.uncomtrade.widget.owuncomtrade.OWUNComtrade.get_selected_years',
                   MagicMock(return_value=[x for x in range(55)])):
            r = self.widget.on_item_changed()
        self.assertEqual(r, 0)

        with patch('orangecontrib.uncomtrade.widget.owuncomtrade.OWUNComtrade.set_info_string',
                   MagicMock(return_value=[256, 277, 1])):
            r = self.widget.on_item_changed()
        self.assertEqual(r, 0)

        with patch('orangecontrib.uncomtrade.widget.owuncomtrade.OWUNComtrade.cs_tree_constructed',
                   MagicMock(return_value=False)):
            r = self.widget.on_item_changed()
        self.assertEqual(r, None)

        data = self.cc.rep_continents
        eu = None
        asia = None
        for key, values in sorted(data.items()):
            continent = QStandardItem(key)
            if (key == 'Europe'):
                continent.setCheckable(True)
                continent.setCheckState(Qt.Checked)
                eu = continent
            elif (key == 'Asia'):
                continent.setCheckable(True)
                continent.setCheckState(Qt.Unchecked)
                asia = continent

            for country in values:
                country = QStandardItem(country)
                country.setCheckable(True)
                continent.setChild(continent.rowCount(), country)

        r = self.widget.on_continent_item_changed(eu)
        self.assertEqual(r, 0)

        r = self.widget.on_continent_item_changed(asia)
        self.assertEqual(r, 0)

    def test_tree_change(self):
        self.widget.commodities_or_services = 0
        r = self.widget.change_tree_view(self.commodities_services_box)
        model = self.widget.tree_model_cs[2]
        first_item = model.item(0, 0).data(0)
        self.assertEqual(first_item, 'AG2 - All 2-digit HS commodities')
        self.assertEqual(r, 0)

        self.widget.commodities_or_services = 1
        r = self.widget.change_tree_view(self.commodities_services_box)
        model = self.widget.tree_model_cs[2]
        first_item = model.item(0, 0).data(0)
        self.assertEqual(first_item, 'ALL - All EBOPS 2002 Services')
        self.assertEqual(r, 0)

    def test_trade_flow_check(self):
        self.widget.tf_import = 0
        self.widget.tf_re_import = 0
        self.widget.tf_re_export = 0
        self.widget.tf_export = 1
        trade = self.widget.get_checked_trades()
        self.assertEqual(trade, ['Export'])

        self.widget.tf_export = 0
        trade = self.widget.get_checked_trades()
        self.assertEqual(trade, [])

        self.widget.tf_import = 1
        self.widget.tf_re_import = 1
        self.widget.tf_re_export = 1
        self.widget.tf_export = 1
        trade = self.widget.get_checked_trades()
        self.assertEqual(trade, ['Import', 'Export', 're-Import', 're-Export'])

    def test_commit(self):
        r = self.widget.commit()
        self.assertEqual(r, None)

        with patch('orangecontrib.uncomtrade.widget.owuncomtrade.OWUNComtrade.checked_tree_items',
                   MagicMock(return_value=[x for x in range(256)])):
            r = self.widget.commit()
        self.assertEqual(r, None)

        with patch('orangecontrib.uncomtrade.widget.owuncomtrade.OWUNComtrade.checked_tree_items',
                   MagicMock(return_value=[x for x in range(277)])):
            r = self.widget.commit()
        self.assertEqual(r, None)

        with patch('orangecontrib.uncomtrade.widget.owuncomtrade.OWUNComtrade.get_selected_years',
                   MagicMock(return_value=[x for x in range(55)])):
            r = self.widget.commit()
        self.assertEqual(r, None)

        r = self.widget.validate_commit(1, 2, 2, 3, 3, 1)
        self.assertTrue(r)

        r = self.widget.validate_commit(3, 2, 2, 3, 3, 1)
        self.assertFalse(r)

        lst = [{'period': 2010, 'TradeValue': 1974694665, 'rgDesc': 'Export', 'ptTitle': 'Austria',
                'cmdDescE': 'All Commodities', 'rtTitle': 'Slovenia'},
               {'period': 2010, 'TradeValue': 2959491560, 'rgDesc': 'Export', 'ptTitle': 'Italy',
                'cmdDescE': 'All Commodities', 'rtTitle': 'Slovenia'},
               {'period': 2011, 'TradeValue': 2245197879, 'rgDesc': 'Export', 'ptTitle': 'Austria',
                'cmdDescE': 'All Commodities', 'rtTitle': 'Slovenia'},
               {'period': 2011, 'TradeValue': 3449419690, 'rgDesc': 'Export', 'ptTitle': 'Italy',
                'cmdDescE': 'All Commodities', 'rtTitle': 'Slovenia'}]

        self.widget.profiles_or_time_series = 0
        with patch('orangecontrib.uncomtrade.widget.owuncomtrade.OWUNComtrade.validate_commit',
                   MagicMock(return_value=True)):
            with patch('orangecontrib.uncomtrade.uncomtradeapi.UNComtrade.get_data', MagicMock(return_value=lst)):
                with patch('orangecontrib.uncomtrade.widget.owuncomtrade.OWUNComtrade.get_selected_years',
                           MagicMock(return_value=['2010', '2011'])):
                    r = self.widget.commit()
        self.assertEqual(type(r), Orange.data.table.Table)
        self.assertEqual(r[0][0], 1974694665.000)
        self.assertEqual(r[0][1], 2245197879.000)
        self.assertEqual(r[1][0], 2959491560.000)
        self.assertEqual(r[1][1], 3449419690.000)

        str_split_1 = table_to_string(r, 0)
        self.assertEqual(str_split_1[2], 'Slovenia')
        self.assertEqual(str_split_1[3], 'Austria')
        self.assertEqual(str_split_1[4], 'Export')
        str_split_2 = table_to_string(r, 1)
        self.assertEqual(str_split_2[2], 'Slovenia')
        self.assertEqual(str_split_2[3], 'Italy')
        self.assertEqual(str_split_2[4], 'Export')

        self.widget.profiles_or_time_series = 1
        with patch('orangecontrib.uncomtrade.widget.owuncomtrade.OWUNComtrade.validate_commit',
                   MagicMock(return_value=True)):
            with patch('orangecontrib.uncomtrade.uncomtradeapi.UNComtrade.get_data', MagicMock(return_value=lst)):
                with patch('orangecontrib.uncomtrade.widget.owuncomtrade.OWUNComtrade.get_selected_years',
                           MagicMock(return_value=['2010', '2011'])):
                    r = self.widget.commit()
        self.assertEqual(type(r), Orange.data.table.Table)
        self.assertEqual(r[0][0], 1974694665.000)
        self.assertEqual(r[1][0], 2959491560.000)
        self.assertEqual(r[2][0], 2245197879.000)
        self.assertEqual(r[3][0], 3449419690.000)

        str_split_1 = table_to_string(r, 0)
        self.assertEqual(str_split_1[1], 'Slovenia')
        self.assertEqual(str_split_1[2], 'Austria')
        self.assertEqual(str_split_1[3], 'Export')
        self.assertEqual(str_split_1[6], '2010')
        str_split_2 = table_to_string(r, 1)
        self.assertEqual(str_split_2[1], 'Slovenia')
        self.assertEqual(str_split_2[2], 'Italy')
        self.assertEqual(str_split_2[3], 'Export')
        self.assertEqual(str_split_2[6], '2010')
        str_split_3 = table_to_string(r, 2)
        self.assertEqual(str_split_3[1], 'Slovenia')
        self.assertEqual(str_split_3[2], 'Austria')
        self.assertEqual(str_split_3[3], 'Export')
        self.assertEqual(str_split_3[6], '2011')
        str_split_4 = table_to_string(r, 3)
        self.assertEqual(str_split_4[1], 'Slovenia')
        self.assertEqual(str_split_4[2], 'Italy')
        self.assertEqual(str_split_4[3], 'Export')
        self.assertEqual(str_split_4[6], '2011')

        with patch('orangecontrib.uncomtrade.widget.owuncomtrade.OWUNComtrade.validate_commit',
                   MagicMock(return_value=True)):
            with patch('orangecontrib.uncomtrade.uncomtradeapi.UNComtrade.get_data', MagicMock(return_value=lst)):
                with patch('orangecontrib.uncomtrade.widget.owuncomtrade.OWUNComtrade.get_selected_years',
                           MagicMock(return_value=['2010', '2011'])):
                    with patch('orangecontrib.uncomtrade.uncomtradeapi.UNComtrade.table_time_series', MagicMock(return_value=None)):
                        r = self.widget.commit()
        self.assertEqual(r, 1)


def table_to_string(tab, i):
    str_split = str(tab[i]).split(' ')
    return [re.sub('[,{}\[\]]', '', str_split[i]) for i in range(len(str_split))]


if __name__ == '__main__':
    unittest.main()
