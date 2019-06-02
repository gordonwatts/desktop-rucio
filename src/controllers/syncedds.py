# Controller for datasets that are synced locally.

import hug
from src.controllers.globals import datasets
from src.grid.datasets import DatasetQueryStatus

@hug.get_post('/ds')
def get_ds(ds_name:str, request):
    r'''
    Returns the info for a downloaded dataset.

    If you call this with the GET HTTP method, then it will not start an upload.
    If you call this with a POST HTTP method, it will trigger a download.

    Args:
        ds_name:       Name of the dataset

    Returns:
        status:     'not_on_server' - the dataset is not local to the server (GET)
                    'does_not_exist' - the dataset is not local or on the GRID (POST)
                    'downloading' - Downloading is in progress for this dataset (GET, POST)
                    'local' - Files are local (GET, POST)
        filelist:   List of files relative to the root mount for the downloaded files.
                    Is an empty list unless the status is `'local`.
    '''

    status,files = datasets.download_ds(ds_name, do_download=request.method == 'POST')
    if status == DatasetQueryStatus.does_not_exist:
        return {'status': 'not_on_server' if request.method == 'GET' else 'does_not_exist', 'filelist':[]}
    elif status == DatasetQueryStatus.query_queued:
        return {'status': 'downloading', 'filelist':[]}
    elif status == DatasetQueryStatus.results_valid:
        return {'status': 'local', 'filelist':files}
    else:
        raise BaseException("Do not know what the status means!")
