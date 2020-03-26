PYTHON DEEPOPS MODULE
=====================

This module contains some functions for performing "deep" operations on
standard Python "compound" data structures - lists/sets/dictionaries:

* `deepmerge()` - merges two compound structures, including all
  sub-items, e.g. items to lists and sets, missing keys/items to
  dictionaries, optionally replacing clashing simple types.
* `deepremoveitems()` - removes items (simple types, or whole compound
  structures) from within another compound data structure.
* `deepdiff()` - compares two compound structures and returns a tuple
  of items to be removed and items to be updated: these could be passed
  to `deepremoveitems()` and `deepmerge()`, respectively, to transform
  one into the other (although note that they would need to be
  `deepcopy()`ed first).

The module was developed and used under Python 3.4-3.7 but seems to
work OK in basic testing under 2.7.

Author
------

Robert Franklin, UK  <rcf@mince.net>
