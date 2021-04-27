# deepops.diff



from .path import DeepPath



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
                              "deepdiff at: %s cannot compare or "
                              "change types: %s and: %s"
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
