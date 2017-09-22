# deepops.py
#
# Copyright (C) Robert Franklin <rcf@mince.net>



"""Deep operations module.

This module contains functions to perform operations on hierarchical
structures of dictionaries, lists and sets.
"""



__version__ = "1.0 (2017-09-22)"



# --- internal functions ---



def _strquote(s):
    """Returns the string representation of an object, surrounding it
    with single quotes, if it's a string (to make it clear it's a
    string and enclose spaces).

    This module uses it in various exception messages.

    Keywork arguments:

    s -- the item to be returned, string or other
    """

    return ("'%s'" % s) if isinstance(s, str) else s



# --- external functions ---



# deepmerge



def _deepmerge(a, b, replace, list_as_set, path):
    """Backend function for deepmerge() that does the actual work.  It
    is defined privately to not offer the 'path' argument.

    See deepmerge() for information.

    Keyword arguments (in addition to deepmerge()):

    path -- this is a list of keys identifying the position in the
    hierarchy of dictionaries being merged: it is used when raising an
    exception to explain where the problem lies
    """


    # if the items being merged are both lists, what we do depends on
    # the list_as_set option...

    if isinstance(a, list) and isinstance(b, list):
        # ... if it's enabled, we treat the list 'a' as a set and only
        # add items from 'b' to it if they don't exist already

        if list_as_set:
            for item in b:
                if item not in a:
                    a.append(item)


        # ... or, if it's disabled, we just append the corresponding
        # list in 'b' to 'a' (potentially adding duplicates)

        else:
            a.extend(b)


    # if the items being merged are both sets, we just add the missing
    # items in 'b'

    elif isinstance(a, set) and isinstance(b, set):
        a.update(b)


    # if the items being merged are both dictionaries, we work through the
    # items in 'b' in see if they're present in 'a'...

    elif isinstance(a, dict) and isinstance(b, dict):
        for item in b:
            if item in a:
                # the item is present - what we do now depends on the type of
                # that object (we only check 'a')...

                if (isinstance(a[item], dict) or
                    isinstance(a[item], list) or
                    isinstance(a[item], set)):

                    # the item is a compound type (dictionary, list or set) -
                    # recursively merge them
                    #
                    # we don't need to check if the two items are different
                    # types as the function will do that itself

                    _deepmerge(
                        a[item], b[item], replace, list_as_set, path + [item])


                else:
                    # the item in 'a' is a simple type - check the
                    # corresponding item in 'b' is also simple and replace it
                    # (if that's enabled), otherwise raise an exception

                    if (isinstance(b[item], dict) or
                        isinstance(b[item], list) or
                        isinstance(b[item], set)):

                        raise(TypeError("cannot replace simple type %s with "
                                        "non-simple type %s at %s" %
                                            (_strquote(a[item]),
                                             _strquote(b[item]),
                                             ".".join(path + [item]))))

                    if replace:
                        a[item] = b[item]


            else:
                # the item exists in 'b' but not in 'a', so just add the item
                # to 'a'

                a[item] = b[item]


    else:
        raise(TypeError("merging incompatible or illegal types %s and %s at "
                        "%s" % (_strquote(a), _strquote(b),
                                ".".join(path + [item]))))



def deepmerge(a, b, replace=True, list_as_set=False):
    """Merge two dictionaries - 'a' and 'b' - the items in 'b' are
    merged into 'a', in place, modifying 'a'.

    What happens for any particular item depends on its type:

    For lists, the corresponding items in 'b' are appended.  This will
    create duplicates, if they're in both lists.

    For sets, the result is the union of the items in 'a' and 'b'.

    For simple types (integers, strings, etc.), the value in 'b'
    replaces the value in 'a'.

    For dictionaries (including the toplevel call), the merge is
    applied recursively, with items in 'b' are added to 'a' by merging
    recursively.  Other types are merged according to the above rules.

    If one of the values is a simple type and the other is a compound
    type (list or dictionary) then a TypeError() exception is raised.

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
    """

    _deepmerge(a, b, replace, list_as_set, [])



# deepremoveitems



def _deepremoveitems(a, b, path):
    """Backend function for deepremoveitems() that does the actual
    work.  It is defined privately to not offer the 'path' argument.

    See deepremoveitems() for information.

    Keyword arguments (in addition to deepremoveitems()):

    path -- this is a list of keys identifying the position in the
    hierarchy of dictionaries being processed: it is used when raising
    an exception to explain where the problem lies
    """


    # we cannot remove a simple type (one that is not a dictionary, list or
    # set), regardless of the type of object we're removing them from (we'll
    # check for that later), so just abort with an exception

    if not(isinstance(b, dict) or isinstance(b, list) or isinstance(b, set)):
        raise(TypeError("cannot remove simple type %s at %s" %
                            (_strquote(b), ".".join(path) if path else ".")))


    # if the object we're removing from is a list or set...

    if isinstance(a, list) or isinstance(a, set):
        # ... and the object specifying what to remove is also a list or set,
        # we just remove any items that are in the removal list

        if isinstance(b, list) or isinstance(b, set):
            for item in b:
                if item in a:
                    a.remove(item)


        # ... or, if the object specifying what to remove is a dictionary, we
        # remove any items matching the keys of the dictionary, as long as the
        # dictionary is empty
        #
        # if the dictionary is not empty, we raise an exception as that implies
        # want to remove specific items from another dictionary (we have to
        # allow empty dictionaries to provide a way to remove a complete item
        # from the dictionary)

        elif isinstance(b, dict):
            for item in b:
                if not(b[item]):
                    if item in a:
                        a.remove(item)
                else:
                    raise(ValueError("cannot remove non-empty dictionary item "
                                     "%s from non-dictionary %s at %s" %
                                         (_strquote(item), _strquote(a),
                                          ".".join(path) if path else ".")))


    # if the object we're removing from is a dictionary...

    elif isinstance(a, dict):
        # ... and the object specifying what to remove is a list or set, we
        # just remove the keys in that list or set, if they exist

        if isinstance(b, list) or isinstance(b, set):
            for item in b:
                if item in a:
                    a.pop(item)


        # ... or, if the object specifying what to remove is also a dictionary,
        # we either remove the entire key, if the corresponding dictionary item
        # is empty
        #
        # if the item is not empty, we recursively process the two dictionaries
        # to remove the corresponding items

        elif isinstance(b, dict):
            for item in b:
                if item in a:
                    if not(b[item]):
                        a.pop(item)
                    else:
                        _deepremoveitems(a[item], b[item], path + [item])


    # if the object we're removing from is not one of the above - probably a
    # simple type - we're raise an exception as that's not supported

    else:
        raise(TypeError("cannot remove items from simple type %s at %s" %
                            (a, ".".join(path) if path else ".")))


def deepremoveitems(a, b):
    """Remove items 'b' from a object 'a', modifying object 'a' in
    place.  Both 'a' and 'b' must be compound types (a dictionary, list
    or set).

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

    _deepremoveitems(a, b, [])
