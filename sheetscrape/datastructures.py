from dataclasses import dataclass


@dataclass
class FIBSEMDataset:
    """
    A (potentially cropped) FIBSEM Dataset
    """

    biotype: str
    alias: str
    dimensions: dict
    offset: dict
    resolution: dict
    labels: list
    parent: str

    def todict(self):
        """

        :return: A dict of property: value pairs
        """

        outDict = self.__dict__
        return outDict
