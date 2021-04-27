# deepops.path



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
