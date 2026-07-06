markdown-checker
================

Markdown link validation reporting tool. It provides a couple of functions to
validate relative paths and web URLs.

Installation
~~~~~~~~~~~~

.. code-block:: bash

   pip install markdown-checker

Requires Python >= 3.11.

New here?
---------

Start with the :doc:`tutorial`: install the tool and run it against a small
sample project to see exactly what it does.

.. toctree::
   :maxdepth: 1

   tutorial

Have a specific task?
----------------------

The :doc:`howto/index` guides cover selecting files, skipping domains/URLs,
configuring via ``pyproject.toml``, tuning rate limits, choosing a report
format, and running in GitHub Actions.

.. toctree::
   :maxdepth: 2
   :caption: How-to Guides

   howto/index

Looking something up?
------------------------

The :doc:`reference/index` pages are dry, complete descriptions of every
CLI option, what each check flags, configuration keys, report formats, and
exit codes.

.. toctree::
   :maxdepth: 2
   :caption: Reference

   reference/index

Want to understand how it works?
-----------------------------------

The :doc:`explanation/index` pages cover the URL-checking pipeline and how
links are detected and classified.

.. toctree::
   :maxdepth: 2
   :caption: Explanation

   explanation/index

API Reference
-------------

If you are looking for information on a specific function, class or
method, this part of the documentation is for you.

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/index

Additional Notes
----------------

.. toctree::
    :maxdepth: 1

    Contributing <CONTRIBUTING>
    Code of Conduct <CODE_OF_CONDUCT>
    changes
    license
