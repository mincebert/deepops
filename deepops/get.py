# deepops.get



from .path import DeepPath



def deepget(d, *path, default=None, default_error=False):
    """This function retrieves a value from a nested data structure of
    dictionaries, given a path through them, expressed as a list of
    keys, given as arguments.

    If default_error is False (the default) and the specified path
    cannot be found, or any of the elements in the path are not
    dictionaries, the 'default' value is returned.

    If default_error is True, one of two exceptions may be raised:
    KeyError, if any element of the path is not found, or TypeError,
    if any element in the path is not a dictionary.
    """


    # path traversed so far (for error message)

    path_so_far = DeepPath()


    # start at the top of the dictionary and work through it

    d_this = d

    for key in path:
        # if we're not raising exceptions, and we can't index this
        # level of the path, return the default value

        if (not default_error) and (not isinstance(d_this, dict)):
            return default


        # if the key can't be found, we either raise an exception, or
        # return the default value, depending on default_error

        if key not in d_this:
            if default_error:
                raise KeyError("deepget at: %s key not found: %s"
                                   % (path_so_far, key))

            return default


        # move down to the next level in the path

        d_this = d_this[key]
        path_so_far.append(key)


    # return the object at the end of the path

    return d_this
