# deepops.py
#
# Copyright (C) Robert Franklin <rcf@mince.net>



"""Deep operations module.

This module contains functions to perform operations on hierarchical
structures of dictionaries, lists and sets.
"""


__version__ = "1.3 (2020-03-20)"



# --- functions ---



def _printable_path(path):
    """Returns a printable version of a path to an object in a
    hierarchy for use in error messages.  This is the supplied path,
    unless it's empty (i.e. the top of the hierarchy), in which case a
    string representing the top is returned.
    """

    return path or "<top>"



def _sub_path(path, sub_item):
    """Returns a new path string, extended by the supplied sub item.
    The sub item is converted to a string with repr(), to add quotes
    around strings, if they are the item.
    """

    return path + ("[%s]" % repr(sub_item))



# deepmerge



def _deepmerge(a, b, replace, list_as_set, change_types, path=""):
    """Backend function for deepmerge() that does the actual work.  It
    is defined privately to not offer the 'path' argument.

    See deepmerge() for information.

    Keyword arguments (in addition to deepmerge()):

    path -- a string giving the 'path' through the structures so far
    (in recursive calls to this function), in the format
    '[...][...]...'; it is used when a problem is encountered, to
    report where the issue lies; the default is the top level
    """


    # if the items being merged are both lists, what we do depends on
    # the list_as_set option...

    if isinstance(a, list) and isinstance(b, list):
        if list_as_set:
            # it's enabled, so we treat the list 'a' as a set and only
            # add items from 'b' to it if they don't exist already

            a.extend([ i for i in b if i not in a ])

        else:

            # it's disabled, so we just append the corresponding list
            # in 'b' to 'a' (potentially adding duplicates)

            a.extend(b)


    # if the items being merged are both sets, we just add the missing
    # items in 'b'

    elif isinstance(a, set) and isinstance(b, set):
        a.update(b)


    # if the items being merged are both dictionaries, we work through the
    # items in 'b' to see if they're present in 'a'...

    elif isinstance(a, dict) and isinstance(b, dict):
        for item in b:
            if item in a:
                # the item is present - what we do now depends on the type of
                # the objects...

                if (isinstance(a[item], (list, set, dict))
                    and (isinstance(b[item], (list, set, dict)))):

                    # the item is a compound type (list, set or dictionary) -
                    # recursively merge them
                    #
                    # we don't need to check if they're the same as the
                    # recursive call will do that

                    _deepmerge(a[item], b[item], replace, list_as_set,
                               change_types, _sub_path(path, item))

                elif (isinstance(a[item], (list, set, dict))
                      or (isinstance(b[item], (list, set, dict)))):

                    # one of the items is a compound type, but not the other,
                    # so we can't change the type
                    #
                    # (we could technically, but that would be inconsistent
                    # with the behaviour at the top level)

                    raise TypeError(
                              "deepmerge at: %s cannot merge compound and "
                              "non-compound types: %s and: %s"
                                  % (_sub_path(path, item), type(a[item]),
                                     type(b[item])))

                else:
                    # the corresponding items in 'a' and 'b' are both
                    # non-compound types, so we can just replace it

                    if ((type(a[item]) != type(b[item]))
                        and (not change_types)):

                        raise TypeError(
                                  "deepmerge at: %s can't compare or change "
                                  "types: %s and: %s"
                                      % (_sub_path(path, item),
                                         type(a[item]), type(b[item])))

                    if replace:
                        a[item] = b[item]

            else:
                # the item exists in 'b' but not in 'a', so just add the item
                # to 'a'

                a[item] = b[item]

    else:
        raise TypeError(
                  "deepmerge at: %s incompatible or unhandled types: %s and: "
                  "%s" % (_printable_path(path), type(a), type(b)))



def deepmerge(a, b, replace=True, list_as_set=False, change_types=False):
    """Recursively merge two nested compound objects - 'a' and 'b': the
    items in 'b' are merged into 'a', in place, modifying 'a'.  Both
    'a' and 'b' must be compound types (a list, set or dictionary) at
    the top level and can contain further compound types or simple
    types, nested within.

    What happens for any particular item depends on its type:

    For lists, the corresponding items in 'b' are appended.  This will
    create duplicates, if they're in both lists (unless list_as_set is
    enabled).

    For sets, the result is the union of the items in 'a' and 'b'.

    For dictionaries (including the top-level call), the merge is
    applied recursively, with items in 'b' added to 'a' by merging
    recursively.  Other types are merged according to the above rules.

    For simple types (integers, strings, etc.), the value in 'b'
    replaces the value in 'a'.

    If one of the values is a simple type and the other is a compound
    type (list, set or dictionary) then a TypeError() exception is raised.

    Keyword arguments:

    a -- the 'initial' dictionary: this dictionary will be modified in
    place to contain the merged items from 'b'

    b -- the 'additional' dictionary: items in this dictionary will be
    added to 'a', taking precedence over them

    replace -- this indicates whether a simple type in 'a' should be
    replaced by a value in 'b'; this effectively determines whether
    values in 'a' or 'b' have precedence

    list_as_set -- this specifies whether lists should be treated as
    lists (= False), resulting in [potentially] duplicated items, or as
    sets (= True), which will only add items from 'b' if they don't
    already exist in 'a' (although note that it won't filter out
    duplicates already in 'a')

    change_types -- this specifies whether a value of one simple type
    can replace that of a different (simple) type (for example, a
    string replacing an integer)
    """

    _deepmerge(a, b, replace, list_as_set, change_types)



# deepremoveitems



def _deepremoveitems(a, b, path=""):
    """Backend function for deepremoveitems() that does the actual
    work.  It is defined privately to not offer the 'path' argument.

    See deepremoveitems() for information.

    Keyword arguments (in addition to deepremoveitems()):

    path -- a string giving the 'path' through the structures so far
    (in recursive calls to this function), in the format
    '[...][...]...'; it is used when a problem is encountered, to
    report where the issue lies; the default is the top level
    """


    # we cannot remove a simple type (one that is not a dictionary, list or
    # set), regardless of the type of object we're removing them from (we'll
    # check for that later), so just abort with an exception

    if not isinstance(b, (list, set, dict)):
        raise TypeError("deepremoveitems at: %s cannot remove simple type: "
                        "%s" % (_printable_path(path), type(b)))


    # if the object we're removing from is a list or set...

    if isinstance(a, (list, set)):
        # ... and the object specifying what to remove is also a list or set,
        # we just remove any items that are in the removal list

        if isinstance(b, (list, set)):
            for item in b:
                if item in a:
                    a.remove(item)


        # ... or, if the object specifying what to remove is a dictionary
        # (since we checked above it was a list, set or dictionary and we've
        # already handled lists and sets), we remove any items matching the
        # keys of the dictionary, as long as the value for that key is 'empty'
        # (is not True)
        #
        # if the dictionary is not empty, we raise an exception as that
        # implies want to remove specific items from another dictionary and
        # this is a list or a set

        else:
            for item in b:
                if not b[item]:
                    if item in a:
                        a.remove(item)

                else:
                    raise ValueError(
                              "deepremoveitems at: %s cannot remove "
                              "non-empty dictionary item: %s from "
                              "non-dictionary type: %s"
                                  % (_printable_path(path), repr(item),
                                     type(a)))


    # if the object we're removing from is a dictionary...

    elif isinstance(a, dict):
        # ... and the object specifying what to remove is a list or set, we
        # just remove the keys in that list or set, if they exist

        if isinstance(b, (list, set)):
            for item in b:
                if item in a:
                    a.pop(item)


        # ... or, if the object specifying what to remove is also a
        # dictionary (since we know it's a list, set or dictionary and we've
        # already handled lists and sets), what we do depends whether the
        # items in it are empty or not...
        #
        # if the item to remove is empty, we remove the entire corresponding
        # item
        #
        # if the item to remove is not empty, we recursively process the two
        # dictionaries to remove the corresponding items

        else:
            for item in b:
                if item in a:
                    if not b[item]:
                        a.pop(item)
                    else:
                        _deepremoveitems(a[item], b[item],
                                         _sub_path(path, item))


    # if the object we're removing from is not one of the above - probably a
    # simple type - we're raise an exception as that's not supported

    else:
        raise TypeError(
                  "deepremoveitems at: %s incompatible or unhandled types: "
                  "%s and: %s" % (_printable_path(path), type(a), type(b)))



def deepremoveitems(a, b):
    """Recursively remove items from nested object 'b' from nested
    object 'a', modifying object 'a' in place.  Both 'a' and 'b' must
    be compound types (a list, set or dictionary) at the top level and
    can contain further compound types or simple types, nested within.

    What happens depends on the types of corresponding items in 'a' and
    'b':

    Where 'a' is a list or set, the items are removed, if they are
    present in 'b'.  'b' can be a list, set or dictionary but, if the
    corresponding item in 'b' is a dictionary, it must be empty.

    Where 'a' is a dictionary, 'b' can either be a list or set (in
    which case, the items in 'b' are removed from 'a'), or a
    dictionary.  In the latter case, if the corresponding item in 'b'
    is empty, the item in 'a' is removed entirely; if not, the items in
    each dictionary are processed recursively.

    The reason for handling empty dictionaries as a special case is to
    allow a mix of removing entire items (which could be done with a
    list or set for 'b') and removing specific items within other items
    (which requires a dictionary).  Note that an empty list or set
    cannot be used instead of an empty dictionary: they will remove
    no items from the corresponding item.

    If there are mismatches, violating the above rules, a TypeError()
    or ValueError() exception is raised.

    Keyword arguments:

    a -- the object to have items removed from it: this can be a
    dictionary, list or set and will be modified in place to remove the
    corresponding items in 'b'

    b -- the object specifying what items are to be removed from 'a';
    it doesn't need to match the type of 'a' but there are certain
    constraints, described above, which it must fit within, at each
    level
    """

    _deepremoveitems(a, b)
