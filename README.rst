micro-finance
=============
Full featured completely customizable software for Microfinanace Institutes
This is MicroPyramid opensource initiative for microfinanace management.
This is full featured software to manage microfinanace Institute(s).

.. image:: https://travis-ci.org/MicroPyramid/micro-finance.svg?branch=master
   :target: https://travis-ci.org/MicroPyramid/micro-finance

.. image:: https://readthedocs.org/projects/micro-finance/badge/?version=latest
   :target: https://readthedocs.org/projects/micro-finance/?badge=latest
   :alt: Documentation Status

.. image:: https://coveralls.io/repos/MicroPyramid/micro-finance/badge.png?branch=master
   :target: https://coveralls.io/r/MicroPyramid/micro-finance?branch=master
   
.. image:: https://landscape.io/github/MicroPyramid/micro-finance/master/landscape.svg
   :target: https://landscape.io/github/MicroPyramid/micro-finance/master
   :alt: Code Health

head to http://micro-finance.readthedocs.org/ for latest documentation

How to deploy?
==============
* clone this repository
* setup virtualenv and install requirements from requirements.txt
* do necessary changes to settings.py
* configure nginx with uwsgi for production on server or you can run inside virtualenv for development purposes.

You can try it by hosting on your own or deploy to Heroku with a button click.

Deploy To Heroku:

.. image:: https://www.herokucdn.com/deploy/button.svg
   :target: https://heroku.com/deploy?template=https://github.com/MicroPyramid/micro-finance

You can view the sample here `https://test-microfinance-app.herokuapp.com/`_

Credentials to MicroFinance Dashboard:

  * **Username:** Admin001
  * **Password:** admin001

Visit our Django Web Development page `Here`_

.. _Here: https://micropyramid.com/django-development-services/
.. _https://test-microfinance-app.herokuapp.com/: https://test-microfinance-app.herokuapp.com/

# c019 2021-02-14T10:18:06 refactor initial project files

# c021 2021-02-18T13:40:20 update the bootstrap config

# c023 2021-02-23T11:02:34 test(bootstrap): initial project files

# c026 2021-03-02T10:35:55 fix(bootstrap): startup settings

# c031 2021-03-13T10:30:30 refactor initial project files

# c036 2021-03-24T16:25:05 polish the deployment entrypoint
