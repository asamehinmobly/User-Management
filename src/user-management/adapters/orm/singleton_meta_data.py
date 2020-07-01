from sqlalchemy import MetaData


class MetaDataSingleton:
    __instance__ = None

    def __init__(self):
        """ Constructor.
        """
        if MetaDataSingleton.__instance__ is None:
            MetaDataSingleton.__instance__ = MetaData()
        else:
            raise Exception("You cannot create another BusSingleton class")

    @staticmethod
    def get_instance():
        """ Static method to fetch the current instance.
        """
        if not MetaDataSingleton.__instance__:
            MetaDataSingleton()
        return MetaDataSingleton.__instance__
