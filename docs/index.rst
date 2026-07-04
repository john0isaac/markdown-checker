markdown-checker
================

Markdown link validation reporting tool. It provides a couple of functions to
validate relative paths and web URLs.

User's Guide
------------

The user guide is the best place to start if you are new to Markdown Checker.
It provides a comprehensive overview of the library, including installation
instructions, usage examples, and troubleshooting tips.

.. toctree::
   :maxdepth: 2
   :caption: Contents

   usage
   advanced
   automate

Requirements
~~~~~~~~~~~~

You will need the following prerequisites in order to use this library:

- Python >= 3.11
- `httpx2 <https://pypi.org/project/httpx2/>`_
- `click <https://pypi.org/project/click/>`_

Installation
~~~~~~~~~~~~

.. code-block:: bash

   pip install markdown-checker

1, 2, 3 - How To
~~~~~~~~~~~~~~~~

1. Run ``pip install markdown-checker``.
2. Run ``markdown-checker -d {src} -f {func} -gu {url}``. Replace ``{src}``
   with the directory you want to analyze, ``{func}`` with one of the
   available functions such as ``check_broken_paths``, and ``{url}`` with the
   full URL to your contribution guide.
3. The output will be displayed in the terminal and in a ``comment.md`` file.


API Reference
-------------

If you are looking for information on a specific function, class or
method, this part of the documentation is for you.

.. toctree::
    :maxdepth: 2
    :caption: API Reference
    :glob:

    api/*

Additional Notes
----------------

.. toctree::
    :maxdepth: 1

    Contributing <CONTRIBUTING>
    Code of Conduct <CODE_OF_CONDUCT>
    changes
    license
