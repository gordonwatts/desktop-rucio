# Controller that will give back listings of what files a dataset contains

import hug
import src.controllers.globals as globals
from src.grid.datasets import DatasetQueryStatus

@hug.get('/dsfiles')
def get_listing(ds_name:str):
    '''
    Return the files in a rucio dataset

    Returns:
                If the dataset is queued
                If the dataset exists, but is empty
                If the dataset exists, and has files
                If the dataset does not exist

    '''
    # Catalog?
    status, files = globals.datasets.get_ds_contents(ds_name)

    # How we return, depends on what we get back.
    if status == DatasetQueryStatus.query_queued:
        return {"status": "query queued"}
    elif status == DatasetQueryStatus.does_not_exist:
        return {"status": "dataset does not exist"}
    elif status == DatasetQueryStatus.results_valid:
        return {"status": "OK", 'files': [(f.filename, f.size, f.events) for f in files]}
    else:
        return {"status": "Internal error"}

