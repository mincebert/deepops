# deepops.setdefault



# default value for the 'last' parameter to the deepsetdefault()
# function, below - we have to declare this separately so we can check
# if it has been overridden explicitly (see inside function for reason)

_empty_dict = {}



def deepsetdefault(d, *path, last=_empty_dict):
    """This function performs a dict.setdefault() along a path to
    initialise multiple levels of a dictionary 'd' with a number of path
    elements ('path', as a variable argument list).

    For example, 'deepsetdefault({}, 1, 2)' will give a dictionary of
    { 1: { 2: {} } }.

    The optional 'last' argument allows the final object to be changed
    from an empty dict().

    As with setdefault(), the final object added will be returned, which
    will be 'last', if the last element in the path is not already set.
    """


    # start at the top of the dictionary

    d_sub = d


    # step through the elements in the path, getting the head and tail

    while path:
        key, path = path[0], path[1:]


        # check we're not at the end of the path, or 'last' was left as
        # the default (which is an empty dictionary), we set this level
        # to be the empty dictionary

        if path or (last is _empty_dict):
            # we handle the default value of 'last' specially because,
            # if we just set it as is (from the value in the funtion
            # definition) and it is modified, this will affect future
            # calls to the function, which will use the (now) non-empty
            # dictionary

            d_sub = d_sub.setdefault(key, {})

        else:
            # we're at the end of the path and 'last' was specified
            # (overriding the default) so we use that value

            d_sub = d_sub.setdefault(key, last)


    # return where we got to at the end of the path

    return d_sub
