class Reference:
    """
    A class used for storing references to other classes
    """

    def __init__(self, system, value, name):
        self.system = system
        self.value = str(value)
        self.name = name

    def __hash__(self):
        return hash([self.system, self.value])

    def __eq__(self, other):
        """
        Reference equality is based on the system/value.  The name is just
        decorative.
        """
        return (
            isinstance(other, self.__class__)
            and self.system == other.system
            and self.value == other.value
        )

    def __ne__(self, other):
        """
        Reference inequality is based on the system/value.  The name is just
        decorative.
        """
        return not self.__eq__(other)
