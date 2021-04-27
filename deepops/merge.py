# deepops.merge



from .path import DeepPath



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
