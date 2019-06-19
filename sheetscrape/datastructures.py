from dataclasses import dataclass

@dataclass
class FIBSEMDataset():
    """
    A (cropped) FIBSEMDataset 
    """
    biotype : str
    alias : str
    dimensions : dict
    offset : dict
    resolution : dict
    labels: list
    parent : str
