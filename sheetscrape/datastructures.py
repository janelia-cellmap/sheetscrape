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
