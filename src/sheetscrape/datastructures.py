from dataclasses import dataclass
import datetime

@dataclass
class FIBSEMDataset:
    """
    A (potentially cropped) FIBSEM Dataset. Has the following properties:

    biotype: A string label that indicates the biological type of the data,
    e.g., "Hela Cell" or "Mouse neurons".

    number: A numeric index that identifies the crop.

    alias: A content-ful name for the subregion of the dataset,
    e.g., "Ribosome"

    dimensions: A `dict` with keys specifying axes and values specifying the dimension, in pixels, of the dataset along
    each axis, e.g., {'z':10, 'y':10, 'x':10} for a 10x10x10 pixel dataset

    offset: A `dict` with keys specifying axes and values specifying the relative offset of the origin, in pixels, of
    the dataset along each axis, e.g., {'z':0, 'y':0, 'x':0} for a dataset that starts in the corner of a parent dataset.

    resolution: A `dict` with keys specifying axes and values specifying the resolution of the dataset along each axis,
    e.g., {'z':8, 'y':4, 'x':4}

    labels: A list of two lists describing the labeled fields identified in the dataset. The first list contains the
    integer codes for the labels, and the second list contains the string names for the coded labels.
    e.g., [[0, 1, 2],['ECS', 'Plasma membrane', 'Mito membrane']]

    parent: A string representation of a raw file path that points to the parent dataset for this dataset.
    e.g., '/groups/hess/hess_collaborators/Annotations/ParentFiles_whole-cell_images/HeLa_Cell3_4x4x4nm/Aubrey_17-7_17_Cell3_4x4x4nm.n5'
    """

    biotype: str
    number: str
    alias: str
    dimensions: dict
    offset: dict
    resolution: dict
    labels: list
    parent: str
    completion: int
    access_date: datetime.datetime

    def todict(self):
        """

        :return: A dict of property: value pairs
        """

        out_dict = self.__dict__
        return out_dict
