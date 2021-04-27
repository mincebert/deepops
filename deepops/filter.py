# deepops.filter



from .path import DeepPath



def _deepfilter(a, b, path=DeepPath()):
    """Backend function for deeprfilter() that does the actual
    work.  It is defined privately to not offer the 'path' argument.

    See deepfilter() for information.

    Keyword arguments (in addition to deepfilter()):

    path -- a DeepPath() object representing the position in the
    structures for this call.
    """


    # we cannot filter a simple type (one that is not a dictionary,
    # list or set), regardless of the type of object we're filtering
    # against (we'll check for that later), so just abort with an
    # exception

    if not isinstance(b, (list, set, dict)):
        raise TypeError("deepfilter at: %s cannot filter simple type: %s"
                            % (path, type(b)))


    # if the object we're filtering from is a list or set...

    if isinstance(a, (list, set)):
        # ... and the object specifying what to filter is also a list or
        # set, we just include any items that are in the filter set

        if isinstance(b, (list, set)):
            r = [ item for item in a if item in b ]


        # ... or, if the object specifying what to filter is a
        # dictionary (since we checked above it was a list, set or
        # dictionary and we've already handled lists and sets), we
        # filter any items matching the keys of the dictionary, as long
        # as the value for that key is 'empty' (is not True)
        #
        # if the dictionary is not empty, we raise an exception as that
        # implies want to filter specific items from another dictionary
        # and this is a list or a set

        else:
            r = []
            for item in a:
                if item in b:
                    if not b[item]:
                        r.append(item)

                    else:
                        raise ValueError(
                                "deepfilter at: %s cannot filter non-"
                                "empty dictionary item from non-"
                                "dictionary type: %s"
                                    % (path.sub(item), type(a)))


        # we did all the work above, building a list (to preserve
        # duplicates and order) - but, if the source type was a set,
        # convert it here, else it's a list, so return it directly

        if isinstance(a, set):
            r = set(r)


    # if the object we're filtering is a dictionary...

    elif isinstance(a, dict):
        r = {}

        # ... and the object specifying what to filter is a list or set,
        # we just include the keys in that list or set, if they exist

        if isinstance(b, (list, set)):
            for item in b:
                if item in a:
                    r[item] = a[item]


        # ... or, if the object specifying what to filter is also a
        # dictionary (since we know it's a list, set or dictionary and
        # we've already handled lists and sets), what we do depends
        # whether the items in it are empty or not...
        #
        # if the item to filter on is empty, we include the entire
        # corresponding item
        #
        # if the item to filter on is not empty, we recursively process
        # the two dictionaries to include the corresponding items

        else:
            for item in b:
                if item in a:
                    if not b[item]:
                        r[item] = a[item]
                    else:
                        # get the recursive result but only include it
                        # if it's not empty

                        sub_r = _deepfilter(a[item], b[item], path.sub(item))
                        if sub_r:
                            r[item] = sub_r


    # if the object we're filtering from is not one of the above -
    # probably a simple type - we're raise an exception as that's not
    # supported

    else:
        raise TypeError(
                  "deepfilter at: %s cannot filter compound type: %s "
                  "from non-compound type: %s"
                      % (path, type(b), type(a)))


    # return the resulting filtered version of 'a'

    return r



def deepfilter(a, b):
    """This function is almost an opposite to deepremoveitems(): it
    takes a nested object 'a' and returns only the items within it that
    are specified in object 'b'.  Both 'a' and 'b' must be compound
    types (a list, set or dictionary) at the top level and can contain
    further compound types or simple types, nested within.

    Neither object 'a' nor 'b' are modified, but the returned value may
    reference the same sub-objects within 'a' so will need to be
    copy.deepcopy()ed, if it is to be modified without affecting 'a'.

    What happens depends on the types of corresponding items in 'a' and
    'b':

    Where 'a' is a list or set, the items are retained, if they are
    present in 'b'.  'b' can be a list, set or dictionary but, if the
    corresponding item in 'b' is a dictionary, it must be empty.

    Where 'a' is a dictionary, 'b' can either be a list or set (in
    which case, the items in 'b' are returned from 'a'), or a
    dictionary.  In the latter case, if the corresponding item in 'b'
    is empty, the item in 'a' is returned entirely; if not, the items in
    each dictionary are processed recursively.

    The reason for handling empty dictionaries as a special case is to
    allow a mix of returning entire items (which could be done with a
    list or set for 'b') and returning specific items within other items
    (which requires a dictionary).  Note that an empty list or set
    cannot be used instead of an empty dictionary: they will return
    no items from the corresponding item.

    If there are mismatches, violating the above rules, a TypeError()
    or ValueError() exception is raised.

    Keyword arguments:

    a -- the object to have items returned from it: this can be a
    dictionary, list or set; it will not be modified but the returned
    value may reference objects within it

    b -- the object specifying what items are to be returned from 'a';
    it doesn't need to match the type of 'a' but there are certain
    constraints, described above, which it must fit within, at each
    level
    """

    return _deepfilter(a, b)
