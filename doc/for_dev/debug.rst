Debugging
=========

To debug the command-line applicaiton ``transonic`` for source-to-source
compilation issues, one approach is to invoke it via ``pdb``. For example,
let's say you tried to use ``transonic`` as follows but errored::

    transonic --no-compile my_code.py

To debug, replace ``transonic`` with ``python -m pdb -m transonic.run``::

    python -m pdb -m transonic.run --no-compile my_code.py

Then type ``c`` followed by the ENTER key to continue to the error. You can, of
course, use other `pdb commands`_.

.. _pdb commands: https://docs.python.org/3/library/pdb.html#debugger-commands

.. note::

    If no error is thrown while using ``--no-compile`` option and it fails
    without it, it is most likely a bug in backend. Report it upstream in the
    backend's issue tracker.

