# deepops.removeitems



from .path import DeepPath



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
        raise TypeError("deepremoveitems at: %s cannot remove simple type: %s"
                            % (path, type(b)))


    # if the object we're removing from is a list or set...

    if isinstance(a, (list, set)):
        # ... and the object specifying what to remove is also a list or
        # set, we just remove any items that are in the removal list

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
                              "deepremoveitems at: %s cannot remove "
                              "non-empty dictionary item from non-"
                              "dictionary type: %s"
                                  % (path.sub(item), type(a)))


    # if the object we're removing from is a dictionary...

    elif isinstance(a, dict):
        # ... and the object specifying what to remove is a list or set,
        # we just remove the keys in that list or set, if they exist

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
                  "deepremoveitems at: %s cannot remove compound type: "
                  "%s from non-compound type: %s"
                      % (path, type(b), type(a)))



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
