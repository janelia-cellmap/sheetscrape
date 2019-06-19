import numpy as np
import pandas as pd
from pathlib import Path
from ..datastructures import FIBSEMDataset

def is_n5(string):
    return Path(string).suffix == '.n5'

def get_parent_aliases(head, body):
    shortname_column_name = 'Cell/Tissue Short Name'
    aliases = list(get_named_column(shortname_column_name, head, body))
    return aliases

def get_crop_aliases(head, body):    
    crop_alias_column_name = 'Crop Short Name'
    aliases =list(get_named_column(crop_alias_column_name, head, body))
    return aliases

def get_named_xyz_triple(name, head, body):
    mask = head == name
    
    if not np.any(mask):
        return None
    
    init_col = np.where(mask)[1][0]        
    indexer = slice(init_col, init_col + 3)
    keys = head.iloc[-1, indexer]
    vals = body.iloc[:, indexer]
    
    try:
        vals_npy = vals.astype('int').to_numpy()       
    except ValueError:
            print(f'Problem converting {vals} to numpy array')
            return None
    results = tuple(dict(zip(keys,val)) for val in vals_npy)
    return results

def get_named_column(name, head, body):
    mask = head == name
    
    if not np.any(mask):
        return None
    
    idx = np.where(mask)
    return list(body.iloc[:,idx[1][0]])

def get_labels(head, body):
    first_label = 'ECS'
    last_label = 'Microtubules in'    
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
        mask = body.iloc[r] == 'X'
        inds_ = np.where(mask)[0]
        indices.append((inds_, tuple(head[mask])))
    return indices

def get_resolutions(head, body):
    vox_size_column_name = 'Voxel Size (nm)'
    return get_named_xyz_triple(vox_size_column_name, head, body)

def get_roi_sizes(head, body):
    roi_size_column_name = 'ROI Size (pixel)'
    return get_named_xyz_triple(roi_size_column_name, head, body)

def get_roi_origins(head, body):
    roi_size_column_name = 'ROI Coordinates'
    return get_named_xyz_triple(roi_size_column_name, head, body)

def get_biotype(head, body):
    biotype_column_name = 'Cell/Tissue Type'
    return get_named_column(biotype_column_name, head, body)

def get_parent_files(head, body):
    parent_file_column_name = 'Parent File'
    parent_files = list(filter(is_n5, set(get_named_column(parent_file_column_name, head, body))))
    return parent_files

def get_crop_file(crop_short_name):
    pass

def decapitate(df, neck):
    """
    Separate the head from the body of a dataframe
    """
    head = df.iloc[:neck]
    body = df.iloc[neck:]
    return head, body

def get_datasets(head, body):
    """
    Given head and body Dataframes, return a dictionary of lists of `FIBSEMDataset` objects, with one entry in the dict per 
    parent data file, and one `FIBSEMDataset` object per crop. This function recurses when the body contains entries from 
    multiple parent datasets; it will call itself on partitioned subsets of the body dataframe. 
    """   
    parent_files = get_parent_files(head, body)
    parent_file_column = np.where(head == 'Parent File')[1][0]    
    result = dict()    

    if len(parent_files) == 1:
        # We have entries from a single parent file
        subresult = []
        path = parent_files[0]
        
        parent_alias = get_parent_aliases(head, body)[0]
        crop_aliases = get_crop_aliases(head, body)
        biotypes = get_biotype(head, body)
        resolutions = get_resolutions(head, body)
        roi_sizes = get_roi_sizes(head, body)
        roi_origins = get_roi_origins(head, body)
        labels = get_labels(head,  body)
        
        for ind in range(body.shape[0]):                
            ds = FIBSEMDataset(biotype = biotypes[ind],
                               alias =  crop_aliases[ind],
                               dimensions = roi_sizes[ind],
                               offset = roi_origins[ind],
                               resolution = resolutions[ind],
                               labels = labels[ind],
                               parent = path)
            subresult.append(ds)
        return subresult
    else:
        # We have entries from multiple parent files
        for rootdir in parent_files:
            sub_body = body[body.iloc[:,parent_file_column] == rootdir]            
            result[rootdir] = get_datasets(head, sub_body)
    
    return result

def parse(df):
    head, body = decapitate(df, neck=3)
    return get_datasets(head, body)
