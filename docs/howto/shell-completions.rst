How to Enable Shell Completions
==================================

Goal: get tab-completion for options and their choices (e.g. ``-f``/
``--func`` and ``-rf``/``--report-format``) in your shell.

markdown-checker is built with `Click <https://click.palletsprojects.com/>`_,
which generates completion support for every option automatically - nothing
needs to be installed separately, but it must be enabled per shell using an
environment variable named after the program: ``markdown-checker`` becomes
``_MARKDOWN_CHECKER_COMPLETE`` (dashes become underscores, uppercased,
prefixed with ``_``).

Bash
------

Add this to ``~/.bashrc``:

.. code-block:: bash

    eval "$(_MARKDOWN_CHECKER_COMPLETE=bash_source markdown-checker)"

Zsh
-----

Add this to ``~/.zshrc``:

.. code-block:: bash

    eval "$(_MARKDOWN_CHECKER_COMPLETE=zsh_source markdown-checker)"

Fish
------

Save the completion script where fish looks for it:

.. code-block:: fish

    _MARKDOWN_CHECKER_COMPLETE=fish_source markdown-checker | source

To make this permanent, save the output to
``~/.config/fish/completions/markdown-checker.fish`` instead of sourcing it
inline:

.. code-block:: fish

    _MARKDOWN_CHECKER_COMPLETE=fish_source markdown-checker > ~/.config/fish/completions/markdown-checker.fish

Verify it worked
------------------

Open a new shell (so the updated rc file is loaded) and try completing a
choice option:

.. code-block:: bash

    markdown-checker -f <TAB>
    # check_broken_paths  check_broken_urls  check_paths_tracking  check_urls_locale  check_urls_tracking

    markdown-checker -rf <TAB>
    # console  github-annotations  json  markdown

File and directory arguments (``SRC``, ``-d``/``--dir``, ``-c``/``--config``)
complete from the filesystem as well.
