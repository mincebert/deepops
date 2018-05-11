#!/usr/bin/env python3

# deepops-example.py - test example for deepops

from __future__ import print_function
import deepops

# something complex to merge into

x = {"a": "x",
     "b": 2,
     "c": ["x"],
     "d": {"m": "x",
           "n": 3,
           "p": [1, 2],
           "q": {"t": [1]}},
     "e": {7, 8}}

# something to complex to merge into above

y = {"a": "y",
     "b": 6,
     "c": ["y", "x"],
     "d": {"m": "y",
           "o": 4,
           "p": [2, 3],
           "q": {"t": [2]}},
     "e": {8, 9}}

# something complex to remove

z = {"a": {},
     "b": {},
     "c": {"x": {}},
     "t": {"n": {}}}

# do some testing, printing the sources and outputs

print("MERGE >")
print("  into:", x)
print("  from:", y)
deepops.deepmerge(x, y, list_as_set=True)
print("MERGED >")
print(" ", x)

print()

print("REMOVE >")
print("  from:", x)
print("  items:", z)
deepops.deepremoveitems(x, z)
print("REMOVED >")
print(" ", x)
