UN Comtrade
===============

.. figure:: icons/uncomtrade.jpg

UN Comtrade

Signals
-------

**Inputs**:

-  (None)

**Outputs**:

-  **Data**

   Attribute-valued data set (Orange.data.Table).


Description
-----------

This widget offers possibility to get data from UN Comtrade REST API
in such form that you are able to use it with other Orange widgets.

.. figure:: images/widget-stamped.png

1. Choose whether you want your output as countries profiles or time series.

2. Filter and select reporting country/countries.

3. Filter and select partner country/countries.

4. Filter and select years.

5. Check wanted reporter trade flows.

6. Choose whether you want to select commodities or services.

7. Filter and select commodities or services.

8. Press *Commit* button to get data and send signal to output.


Examples
--------

In the schema below, the most common use of the widget is presented.
First, the data is read and a CN2 rule classifier is trained. We are using
*titanic* data set for the rule constrution. The rules
are then viewed using the :doc:`Rule Viewer <../visualize/cn2ruleviewer>`. To explore different CN2
algorithms and understand how adjusting parameters influences the
learning process, **Rule Viewer** should be kept open and in sight, while
setting the CN2 learning algorithm (the presentation will be updated
promptly).

.. figure:: images/CN2-Viewer-Example1.png

Selecting a rule outputs filtered data instances. These can be viewed in
a :doc:`Data Table <../data/datatable>`.