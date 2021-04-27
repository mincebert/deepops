# deepops.setdefault



def deepsetdefault(d, *path, last={}):
    """This function performs a path of dict.setdefault() calls to
    initialise multiple levels of a dictionary 'd' with a number of path
    elements ('path', as a variable argument list).

    For example, 'deepsetdefault({}, 1, 2)' will give a dictionary of
    {1: { 2: {} }}.

    The optional 'last' argument allows the final object to be changed
    from a dict().

    As with setdefault(), the final object added will be returned.
    """


    # get the length of the path so we can count down until the last
    # item

    path_remain = len(path)


    # start at the top of the dictionary

    d_sub = d

    for key in path:
        # setdefault() the next level in the path, using the last
        # parameter, if this is the final level - if so, we also need to
        # copy() it first, otherwise the same instance will be used for
        # all defaults (if it was the default argument)

        d_sub = d_sub.setdefault(
            key, {} if path_remain > 1 else last.copy())


        path_remain -= 1


    # return where we got to at the end of the path

    return d_sub
