import numpy as np
from pathlib import Path
import pandas as pd
from ..datastructures import FIBSEMDataset
from datetime import datetime
from functools import partial

columns = dict()
columns["parent_alias"] = "Cell/Tissue Short Name"
columns['crop_number'] = "Crop Number"
columns["crop_alias"] = "Crop Short Name"
columns["voxel_size"] = "Voxel Size (nm)"
columns["roi_size"] = "ROI Size (pixel)"
columns["roi_origins"] = "ROI Coordinates"
columns["biotype"] = "Cell/Tissue Type"
columns["parent_file"] = "File Paths"
columns["label_bounds"] = ("ECS", "Nucleus combined")
columns["completion"] = "Completion Stage"

type_converters = dict()
type_converters[None] = lambda v: v
type_converters['int'] = int
type_converters['float'] = float

def get_named_xyz_triple(name, head, body, val_type=None):
    mask = head == name
    type_converter = type_converters[val_type]
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

    results = tuple(dict(zip(keys, list(map(type_converter, val))))for val in vals_npy)
    return results


def get_named_column(name, head, body):
    mask = head == name

    if not np.any(mask):
        return None

    idx = np.where(mask)
    if body.ndim == 1:
        body = pd.DataFrame(body).T

    return body.iloc[:, idx[1][0]].to_list()


def clean_filename(string):
    return string.strip()


def get_parent_aliases(head, body):
    aliases = get_named_column(columns["parent_alias"], head, body)
    return aliases


def get_crop_aliases(head, body):
    aliases = get_named_column(columns["crop_alias"], head, body)
    return aliases

def get_crop_number(head, body):
    return get_named_column(columns['crop_number'], head, body)

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
    flags = 'X', '/', '-', '!'
    label_keys = 'present_annotated', 'present_unannotated', 'absent_annotated', 'present_partial_annotation'
    label_dict = dict()

    for r in range(body.shape[0]):
        for flag, label_key in zip(flags, label_keys):
            mask = body.iloc[r] == flag
            inds_ = (np.where(mask)[0] + 1).tolist()
            label_dict[label_key] = list(zip(inds_, tuple(head[mask])))
    return label_dict


def get_resolutions(head, body):
    return get_named_xyz_triple(columns["voxel_size"], head, body, val_type='float')


def get_roi_sizes(head, body):
    return get_named_xyz_triple(columns["roi_size"], head, body, val_type='int')


def get_roi_origins(head, body):
    return get_named_xyz_triple(columns["roi_origins"], head, body, val_type='int')


def get_biotype(head, body):
    return get_named_column(columns["biotype"], head, body)


def get_parent_file(head, body):
    return get_named_column(columns["parent_file"], head, body)


def get_completion_stage(head, body):
    result = get_named_column(columns["completion"], head, body)

    for ind in range(len(result)):
        r = result[ind]
        if len(r)>0:
            result[ind] = int(r)
        else:
            result[ind] = 0
    return result

def get_crop_file(crop_short_name):
    pass

def get_end(head, body, column_name):
    """
    Return the first index where the column is empty
    """
    end = get_named_column(column_name, head, body).index('')
    return end

            
def decap(df, neck, end_func=None):
    """
    Separate the head from the body of a dataframe
    """
    if end_func is None:
        end_func = lambda h, b: len(b) - 1

    head = df.iloc[:neck]
    body = df.iloc[neck:]
    end = end_func(head, body)
    body = body[:end]

    return head, body


def get_datasets(head, body):
    """
    Given a head and body dataframes, decompose each row of the body dataframe into a FIBSEMDataset object.
    """
    results = []
    for idx, row in body.iterrows():
        parent_file = get_parent_file(head, row)[0]
        crop_alias = get_crop_aliases(head, row)[0]
        crop_number = get_crop_number(head, row)[0]
        biotype = get_biotype(head, row)[0]
        resolution = get_resolutions(head, row)[0]
        roi_size = get_roi_sizes(head, row)[0]
        roi_origin = get_roi_origins(head, row)[0]
        labels = get_labels(head, row)
        completion = get_completion_stage(head, row)[0]
        ds = FIBSEMDataset(
            biotype=biotype,
            number=crop_number,
            alias=crop_alias,
            dimensions=roi_size,
            offset=roi_origin,
            resolution=resolution,
            labels=labels,
            parent=parent_file,
            completion=completion,
            access_date=datetime.now()
        )
        results.append(ds)
    return results


def parse(df):
    ef = partial(get_end, column_name = columns['parent_file'])
    head, body = decap(df, neck=3, end_func=ef)
    return get_datasets(head, body)
