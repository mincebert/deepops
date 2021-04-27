# deepops.__init__



"""Deep operations module.

This module contains functions to perform operations on hierarchical
structures of dictionaries, lists and sets.
"""



from .diff import deepdiff
from .filter import deepfilter
from .merge import deepmerge
from .get import deepget
from .removeitems import deepremoveitems
from .setdefault import deepsetdefault



__version__ = "1.7.4"



__all__ = [
    "deepdiff",
    "deepfilter",
    "deepget",
    "deepmerge",
    "deepremoveitems",
    "deepsetdefault",
]
