import numpy as np
from pathlib import Path
import pandas as pd
from ..datastructures import FIBSEMDataset

columns = dict()
columns["parent_alias"] = "Cell/Tissue Short Name"
columns["crop_alias"] = "Crop Short Name"
columns["voxel_size"] = "Voxel Size (nm)"
columns["roi_size"] = "ROI Size (pixel)"
columns["roi_origins"] = "ROI Coordinates"
columns["biotype"] = "Cell/Tissue Type"
columns["parent_file"] = "File Paths"
columns["label_bounds"] = ("ECS", "Microtubules in")


def clean_filename(string):
    return string.strip()


def get_parent_aliases(head, body):
    aliases = get_named_column(columns["parent_alias"], head, body)
    return aliases


def get_crop_aliases(head, body):
    aliases = get_named_column(columns["crop_alias"], head, body)
    return aliases


def get_named_xyz_triple(name, head, body):
    mask = head == name

    if not np.any(mask):
        return None

    init_col = np.where(mask)[1][0]
    indexer = slice(init_col, init_col + 3)
    keys = head.iloc[-1, indexer]

    if body.ndim == 1:
        body = pd.DataFrame(body).T

    vals = body.iloc[:, indexer].copy()

    vals[vals == ""] = -1
    try:
        vals_npy = vals.astype("int").to_numpy()
    except ValueError:
        print(f"Problem converting {vals} to numpy array")
        return None
    results = tuple(dict(zip(keys, val)) for val in vals_npy)
    return results


def get_named_column(name, head, body):
    mask = head == name

    if not np.any(mask):
        return None

    idx = np.where(mask)
    if body.ndim == 1:
        body = pd.DataFrame(body).T

    return body.iloc[:, idx[1][0]].to_list()[0]


def get_labels(head, body):

    if body.ndim == 1:
        body = pd.DataFrame(body).T

    first_label, last_label = columns["label_bounds"]
    first_row, first_col = np.where(head == first_label)
    first_row = first_row[0]
    first_col = first_col[0]
    last_col = np.where(head == last_label)[1][0] + 1
    indexer = slice(first_col, last_col)
    indices = parse_labels(head.iloc[first_row, indexer], body.iloc[:, indexer])
    return indices


def parse_labels(head, body):
    indices = []
    for r in range(body.shape[0]):
        mask = body.iloc[r] == "X"
        inds_ = np.where(mask)[0]
        indices.append((inds_, tuple(head[mask])))
    return indices


def get_resolutions(head, body):
    return get_named_xyz_triple(columns["voxel_size"], head, body)


def get_roi_sizes(head, body):
    return get_named_xyz_triple(columns["roi_size"], head, body)


def get_roi_origins(head, body):
    return get_named_xyz_triple(columns["roi_origins"], head, body)


def get_biotype(head, body):
    return get_named_column(columns["biotype"], head, body)


def get_parent_file(head, body):
    return clean_filename(get_named_column(columns["parent_file"], head, body))


def get_crop_file(crop_short_name):
    pass


def decap(df, neck):
    """
    Separate the head from the body of a dataframe
    """
    head = df.iloc[:neck]
    body = df.iloc[neck:]
    return head, body


def get_datasets(head, body):
    """
    Given a head and body dataframes, decompose each row of the body dataframe into a FIBSEMDataset object.
    """
    results = []
    for idx, row in body.iterrows():
        parent_file = get_parent_file(head, row)
        crop_alias = get_crop_aliases(head, row)
        biotype = get_biotype(head, row)
        resolution = get_resolutions(head, row)
        roi_size = get_roi_sizes(head, row)
        roi_origin = get_roi_origins(head, row)
        labels = get_labels(head, row)

        ds = FIBSEMDataset(
            biotype=biotype,
            alias=crop_alias,
            dimensions=roi_size,
            offset=roi_origin,
            resolution=resolution,
            labels=labels,
            parent=parent_file,
        )
        results.append(ds)
    return results


def parse(df):
    head, body = decap(df, neck=3)
    return get_datasets(head, body)
