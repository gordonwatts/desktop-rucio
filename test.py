# Test harness for debugging easily.

from tests.grid.test_datasets import test_dataset_download_restart_and_marked
from src.grid.rucio import RucioFile, RucioException
from src.utils.dataset_cache_mgr import dataset_cache_mgr
from src.utils.dataset_cache_mgr import dataset_listing_info
from tests.grid.utils_for_tests import run_dummy_multiple
import os
import tempfile
import shutil
from time import sleep

def rucio_2file_dataset(simple_dataset):
    class rucio_dummy:
        def __init__(self, ds):
            self._ds = ds
            self.CountCalled = 0
            self.CountCalledDL = 0
            self._cache_mgr = None

        def get_file_listing(self, ds_name, log_func = None):
            self.CountCalled += 1
            if ds_name == self._ds.Name:
                return self._ds.FileList
            return None

        def download_files(self, ds_name, data_dir):
            if self._cache_mgr is not None:
                self._cache_mgr.add_ds(self._ds)
            self.CountCalledDL += 1

    return rucio_dummy(simple_dataset)

def rucio_do_nothing():
    class rucio_dummy:
        def __init__(self):
            self.CountCalled = 0
            self.CountCalledDL = 0
            
        def get_file_listing(self, ds_name, log_func = None):
            self.CountCalled += 1
            return None

        def download_files(self, ds_name, data_dir, log_func = None):
            self.CountCalledDL += 1
            sleep(15)

    return rucio_dummy()

def rucio_2file_dataset_with_fails(simple_dataset):
    class rucio_dummy:
        def __init__(self, ds):
            self._ds = ds
            self.CountCalled = 0
            self.CountCalledDL = 0
            self._cache_mgr = None
            self.DLSleep = None

        def get_file_listing(self, ds_name, log_func = None):
            self.CountCalled += 1
            if self.CountCalled < 5:
                raise RucioException("Please Try again Due To Internet Being Out")
            if ds_name == self._ds.Name:
                return self._ds.FileList
            return None

        def download_files(self, ds_name, data_dir, log_func = None):
            self.CountCalledDL += 1
            if self.DLSleep is not None:
                sleep(self.DLSleep)
            if self.CountCalledDL < 5:
                raise RucioException("Please try again due to internet being out")
            if self._cache_mgr is not None:
                self._cache_mgr.add_ds(self._ds)

    return rucio_dummy(simple_dataset)

def rucio_2file_dataset_take_time(simple_dataset):
    class rucio_dummy:
        def __init__(self, ds):
            self._ds = ds
            self.CountCalled = 0

        def get_file_listing(self, ds_name):
            sleep(0.005)
            self.CountCalled += 1
            if ds_name == self._ds.Name:
                return self._ds.FileList
            return None

    return rucio_dummy(simple_dataset)

def rucio_2file_dataset_shows_up_later(simple_dataset):
    class rucio_dummy:
        def __init__(self, ds):
            self._ds = ds
            self.CountCalled = 0

        def get_file_listing(self, ds_name, log_func = None):
            self.CountCalled += 1
            if self.CountCalled < 2:
                return None
            if ds_name == self._ds.Name:
                return self._ds.FileList
            return None

    return rucio_dummy(simple_dataset)

def cache_empty():
    'Create an empty cache that will save anything saved in it.'
    class cache_good_dummy():
        def __init__(self):
            self._ds_list = {}
            self._in_progress = []
            self._in_download = []
            self._downloaded_ds = {}
        
        def get_download_directory(self):
            return 'totally-bogus'

        def add_ds(self, ds_info):
            self._downloaded_ds[ds_info.Name] = ds_info

        def get_listing(self, ds_name):
            if ds_name in self._ds_list:
                return self._ds_list[ds_name]
            return None

        def save_listing(self, ds_info):
            self._ds_list[ds_info.Name] = ds_info
            self._in_progress.remove(ds_info.Name)

        def mark_query(self, ds_name):
            self._in_progress.append(ds_name)
        def query_in_progress(self, ds_name):
            return ds_name in self._in_progress
        def get_queries(self):
            return self._in_progress

        def get_ds_contents(self, ds_name):
            if ds_name in self._downloaded_ds:
                return [f.filename for f in self._downloaded_ds[ds_name].FileList]
            return None

        def mark_downloading(self, ds_name):
            self._in_download.append(ds_name)

        def download_in_progress(self, ds_name):
            return ds_name in self._in_download

        def get_downloading(self):
            return self._in_download

        def mark_download_done(self, ds_name):
            self._in_download.remove(ds_name)

    return cache_good_dummy()


def simple_dataset():
    'Create a simple dataset with 2 files in it and no expiration'
    f1 = RucioFile('f1.root', 100, 1)
    f2 = RucioFile('f2.root', 200, 2)
    return dataset_listing_info('dataset1', [f1, f2])

def local_cache():
    'Setup cache temp directory, and then remove it when done'
    loc = "{0}/desktop-rucio-cache-testing".format(tempfile.gettempdir())
    if os.path.exists(loc):
        shutil.rmtree(loc)
    os.mkdir(loc)
    return dataset_cache_mgr(location=loc)


def rucio_good_ds_download():
    responses = {"cd /data; rucio download mc16_13TeV.311309.MadGraphPythia8EvtGen_A14NNPDF31LO_HSS_LLP_mH125_mS5_ltlow.deriv.DAOD_EXOT15.e7270_e5984_s3234_r10201_r10210_p3795":
        {'shell_output': ['''bash-4.2# cd /data; rucio download mc16_13TeV.311309.MadGraphPythia8EvtGen_A14NNPDF31LO_HSS_LLP_mH125_mS5_ltlow.deriv.DAOD_EXOT15.e7270_e5984_s3234_r10201_r10210_p3795
2019-04-27 23:14:27,425 INFO    Processing 1 item(s) for input
2019-04-27 23:14:27,426 INFO    Getting sources of DIDs
2019-04-27 23:14:28,742 INFO    Using 3 threads to download 5 files
2019-04-27 23:14:28,744 INFO    Thread 1/3: Preparing download of mc16_13TeV:DAOD_EXOT15.17545497._000001.pool.root.1
2019-04-27 23:14:28,748 INFO    Thread 2/3: Preparing download of mc16_13TeV:DAOD_EXOT15.17545497._000002.pool.root.1
2019-04-27 23:14:28,751 INFO    Thread 3/3: Preparing download of mc16_13TeV:DAOD_EXOT15.17545497._000003.pool.root.1
2019-04-27 23:14:29,432 INFO    Thread 2/3: Trying to download with root from TAIWAN-LCG2_DATADISK: mc16_13TeV:DAOD_EXOT15.17545497._000002.pool.root.1 
2019-04-27 23:14:29,482 INFO    Thread 3/3: Trying to download with root from TAIWAN-LCG2_DATADISK: mc16_13TeV:DAOD_EXOT15.17545497._000003.pool.root.1 
2019-04-27 23:14:29,484 INFO    Thread 1/3: Trying to download with root from TAIWAN-LCG2_DATADISK: mc16_13TeV:DAOD_EXOT15.17545497._000001.pool.root.1 
2019-04-28 00:02:09,137 INFO    Thread 1/3: File mc16_13TeV:DAOD_EXOT15.17545497._000001.pool.root.1 successfully downloaded. 2.011 GB in 2828.17 seconds = 0.71 MBps
2019-04-28 00:02:09,139 INFO    Thread 1/3: Preparing download of mc16_13TeV:DAOD_EXOT15.17545497._000004.pool.root.1
2019-04-28 00:02:09,834 INFO    Thread 1/3: Trying to download with gsiftp from SWT2_CPB_DATADISK: mc16_13TeV:DAOD_EXOT15.17545497._000004.pool.root.1 
2019-04-28 00:02:11,968 WARNING Thread 1/3: Download attempt failed. Try 1/2
2019-04-28 00:02:13,614 WARNING Thread 1/3: Download attempt failed. Try 2/2
2019-04-28 00:02:14,346 INFO    Thread 1/3: Trying to download with root from TAIWAN-LCG2_DATADISK: mc16_13TeV:DAOD_EXOT15.17545497._000004.pool.root.1 
2019-04-28 00:02:19,178 INFO    Thread 3/3: File mc16_13TeV:DAOD_EXOT15.17545497._000003.pool.root.1 successfully downloaded. 2.019 GB in 2839.03 seconds = 0.71 MBps
2019-04-28 00:02:19,179 INFO    Thread 3/3: Preparing download of mc16_13TeV:DAOD_EXOT15.17545497._000005.pool.root.1
2019-04-28 00:02:19,179 INFO    Thread 3/3: Trying to download with root from TAIWAN-LCG2_DATADISK: mc16_13TeV:DAOD_EXOT15.17545497._000005.pool.root.1 
2019-04-28 00:03:07,137 INFO    Thread 2/3: File mc16_13TeV:DAOD_EXOT15.17545497._000002.pool.root.1 successfully downloaded. 2.010 GB in 2893.48 seconds = 0.69 MBps
2019-04-28 00:32:19,792 INFO    Thread 1/3: File mc16_13TeV:DAOD_EXOT15.17545497._000004.pool.root.1 successfully downloaded. 2.012 GB in 1793.79 seconds = 1.12 MBps
2019-04-28 00:34:12,348 INFO    Thread 3/3: File mc16_13TeV:DAOD_EXOT15.17545497._000005.pool.root.1 successfully downloaded. 2.018 GB in 1901.95 seconds = 1.06 MBps
----------------------------------
Download summary
----------------------------------------
DID mc16_13TeV:mc16_13TeV.311309.MadGraphPythia8EvtGen_A14NNPDF31LO_HSS_LLP_mH125_mS5_ltlow.deriv.DAOD_EXOT15.e7270_e5984_s3234_r10201_r10210_p3795
Total files :                                 5
Downloaded files :                            5
Files already found locally :                 0
Files that cannot be downloaded :             0'''], 'shell_result':0}}
    return run_dummy_multiple(responses)

def rucio_good_ds_download_takes_time():
    responses = {"cd /data; rucio download mc16_13TeV.311309.MadGraphPythia8EvtGen_A14NNPDF31LO_HSS_LLP_mH125_mS5_ltlow.deriv.DAOD_EXOT15.e7270_e5984_s3234_r10201_r10210_p3795dude":
        {'shell_output': ['''bash-4.2# cd /data; rucio download mc16_13TeV.311309.MadGraphPythia8EvtGen_A14NNPDF31LO_HSS_LLP_mH125_mS5_ltlow.deriv.DAOD_EXOT15.e7270_e5984_s3234_r10201_r10210_p3795    
2019-04-28 00:42:29,370 INFO    Processing 1 item(s) for input
2019-04-28 00:42:29,370 INFO    Getting sources of DIDs
2019-04-28 00:42:30,617 INFO    Using 3 threads to download 5 files
2019-04-28 00:42:30,619 INFO    Thread 1/3: Preparing download of mc16_13TeV:DAOD_EXOT15.17545497._000001.pool.root.1
2019-04-28 00:42:30,620 INFO    Thread 1/3: File exists already locally: mc16_13TeV:DAOD_EXOT15.17545497._000001.pool.root.1
2019-04-28 00:42:30,626 INFO    Thread 2/3: Preparing download of mc16_13TeV:DAOD_EXOT15.17545497._000002.pool.root.1
2019-04-28 00:42:30,628 INFO    Thread 2/3: File exists already locally: mc16_13TeV:DAOD_EXOT15.17545497._000002.pool.root.1
2019-04-28 00:42:30,628 INFO    Thread 3/3: Preparing download of mc16_13TeV:DAOD_EXOT15.17545497._000003.pool.root.1
2019-04-28 00:42:30,629 INFO    Thread 3/3: File exists already locally: mc16_13TeV:DAOD_EXOT15.17545497._000003.pool.root.1
2019-04-28 00:42:31,310 INFO    Thread 1/3: Preparing download of mc16_13TeV:DAOD_EXOT15.17545497._000004.pool.root.1
2019-04-28 00:42:31,311 INFO    Thread 1/3: File exists already locally: mc16_13TeV:DAOD_EXOT15.17545497._000004.pool.root.1
2019-04-28 00:42:31,317 INFO    Thread 2/3: Preparing download of mc16_13TeV:DAOD_EXOT15.17545497._000005.pool.root.1
2019-04-28 00:42:31,317 INFO    Thread 2/3: File exists already locally: mc16_13TeV:DAOD_EXOT15.17545497._000005.pool.root.1
----------------------------------
Download summary
----------------------------------------
DID mc16_13TeV:mc16_13TeV.311309.MadGraphPythia8EvtGen_A14NNPDF31LO_HSS_LLP_mH125_mS5_ltlow.deriv.DAOD_EXOT15.e7270_e5984_s3234_r10201_r10210_p3795
Total files :                                 5
Downloaded files :                            0
Files already found locally :                 5
Files that cannot be downloaded :             0'''], 'shell_result':75, 'delay': 0.01}}
    return run_dummy_multiple(responses)


test_dataset_download_restart_and_marked(rucio_do_nothing(), rucio_2file_dataset_with_fails(simple_dataset()), cache_empty(), simple_dataset())
