import unittest
from code.UNComtrade import UNComtrade

unc = UNComtrade()

class TestPossibleParameters(unittest.TestCase):
    def test_years(self):
        should_be = [1962, 1963, 1964, 1965, 1966, 1967, 1968, 1969, 1970, 1971, 1972, 1973, 1974, 1975, 1976, 1977,
                     1978, 1979, 1980, 1981, 1982, 1983, 1984, 1985, 1986, 1987, 1988, 1989, 1990, 1991, 1992, 1993,
                     1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009,
                     2010, 2011, 2012, 2013, 2014, 2015, 2016, 'all']
        self.assertEqual(unc.years(), should_be)

    def test_reporters(self):
        reporters = unc.reporters()
        self.assertEqual(reporters[0], 'All')
        self.assertEqual(len(reporters), 255)

    def test_partners(self):
        partners = unc.partners()
        self.assertEqual(partners[1], 'World')
        self.assertEqual(len(partners), 293)

    def test_commodities_HS(self):
        comm_HS = unc.commodities_HS()
        self.assertEqual(comm_HS[1], 'TOTAL - Total of all HS commodities')
        self.assertEqual(len(comm_HS), 7656)

    def test_commodities_ST(self):
        comm_ST = unc.commodities_ST()
        self.assertEqual(comm_ST[2], 'AG1 - All 1-digit SITC commodities')
        self.assertEqual(len(comm_ST), 5993)

    def test_commodities_BEC(self):
        comm_BEC = unc.commodities_BEC()
        self.assertEqual(comm_BEC[0], 'ALL - All BEC categories')
        self.assertEqual(len(comm_BEC), 34)

    def test_services(self):
        services = unc.services()
        self.assertEqual(services[3], '1.1 Sea transport')
        self.assertEqual(len(services), 119)

    def test_trade_flows(self):
        trade_flows = unc.trade_flows()
        self.assertEqual(trade_flows[1], 'Import')
        self.assertEqual(len(trade_flows), 5)



class TestAPICalls(unittest.TestCase):

    def test_restrictions(self):
        # max five reporters
        r = unc.call_api(['Croatia', 'Italy', 'Austria', 'Hungary', 'Germany', 'France'], 'Slovenia', ['all'], 'Export')
        self.assertEqual(r, 3)

        # max five partners
        r = unc.call_api('Slovenia', ['Croatia', 'Italy', 'Austria', 'Hungary', 'Germany', 'France'], ['all'], 'Export')
        self.assertEqual(r, 3)

        # max five years
        r = unc.call_api('Slovenia', ['Croatia', 'Italy', 'Austria', 'Hungary'], [2007,2008,2009,2010,2011,2012,2013], 'Export')
        self.assertEqual(r, 3)

        # max 20 commodities
        comm = ['01 - Live animals', '0101 - Live horses, asses, mules and hinnies', '010110 - Live horses/asses/mules/hinnies: pure-bred breeding animals',
                '010111 - Horses, live pure-bred breeding', '010119 - Horses, live except pure-bred breeding', '010120 - Asses, mules and hinnies, live',
                '010121 - Live animals // Live horses, asses, mules and hinnies. // - Horses : // -- Pure-bred breeding animals',
                '010129 - Live animals // Live horses, asses, mules and hinnies. // - Horses : // -- Other',
                '010130 - Live animals // Live horses, asses, mules and hinnies. // -Asses',
                '010190 - Live horses/asses/mules/hinnies other than pure-bred breeding animals',
                '0102 - Live bovine animals', '010210 - Bovine animals, live pure-bred breeding',
                '010221 - Live animals // Live bovine animals. // - Cattle : // -- Pure-bred breeding animals',
                '010229 - Live animals // Live bovine animals. // - Cattle : // -- Other',
                '010231 - Live animals // Live bovine animals. // - Buffalo : // -- Pure-bred breeding animals',
                '010239 - Live animals // Live bovine animals. // - Buffalo : // -- Other', '010290 - Bovine animals, live, except pure-bred breeding',
                '0103 - Live swine', '010310 - Swine, live pure-bred breeding', '010391 - Swine, live except pure-bred breeding < 50 kg',
                '010392 - Swine, live except pure-bred breeding > 50 kg', '0104 - Live sheep and goats', '010410 - Sheep, live']

        r = unc.call_api('Slovenia', ['Croatia', 'Italy'], [2007, 2008, 2009], 'Export', commodities=comm)
        self.assertEqual(r, 3)

        # max 1 'all' in reporters, partners and years
        r = unc.call_api('all', ['Croatia', 'Italy'], 'all', 'Export')
        self.assertEqual(r, 2)


    def test_parameter_all(self):
        # if parameter 'all' is chosen, others don't matter
        r_1 = unc.call_api(['all'], ['Croatia', 'Italy'], 2015, 'Import', max_values=100000)
        r_2 = unc.call_api(['Slovenia', 'all'], ['Croatia', 'Italy'], 2015, 'Import', max_values=100000)
        self.assertEqual(len(r_1), len(r_2))

        r_1 = unc.call_api('Slovenia', ['all', 'Italy'], 2015, 'Import', max_values=100000)
        r_2 = unc.call_api('Slovenia', ['all'], 2015, 'Import', max_values=100000)
        self.assertEqual(len(r_1), len(r_2))


    def test_optional_parameters(self):
        # annual vs monthly
        r = unc.call_api('Slovenia', ['Croatia', 'Italy'], [2014, 2015], 'Export', freq='A')
        self.assertNotEqual(r, 1)
        self.assertNotEqual(r, 2)
        self.assertNotEqual(r, 3)

        r = unc.call_api('Slovenia', ['Croatia', 'Italy'], [2014, 2015], 'Export', freq='M')
        self.assertEqual(len(r), 0)

        r = unc.call_api('Slovenia', ['Croatia', 'Italy'], [201401, 201503], 'Export', freq='M')
        self.assertNotEqual(len(r), 0)

        # services
        r = unc.call_api('All', 'Slovenia', [2015], 'Export', type='S')
        self.assertEqual(len(r), 5)

        # max values
        r = unc.call_api('Slovenia', ['Croatia', 'Italy'], [2015], 'Export', max_values=-5)
        self.assertEqual(r, 1)
        r = unc.call_api('Slovenia', ['Croatia', 'Italy'], [2015], 'Export', max_values=150000)
        self.assertEqual(r, 1)
        r = unc.call_api('Slovenia', ['Croatia', 'Italy'], [2013, 2014, 2015], 'Export', max_values=100)
        self.assertEqual(len(r), 100)

        # classification
        r = unc.call_api('Slovenia', ['Croatia', 'Italy'], [2013, 2014, 2015], 'Export', classification='WRONG')
        self.assertEqual(r, 1)
        r = unc.call_api('Slovenia', ['Croatia', 'Italy'], [2013, 2014, 2015], 'Export', classification='HS')
        self.assertNotEqual(len(r), 0)


    def test_wrong_inputs(self):
        # non-existing country
        r = unc.call_api('Lovenia', ['Croatia', 'Italy'], [2013, 2014, 2015], 'Export')
        self.assertEqual(r, 3)

        # non-existing year
        r = unc.call_api('Lovenia', ['Croatia', 'Italy'], [2013, 2014, 2150], 'Export')
        self.assertEqual(r, 3)

        # non-existing trade_flows
        r = unc.call_api('Lovenia', ['Croatia', 'Italy'], [2013, 2014, 2150], 'Import-Export')
        self.assertEqual(r, 3)

        # wrong input for optional parameters
        r = unc.call_api('Slovenia', ['Croatia', 'Italy'], [2013, 2014, 2015], 'Export', type='L')
        self.assertEqual(r, 1)
        r = unc.call_api('Slovenia', ['Croatia', 'Italy'], [2013, 2014, 2015], 'Export', freq='L')
        self.assertEqual(r, 1)
        r = unc.call_api('Slovenia', ['Croatia', 'Italy'], [2013, 2014, 2015], 'Export', head='L')
        self.assertEqual(r, 1)
        r = unc.call_api('Slovenia', ['Croatia', 'Italy'], [2013, 2014, 2015], 'Export', format='L')
        self.assertEqual(r, 1)
        r = unc.call_api('Slovenia', ['Croatia', 'Italy'], [2013, 2014, 2015], 'Export', classification='L')
        self.assertEqual(r, 1)
        r = unc.call_api('Slovenia', ['Croatia', 'Italy'], [2013, 2014, 2015], 'Export', commodities='L')
        self.assertEqual(r, 3)
        r = unc.call_api('Slovenia', ['Croatia', 'Italy'], [2013, 2014, 2015], 'Export', max_values='L')
        self.assertEqual(r, 1)


    def test_random_calls(self):
        r = unc.call_api('Slovenia', ['Italy'], 2015, 'Import', max_values=1000)
        self.assertEqual(len(r), 95)

        r = unc.call_api('Slovenia', ['France'], [2010, 2015], 'Import', max_values=1000)
        self.assertEqual(len(r), 187)

        # r = unc.call_api('USA', ['France'], [2000, 2001], 'Import', max_values=1000)
        # self.assertEqual(len(r), 194)
        #
        # r = unc.call_api('USA', ['France'], [2000, 2001], 'All', max_values=1000)
        # self.assertEqual(len(r), 572)
        #
        # r = unc.call_api('Slovenia', ['Germany'], [2010], 'All', max_values=1000)
        # self.assertEqual(len(r), 189)

        # r = unc.call_api('Slovenia', ['Cuba'], [2010], 'Import', max_values=1000)
        # self.assertEqual(len(r), 10)
        # self.assertEqual(r[0]['TradeValue'], 67035)
        # self.assertEqual(r[1]['TradeValue'], 54)

        # r = unc.call_api('Slovenia', ['Denmark'], [2011], 'Import', max_values=1000)
        # self.assertEqual(len(r), 82)
        # self.assertEqual(r[0]['TradeValue'], 46934)
        # self.assertEqual(r[1]['TradeValue'], 918870)

        # r = unc.call_api('Slovenia', ['Sweden'], [2011], 'Import', max_values=1000)
        # self.assertEqual(len(r), 75)
        # self.assertEqual(r[0]['TradeValue'], 772133)
        # self.assertEqual(r[1]['TradeValue'], 108040)

        r = unc.call_api('Norway', ['Finland'], [2015], 'Import', max_values=1000)
        self.assertEqual(len(r), 96)
        self.assertEqual(r[0]['TradeValue'], 35226)
        self.assertEqual(r[1]['TradeValue'], 1486708)

        # r = unc.call_api('Norway', ['Finland', 'Denmark'], [2014, 2015], 'All', max_values=1000)
        # self.assertEqual(len(r), 750)
        # self.assertEqual(r[0]['TradeValue'], 10095648)
        # self.assertEqual(r[1]['TradeValue'], 972794)



if __name__ == '__main__':
    unittest.main()

