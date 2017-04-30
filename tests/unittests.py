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
    pass



if __name__ == '__main__':
    unittest.main()