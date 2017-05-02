## Usage of library

### Required installations:
* Python 3
* Orange 3

### Usage examples:

If you are in _UN-Comtrade/code_ directory and start Python console, you can get started with library.  

First you need to import module:
```python
from UNComtrade import UNComtrade
```

Then you create an instance of the class, for example:
```python
unc = UNComtrade()
```

After that you can retrieve which options are available for some parameter.  
```python
# get all possible years
unc.years()

# get all possible reporters
unc.reporters()

# get all possible partners
unc.partners()

# get all possible HS commodities
unc.commodities_HS()

# get all possible ST commodities
unc.commodities_ST()

# get all possible BEC commodities
unc.commodities_BEC()

# get all possible services
unc.services()

# get all possible trade regimes
unc.trade_flows()
```

#### Parameters to call UN Comtrade API are following:
##### required (parameter order is important)
* reporters

  _options:_ you can see list of all reporters with call unc.reporters()  
  
* partners

  _options:_ you can see list of all partners with call unc.partners()  
  
* time_period

  _options:_ you can see list of all years with call unc.years(), if freq='M' you can type e.g. 201102, which means February 2011  
  
* trade_flows

  _options:_ you can see list of all trade regimes with call unc.trade_flows()  

##### optional
* type

  _options:_ 'C' or 'S' (commodities or services)  
  _default:_ 'C'
 
* freq

  _options:_ 'A' or 'M' (annually or monthly)  
  _default:_ 'A'
  
* classification

  _options:_ 'HS' or 'ST' or 'BEC'  
  _default:_ 'HS'
  
* commodities

  _options:_ you can see list of all HS commodities with call unc.commodities_HS()  
  _default:_ 'AG2 - All 2-digit HS commodities'
  
* max_values

  _options:_ [1, 100.000]  
  _default:_ 10
  
* head

  _options:_ 'H' or 'M' (human or machine readable)  
  _default:_ 'H'
  
* format

  _options:_ 'json' or 'csv'  
  _default:_ 'json'


### Restrictions on parameters
__reporters, partners, time_period__ --> you can choose up to 5 for each, but only one of those three can be set to all  
__commodities__ --> you can choose up to 20 commodities per call


### Restrictions on REST API
__API calls__ --> you can call API one time per second and 100 times per hour.


### Examples
If you want to know the first 10 records of import to Slovenia from all countries in years 2010 and 2012, your call should be:  
```python
unc.call_api('Slovenia', 'All', [2010, 2012], 'Import')
```

If you want to know first 1000 records of export from Croatia to Slovenia in all years, your call should be:  
```python
unc.call_api('Croatia', 'Slovenia', 'all', 'Export', max_values=1000)
```

If you want to know all records of USA import of live animals in 2015, your call should be:  
```python
unc.call_api('USA', 'All', 2015, 'Import', commodities='01 - Live animals', max_values=100000)
```
