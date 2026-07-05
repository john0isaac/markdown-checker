Usage
=====

The library provides the following functions.

.. contents:: Available checks
    :local:

``check_broken_paths``
----------------------

This function ensures that any relative path in your files is working.

Example
~~~~~~~

.. code-block:: bash

    markdown-checker -d . -f check_broken_paths -gu https://github.com/john0isaac/markdown-checker/blob/main/docs/CONTRIBUTING.rst

``check_broken_urls``
---------------------

This function ensures that any web URL in your files is working and returns a
200 status code.

Example
~~~~~~~

.. code-block:: bash

    markdown-checker -d . -f check_broken_urls -gu https://github.com/john0isaac/markdown-checker/blob/main/docs/CONTRIBUTING.rst

``check_urls_locale``
---------------------

This function checks whether a country-specific locale is present in URLs.

Example
~~~~~~~

.. code-block:: bash

    markdown-checker -d . -f check_urls_locale -gu https://github.com/john0isaac/markdown-checker/blob/main/docs/CONTRIBUTING.rst

``check_paths_tracking``
------------------------

This function ensures that any relative path has tracking in it.

Example
~~~~~~~

.. code-block:: bash

    markdown-checker -d . -f check_paths_tracking -gu https://github.com/john0isaac/markdown-checker/blob/main/docs/CONTRIBUTING.rst

``check_urls_tracking``
-----------------------

This function ensures that any URL has tracking in it.

Example
~~~~~~~

.. code-block:: bash

    markdown-checker -d . -f check_urls_tracking -gu https://github.com/john0isaac/markdown-checker/blob/main/docs/CONTRIBUTING.rst

Want to do more?
----------------

Check out the :doc:`Advanced Usage <advanced>` page.
