rdata
=====

|build-status| |docs| |coverage| |pypi| |zenodo|

Read R datasets from Python.

..
	Github does not support include in README for dubious security reasons, so
	we copy-paste instead. Also Github does not understand Sphinx directives.
	.. include:: docs/index.rst
	.. include:: docs/simpleusage.rst

The package rdata offers a lightweight way to import R datasets/objects stored
in the ".rda" and ".rds" formats into Python.
Its main advantages are:

- It is a pure Python implementation, with no dependencies on the R language or
  related libraries.
  Thus, it can be used anywhere where Python is supported, including the web
  using `Pyodide <https://pyodide.org/>`_.
- It attempt to support all R objects that can be meaningfully translated.
  As opposed to other solutions, you are no limited to import dataframes or
  data with a particular structure.
- It allows users to easily customize the conversion of R classes to Python
  ones.
  Does your data use custom R classes?
  Worry no longer, as it is possible to define custom conversions to the Python
  classes of your choosing.
- It has a permissive license (MIT). As opposed to other packages that depend
  on R libraries and thus need to adhere to the GPL license, you can use rdata
  as a dependency on MIT, BSD or even closed source projects.
	
Installation
============

rdata is on PyPi and can be installed using :code:`pip`:

.. code::

   pip install rdata

It is also available for :code:`conda` using the :code:`conda-forge` channel:

.. code::

   conda install -c conda-forge rdata

Documentation
=============

The documentation of rdata is in
`ReadTheDocs <https://rdata.readthedocs.io/en/latest/>`_.
	
Simple usage
============

Read a R dataset
----------------

The common way of reading an R dataset is the following one:

>>> import rdata

>>> parsed = rdata.parser.parse_file(rdata.TESTDATA_PATH / "test_vector.rda")
>>> converted = rdata.conversion.convert(parsed)
>>> converted
{'test_vector': array([1., 2., 3.])}
    
This consists on two steps: 

#. First, the file is parsed using the function
   `parse_file`. This provides a literal description of the
   file contents as a hierarchy of Python objects representing the basic R
   objects. This step is unambiguous and always the same.
#. Then, each object must be converted to an appropriate Python object. In this
   step there are several choices on which Python type is the most appropriate
   as the conversion for a given R object. Thus, we provide a default
   `convert` routine, which tries to select Python
   objects that preserve most information of the original R object. For custom
   R classes, it is also possible to specify conversion routines to Python
   objects.
   
Convert custom R classes
------------------------

The basic `convert` routine only constructs a
`SimpleConverter` objects and calls its
`convert` method. All arguments of
`convert` are directly passed to the
`SimpleConverter` initialization method.

It is possible, although not trivial, to make a custom
`Converter` object to change the way in which the
basic R objects are transformed to Python objects. However, a more common
situation is that one does not want to change how basic R objects are
converted, but instead wants to provide conversions for specific R classes.
This can be done by passing a dictionary to the
`SimpleConverter` initialization method, containing
as keys the names of R classes and as values, callables that convert a
R object of that class to a Python object. By default, the dictionary used
is `DEFAULT_CLASS_MAP`, which can convert
commonly used R classes such as `data.frame` and `factor`.

As an example, here is how we would implement a conversion routine for the
factor class to `bytes` objects, instead of the default conversion to
Pandas `Categorical` objects:

>>> import rdata

>>> def factor_constructor(obj, attrs):
...     values = [bytes(attrs['levels'][i - 1], 'utf8')
...               if i >= 0 else None for i in obj]
...
...     return values

>>> new_dict = {
...         **rdata.conversion.DEFAULT_CLASS_MAP,
...         "factor": factor_constructor
...         }

>>> parsed = rdata.parser.parse_file(rdata.TESTDATA_PATH
...                                  / "test_dataframe.rda")
>>> converted = rdata.conversion.convert(parsed, new_dict)
>>> converted
{'test_dataframe':   class  value
    1     b'a'      1
    2     b'b'      2
    3     b'b'      3}


.. |build-status| image:: https://github.com/vnmabus/rdata/actions/workflows/main.yml/badge.svg?branch=master
    :alt: build status
    :scale: 100%
    :target: https://github.com/vnmabus/rdata/actions/workflows/main.yml

.. |docs| image:: https://readthedocs.org/projects/rdata/badge/?version=latest
    :alt: Documentation Status
    :scale: 100%
    :target: https://rdata.readthedocs.io/en/latest/?badge=latest
    
.. |coverage| image:: http://codecov.io/github/vnmabus/rdata/coverage.svg?branch=develop
    :alt: Coverage Status
    :scale: 100%
    :target: https://codecov.io/gh/vnmabus/rdata/branch/develop
    
.. |pypi| image:: https://badge.fury.io/py/rdata.svg
    :alt: Pypi version
    :scale: 100%
    :target: https://pypi.python.org/pypi/rdata/
    
.. |zenodo| image:: https://zenodo.org/badge/DOI/10.5281/zenodo.6382237.svg
    :alt: Zenodo DOI
    :scale: 100%
    :target: https://doi.org/10.5281/zenodo.6382237