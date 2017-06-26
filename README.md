## Data mining of UN Comtrade database

#### UN Comtrade
United Nations International Trade Statistics Database provides trading data between more than 170 countries over the world.
UN Comtrade is the largest database of trading data with more than 3 billion data records since the year 1962.  
Database has option to discover data on trading goods or services.
It offers publicly accessible API which can be used with some constraints - 1 API call per second, maximum 50.000 records per query.

#### UN Comtrade API 
Comtrade API offers many parameters to search the database, such as time period, reporters, partners, trade flows and commodities.  
This repository offers code for accessing Comtrade API through Python function and objects.

#### How to use this library
Required installation and usage examples are explained in README file in code directory.

#### Installation of Orange widget
To install widget in Orange you have clone or download GitHub project.  
In terminal move to _/code/Orange_widget_ directory and run this command:
```sh
pip install -e .
```

Now open your Orange from terminal with:
```sh
python -m Orange.canvas
```
The new widget should appear under the section UNComtrade.