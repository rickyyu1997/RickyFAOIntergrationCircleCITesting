Python Netsuite
===============
Netsuite Python Toolkit for SuiteTalk SOAP API.

Note: README.md was created to describe our integration specific approaches to this package as as an integration
adapter. This file only covers the basic package setup instructions.

Installation
------------
.. code:: python

    pip3 install git+git://github.com/fmalina/python-netsuite.git#egg=python-netsuite

Example usage
-------------
Copy :code:`ns_config.py.txt` into :code:`ns_config.py` and update with your credentials.

.. code:: python

    from netsuite.client import client
    from netsuite.api.customer import get_customer

    # print names of first 100 customers
    for internal_id in range(100):
        customer = get_customer(internal_id)
        if customer:
            print(customer.firstName, customer.lastName)

NetSuite Documentation
----------------------
* `SuiteTalk Documentation <http://www.netsuite.com/portal/developers/resources/suitetalk-documentation.shtml>`_
* `Schema Browser (CashSale example) <http://www.netsuite.com/help/helpcenter/en_US/srbrowser/Browser2016_2/schema/record/cashsale.html?mode=package>`_

Development
-----------

* Get Netsuite WSDL export to look at

.. code:: bash

    mkdir archive
    python3 -mzeep https://webservices.sandbox.netsuite.com/wsdl/v2016_1_0/netsuite.wsdl > archive/wsdl.txt
    # improve formatting
    sed -i -e 's/, /, \n          /g' archive/wsdl.txt
    less archive/wsdl.txt

* Add Netsuite models you need to work with based on WSDL to :code:`netsuite/service.py`.
* Add functions to get, create, lookup... these model instances to :code:`netsuite/api/[model].py`.
* Add tests to :code:`tests.py`. Run tests using :code:`./tests.py`