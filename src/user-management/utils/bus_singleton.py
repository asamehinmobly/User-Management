import bootstrap


class BusSingleton:
    __instance__ = None

    def __init__(self):
        """ Constructor.
        """
        if BusSingleton.__instance__ is None:
            BusSingleton.__instance__ = bootstrap.bootstrap()
        else:
            raise Exception("You cannot create another BusSingleton class")

    @staticmethod
    def get_instance():
        """ Static method to fetch the current instance.
        """
        if not BusSingleton.__instance__:
            BusSingleton()
        return BusSingleton.__instance__
