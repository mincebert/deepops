# deepops.py
#
# Copyright (C) Robert Franklin <rcf@mince.net>



"""Deep operations module.

This module contains functions to perform operations on hierarchical
structures of dictionaries, lists and sets.
"""



# --- functions ---



class DeepPath(list):
    """This class represents the 'path' into a hierarchy of
    dictionaries, lists and sets.

    It is used for generating string representations of a path for
    error messages, as well as performing checks for specific
    locations.
    """


    def __str__(self):
        """Returns a printable version of the path for use in error
        messages.  This is the path items, each converted to a string
        with repr() (so strings will gain surrounding quotes) and
        enclosed by square brackets (to look like a dictionary index),
        unless the path is empty (i.e. the top of the hierarchy), in
        which case a string representing the top is returned
        ('<root>').

        This string should not be parsed to understand the output but,
        instead, the available methods on it used.
        """

        return "".join(map(lambda i: "[%s]" % repr(i), self)) or "<root>"

    def sub(self, sub_item):
        """Returns a new path, extended by the supplied sub item.  The
        returned path is a copy and does not affect the path the
        method is called on.

        This method is used when calling the deep...() functions
        recursively, to construct the path to the sub item.
        """

        return DeepPath(self + [sub_item])

    def startswith(self, test_path):
        """Returns whether the path starts with (i.e. is contained
        within) the specified path (which can be any iterable of path
        items - typically it's a list of path items as strings).
        """

        # if the length of the test path is greater than my our path,
        # we're definitely not inside it
        if len(test_path) > len(self):
            return False

        # compare items up to the length of the test path (because
        # zip() only returns up to the length of the shortest iterable)
        # with our path to see if they're the same, up to that point -
        # if any don't match at any point, we're not inside it
        for my_item, test_item in zip(self, test_path):
            if my_item != test_item:
                return False

        # if we get here, we're inside the test path
        return True



# deepmerge



def _deepmerge(a, b, replace, list_as_set, change_types, filter_func,
               path=DeepPath()):

    """Backend function for deepmerge() that does the actual work.  It
    is defined privately to not offer the 'path' argument.

    See deepmerge() for information.

    Keyword arguments (in addition to deepmerge()):

    path -- a DeepPath() object representing the position in the
    structures for this call.
    """


    # if a filter function was supplied call it and return without
    # doing anything, if it returns False

    if filter_func:
        if not filter_func(path, a, b):
            return


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


    # if the items being merged are both dictionaries, we work through
    # the items in 'b' to see if they're present in 'a'...

    elif isinstance(a, dict) and isinstance(b, dict):
        for item in b:
            if item in a:
                # the item is present - what we do now depends on the
                # type of the objects...

                if (isinstance(a[item], (list, set, dict))
                    and (isinstance(b[item], (list, set, dict)))):

                    # the item is a compound type (list, set or
                    # dictionary) - recursively merge them
                    #
                    # we don't need to check if they're the same as the
                    # recursive call will do that

                    _deepmerge(a[item], b[item], replace, list_as_set,
                               change_types, filter_func, path.sub(item))

                else:
                    # this isn't a recursive call but we still might
                    # want to filter it

                    if filter_func:
                       if not filter_func(path.sub(item), a[item], b[item]):
                           return


                    if (isinstance(a[item], (list, set, dict))
                      or (isinstance(b[item], (list, set, dict)))):

                        # one of the items is a compound type, but not
                        # the other, so we can't change the type
                        #
                        # (we could technically, but that would be
                        # inconsistent with the behaviour at the root)

                        raise TypeError(
                                "deepmerge at: %s cannot merge compound and "
                                "non-compound types: %s and: %s"
                                    % (path.sub(item), type(a[item]),
                                        type(b[item])))

                    else:
                        # the corresponding items in 'a' and 'b' are
                        # both non-compound types, so we can just
                        # replace it

                        if ((type(a[item]) != type(b[item]))
                            and (not change_types)):

                            raise TypeError(
                                    "deepmerge at: %s can't compare or "
                                    "change types: %s and: %s"
                                        % (path.sub(item), type(a[item]),
                                            type(b[item])))

                        if replace:
                            a[item] = b[item]

            else:
                # this isn't a recursive call but we still might want to
                # filter it

                if filter_func:
                    if not filter_func(path.sub(item), None, b[item]):
                        return


                # the item exists in 'b' but not in 'a', so just add
                # the item to 'a'

                a[item] = b[item]

    else:
        raise TypeError(
                  "deepmerge at: %s incompatible or unhandled types: %s and: "
                  "%s" % (path, type(a), type(b)))



def deepmerge(a, b, replace=True, list_as_set=False, change_types=False,
              filter_func=None):

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
    type (list, set or dictionary) then a TypeError() exception is
    raised.

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

    filter_func -- if this is specified, it is a function which is
    called upon each recursion, receiving the parameters (path [a
    DeepPath object], a, b) and returns a boolean specifying whether to
    act on this level or skip it: it can be used to filter at specific
    levels, perform some other action or raise an exception, if a
    particular level is problematic
    """

    _deepmerge(a, b, replace, list_as_set, change_types, filter_func)



# deepremoveitems



def _deepremoveitems(a, b, filter_func, path=DeepPath()):
    """Backend function for deepremoveitems() that does the actual
    work.  It is defined privately to not offer the 'path' argument.

    See deepremoveitems() for information.

    Keyword arguments (in addition to deepremoveitems()):

    path -- a DeepPath() object representing the position in the
    structures for this call.
    """


    # if a filter function was supplied call it and return without
    # doing anything, if it returns False

    if filter_func:
        if not filter_func(path, a, b):
            return


    # we cannot remove a simple type (one that is not a dictionary,
    # list or set), regardless of the type of object we're removing
    # them from (we'll check for that later), so just abort with an
    # exception

    if not isinstance(b, (list, set, dict)):
        raise TypeError("deepremoveitems at: %s cannot remove simple type: "
                        "%s" % (path, type(b)))


    # if the object we're removing from is a list or set...

    if isinstance(a, (list, set)):
        # ... and the object specifying what to remove is also a list
        # or set, we just remove any items that are in the removal list

        if isinstance(b, (list, set)):
            for item in b:
                if item in a:
                    a.remove(item)


        # ... or, if the object specifying what to remove is a
        # dictionary (since we checked above it was a list, set or
        # dictionary and we've already handled lists and sets), we
        # remove any items matching the keys of the dictionary, as long
        # as the value for that key is 'empty' (is not True)
        #
        # if the dictionary is not empty, we raise an exception as that
        # implies want to remove specific items from another dictionary
        # and this is a list or a set

        else:
            for item in b:
                if not b[item]:
                    if item in a:
                        a.remove(item)

                else:
                    raise ValueError(
                              "deepremoveitems at: %s cannot remove non-"
                              "empty dictionary item from non-dictionary "
                              "type: %s" % (path.sub(item), type(a)))


    # if the object we're removing from is a dictionary...

    elif isinstance(a, dict):
        # ... and the object specifying what to remove is a list or
        # set, we just remove the keys in that list or set, if they
        # exist

        if isinstance(b, (list, set)):
            for item in b:
                if item in a:
                    a.pop(item)


        # ... or, if the object specifying what to remove is also a
        # dictionary (since we know it's a list, set or dictionary and
        # we've already handled lists and sets), what we do depends
        # whether the items in it are empty or not...
        #
        # if the item to remove is empty, we remove the entire
        # corresponding item
        #
        # if the item to remove is not empty, we recursively process
        # the two dictionaries to remove the corresponding items

        else:
            for item in b:
                if item in a:
                    if not b[item]:
                        a.pop(item)
                    else:
                        _deepremoveitems(a[item], b[item], filter_func,
                                         path.sub(item))


    # if the object we're removing from is not one of the above -
    # probably a simple type - we're raise an exception as that's not
    # supported

    else:
        raise TypeError(
                  "deepremoveitems at: %s cannot remove compound type: %s "
                  "from non-compound type: %s" % (path, type(b), type(a)))



def deepremoveitems(a, b, filter_func=None):
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

    filter_func -- if this is specified, it is a function which is
    called upon each recursion, receiving the parameters (path [a
    DeepPath object], a, b) and returns a boolean specifying whether to
    act on this level or skip it: it can be used to filter at specific
    levels, perform some other action or raise an exception, if a
    particular level is problematic
    """

    _deepremoveitems(a, b, filter_func)



# deepdiff



def _deepdiff(a, b, list_as_set, change_types, filter_func, path=DeepPath()):
    """Backend function for deepdiff() that does the actual work.  It
    is defined privately to not offer the 'path' argument.

    See deepdiff() for information.

    Keyword arguments (in addition to deepdiff()):

    path -- a DeepPath() object representing the position in the
    structures for this call.
    """


    # if a filter function was supplied call it and return without
    # doing anything, if it returns False

    if filter_func:
        if not filter_func(path, a, b):
            return None, None


    # raise errors if either of the supplied objects are not compound
    # types

    if not isinstance(a, (list, set, dict)):
        raise TypeError("deepdiff at: %s invalid type for 'from' ('a') "
                        "object: %s" % (path, type(a)))

    if not isinstance(b, (list, set, dict)):
        raise TypeError("deepdiff at: %s invalid type for 'to' ('b') object: "
                        "%s" % (path, type(b)))


    # if they're the same, there's nothing to remove, nothing to update

    if a == b:
        return None, None


    if isinstance(a, list) and isinstance(b, list):
        if list_as_set:
            # we're treating lists as sets, so we find the differences,
            # ignoring the order

            return (
                # remove everything in 'a' that is not in 'b'
                [ i for i in a if i not in b ],

                # update (add) everything in 'b' that is not in 'a'
                [ i for i in b if i not in a ])

        else:
            # with lists as lists, the order is important and they're
            # different, so we just remove everything in 'a' and add
            # everything in 'b'

            return a, b


    elif isinstance(a, set) and isinstance(b, set):
        # remove everything in 'a' not in 'b' and add everything in 'b'
        # not in 'a'

        return a.difference(b), b.difference(a)


    elif isinstance(a, dict) and isinstance(b, dict):
        # we delete all the items where the key is in 'a' but not in
        # 'b' (the value in the returned dictionary is None as we want
        # to remove the entire key, not items from within it, which is
        # how deepremoveitems() handles this)
        #
        # this also initialises the remove_items dictionary (perhaps to
        # an empty dictionary, if there are none)

        remove_items = { i: None for i in a if i not in b }


        # we add all the items where the key is in 'b' but not in 'a',
        # including their value
        #
        # this also initialises the update_items dictionary (perhaps to
        # an empty dictionary, if there are none)

        update_items = { i: b[i] for i in b if i not in a }


        # finally, work through the keys that are common to both
        # dictionaries...

        for item in set(a).intersection(b):
            # if this item is a compound type in both dictionaries...
            #
            # (we don't need to check the types are the same as this
            # will be done by the recursive call)

            if (isinstance(a[item], (list, set, dict))
                and isinstance(b[item], (list, set, dict))):

                # recursively calculate the differences, getting the
                # subitems to be removed and updated within it

                remove_subitems, update_subitems = (
                    _deepdiff(a[item], b[item], list_as_set, change_types,
                              filter_func, path.sub(item)))


                # if there were subitems to remove or update (they'd be
                # None, or empty structures - something that tests as
                # False - if they were the same), store those in the
                # dictionaries of replies

                if remove_subitems:
                    remove_items[item] = remove_subitems

                if update_subitems:
                    update_items[item] = update_subitems


            # the item is a simple type in one or both of the
            # dictionaries...

            else:
                # this isn't a recursive call but we still might want
                # to filter it

                if filter_func:
                    if not filter_func(
                               path.sub(item), a[item], b[item]):

                        continue


                # the types must match, unless we're allowed to
                # change_types

                if (type(a[item]) != type(b[item])) and (not change_types):
                    raise TypeError(
                              "deepmerge at: %s cannot compare or change "
                              "types: %s and: %s"
                                  % (path.sub(item), type(a[item]),
                                     type(b[item])))


                # store the new value for the item in the update
                # dictionary

                if a[item] != b[item]:
                    update_items[item] = b[item]


        return remove_items, update_items


    # if we get here, the items are of different types (but are both
    # compound types, as we checked for that earlier): raise a
    # TypeError

    raise TypeError(
              "deepdiff at %s: unable to change from type: %s to type: %s"
                  % (path, type(a), type(b)))



def deepdiff(a, b, list_as_set=False, change_types=False, filter_func=None):
    """Recursively compare two nested compound objects - 'a' and 'b' -
    returning what needs to be done to transform 'a' into 'b'.  Both
    'a' and 'b' must be compound types (a list, set or dictionary) at
    the top level and can contain further compound types or simple
    types, nested within.

    The return value is a 2-tuple: ('remove_items', 'update_items'):

    'remove_items' is what needs to be removed from 'a' (i.e. items
    that are in 'a' that are not in 'b').

    'update_items' is what (then) needs to be added or modified to 'a'
    (i.e. items that are in 'b' that are not in 'a', or items where the
    value in 'b' is different from 'a').

    Calling 'deepremoveitems(a, remove_items)' followed by
    'deepmerge(a, update_items)' should result in 'a' being equal to
    'b' by value.  See those functions for more information.

    Note, however, the items to be removed/updated are not copied
    before being returned so will be the same object from 'a' or 'b'.
    This may cause trouble if they're modified or passed directly to
    deepremoveitems() or deepmerge() as it will break the interation
    process, as the same object will be iterated over twice,
    simultaneously.  To do this, they shoould be copy.deepcopy()ed
    first (or similar).

    The behaviour of this function depends on the type of object being
    compared (which must be the same for 'a' and 'b'):

    For lists, if they differ (at all - either in terms of order or the
    actual items) all items in 'a' are removed and all the items in 'b'
    updated (i.e. 'added'), effectively replacing the entire list,
    unless list_as_set is set to True, in which case they are handled
    as per a set (although the result will still be a list).  No
    attempt is made to transform the list, leaving the common items in
    place, as this would be tricky regarding the ordering.

    For sets, the items in 'a' that are not in 'b' are removed, and the
    items in 'b' that are not in 'a' are updated (added).

    For dictionaries, the process is more complicated: keys in 'a' that
    are not in 'b' are removed; keys in 'b' that are not in 'a' are
    updated (added).  Where a key exists in both, if the value is a
    compound type, a recursive call is made.  If the value is a simple
    type, it is updated (replaced), as long as it is of the same type
    (according to type()) - a TypeError is raised otherwise - unless
    change_types is set to True.

    Keyword arguments:

    a -- the 'from' object

    b -- the 'to' object

    list_as_set -- this specifies whether lists should be treated as
    lists (= False), resulting in [potentially] duplicated items, or as
    sets (= True), which will ignore the order of the list (although
    note that it won't filter out duplicates already in 'a' and leaves
    the type as a list).

    change_types -- this specifies whether a value can be changed from
    one simple type to another (for example, a string replacing an
    integer); if this is False and a difference is encountered, a
    TypeError will be raised.  This will not change between compound
    types (for example a list changing to a set).

    filter_func -- if this is specified, it is a function which is
    called upon each recursion, receiving the parameters (path [a
    DeepPath object], a, b) and returns a boolean specifying whether to
    act on this level or skip it: it can be used to filter at specific
    levels, perform some other action or raise an exception, if a
    particular level is problematic
    """

    return _deepdiff(a, b, list_as_set, change_types, filter_func)
