PYTHON DEEPOPS MODULE
=====================

This module contains some functions for performing "deep" operations on
standard Python data structures - dictionaries/lists/sets:

* `deepmerge()` - merges two dictionaries/lists/sets, including all
  sub-items, e.g. items to lists and sets, missing keys/items to
  dictionaries, optionally replacing clashing simple types.
* `deepremoveitems()` - removes items (simple types, or whole
  dictionaries/lists/sets) from specified locations within a complex
  data structure.

The module was developed and used under Python 3.4 but seems to work OK
in basic testing under 2.7.

Author
------

Robert Franklin, UK  <rcf@mince.net>
