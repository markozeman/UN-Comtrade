import unittest
from unittest.mock import patch, MagicMock

import re

import Orange
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel

from Orange.widgets.tests.base import WidgetTest


from orangecontrib.uncomtrade.widget.owuncomtrade import OWUNComtrade


class TestOrangeWidget(WidgetTest):
    def setUp(self):
        self.widget = self.create_widget(OWUNComtrade)

    def test_info(self):
        info = self.widget.info
        self.assertIsInstance(info, QLabel)

        info_text = info.text()
        self.assertIsInstance(info_text, str)
        self.assertEqual(info_text, 'Input: no reporters, no partners, no commodities/services')

        model = self.widget.list_model_reporter[2]
        self.assertIsInstance(model, QStandardItemModel)

        item = model.item(0, 0)
        self.assertIsInstance(item, QStandardItem)
        self.assertEqual(item.data(0), 'Africa')
        self.assertTrue(item.isCheckable())
        item = model.item(1, 0).data(0)
        self.assertEqual(item, 'Asia')
        item = model.item(2, 0).data(0)
        self.assertEqual(item, 'Australia & Oceania')
        item = model.item(3, 0).data(0)
        self.assertEqual(item, 'Europe')
        item = model.item(4, 0).data(0)
        self.assertEqual(item, 'North America')
        item = model.item(5, 0).data(0)
        self.assertEqual(item, 'South America')

        item = model.item(0, 0)
        item.setCheckState(Qt.Checked)
        self.assertEqual(self.widget.info.text(), 'Input: 62 reporters, no partners, no commodities/services')

        item = model.item(1, 0)
        item.setCheckState(Qt.Checked)
        self.assertEqual(self.widget.info.text(), 'Input: 128 reporters, no partners, no commodities/services')

        model = self.widget.list_model_partner[2]
        self.assertIsInstance(model, QStandardItemModel)

        item = model.item(3, 0)
        self.assertIsInstance(item, QStandardItem)
        self.assertEqual(item.data(0), 'Europe')
        item.setCheckState(Qt.Checked)
        self.assertEqual(self.widget.info.text(), 'Input: 128 reporters, 54 partners, no commodities/services')

        model = self.widget.tree_model_cs[2]
        self.assertIsInstance(model, QStandardItemModel)

        item = model.item(0, 0)
        self.assertEqual(item.data(0), 'AG2 - All 2-digit HS commodities')
        self.assertFalse(item.hasChildren())
        item.setCheckState(Qt.Checked)
        self.assertEqual(self.widget.info.text(), 'Input: 128 reporters, 54 partners, 1 commodity/service')

        item = model.item(4, 0)
        self.assertEqual(item.data(0), 'TOTAL - Total of all HS commodities')
        self.assertTrue(item.hasChildren())
        item.setCheckState(Qt.Checked)
        self.assertEqual(self.widget.info.text(), 'Input: 128 reporters, 54 partners, 2 commodities/services')
        item.setCheckState(Qt.Unchecked)
        self.assertEqual(self.widget.info.text(), 'Input: 128 reporters, 54 partners, 1 commodity/service')

    def test_commit_button(self):
        self.assertEqual(self.get_output("API data"), None)

        button = self.widget.commit_button
        self.assertEqual(button.isEnabled(), False)

        model = self.widget.list_model_reporter[2]
        item = model.item(0, 0)
        item.setCheckState(Qt.Unchecked)
        child_item = item.child(2)
        child_item.setCheckState(Qt.Checked)
        item = model.item(1, 0)
        item.setCheckState(Qt.Unchecked)

        model = self.widget.list_model_partner[2]
        item = model.item(3, 0)
        item.setCheckState(Qt.Unchecked)
        child_item = item.child(2)
        child_item.setCheckState(Qt.Checked)
        child_item = item.child(4)
        child_item.setCheckState(Qt.Checked)

        model = self.widget.tree_model_cs[2]
        item = model.item(0, 0)
        item.setCheckState(Qt.Unchecked)
        item = model.item(4, 0)
        item.setCheckState(Qt.Checked)

        self.assertEqual(self.widget.info.text(), 'Input: 1 reporter, 2 partners, 1 commodity/service')

        with patch('orangecontrib.uncomtrade.widget.owuncomtrade.OWUNComtrade.get_selected_years',
                   MagicMock(return_value=['2015'])):
            r = self.widget.commit()
        self.assertEqual(type(r), Orange.data.table.Table)
        self.assertEqual(r[0][0], 10784.000)

        str_split = table_to_string(r, 0)
        self.assertEqual(str_split[1], 'Benin')
        self.assertEqual(str_split[2], 'Austria')
        self.assertEqual(str_split[3], 'Export')

        self.assertEqual(button.isEnabled(), True)

        self.assertEqual(self.get_output("API data"), r)


def table_to_string(tab, i):
    str_split = str(tab[i]).split(' ')
    return [re.sub('[,{}\[\]]', '', str_split[i]) for i in range(len(str_split))]



if __name__ == "__main__":
    unittest.main()