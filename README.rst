fantasy_basketball
==================

.. image:: https://pypip.in/v/Fantasy_Basketball/badge.png
   :target: https://pypi.python.org/pypi/Fantasy_Basketball
   :alt: Latest Version

.. image:: https://landscape.io/github/dwwkelly/fantasy_basketball/master/landscape.png
   :target: https://landscape.io/github/dwwkelly/fantasy_basketball/master
      :alt: Code Health

.. image:: https://travis-ci.org/dwwkelly/fantasy_basketball.svg?branch=master
   :target: https://travis-ci.org/dwwkelly/fantasy_basketball
      :alt: Build Status

This package will fetch NBA stas from basketball-reference.com, parse 
the statistics into pandas dataframes, then visualize the statistics.

Installation
============

This package can be installed with either pip,::

   $ pip install Fantasy_Basketball

Or with directly from the source code::

   $ git checkout https://github.com/dwwkelly/fantasy_basketball
   $ cd fantasy_basketball
   $ python setup.py install


Dependencies
============

* `Click <http://click.pocoo.org/3/>`_
* `numpy <http://www.numpy.org/>`_
* `matplotlib <matplotlib.org>`_
* `pandas <http://pandas.pydata.org/>`_
* `jinja2 <http://jinja.pocoo.org/>`_
* `pycurl <http://pycurl.sourceforge.net/>`_
* `beautifulsoup4 <http://www.crummy.com/software/BeautifulSoup/>`_
 
Usage
=====

A library and a user application are provided, you can use
the user application like this::

   $ FB_Manager download --year 2013 --teams --draft
   $ FB_Manager process --year 2013 --teams
   $ FB_Manager plot --year 2013

Data Storage
============

The fantasy_basketball library creates several directories::

   ~/.fantasy_basketball/plots
   ~/.fantasy_basketball/processed_data
   ~/.fantasy_basketball/raw_data

Each directory contains directories that are either the data type or
the year for the data, *e.g.*::

   ~/.fantasy_basketball/processed_data/2013
   ~/.fantasy_basketball/raw_data/teams/2013

The raw data is all HTML files, the processed data is pickle files
that contain pandas dataframes, the plots directory contains either
eps images or png images.

You can import the dataframes yourself for your own analysis with ipython::

   In [1]: import pandas as pd

   In [2]: import os

   In [3]: data_dir = os.path.expanduser('~/.fantasy_basketball/processed_data/2013/team_data.pkl')

   In [4]: df = pd.read_pickle(data_dir)

   In [5]: df.shape
   Out[5]: (347, 55)



TODO
====

* Config file.
* Generate HTML from data.
* Download and process more statistics.
* Deal with infer_types warning for pandas > 0.14

Thanks
======
Thanks to `basketball-reference.com <basketball-reference.com>`_ for providing the statistics
