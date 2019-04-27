# Test out using rucio to run things
#
import pytest
from tests.grid.utils_for_tests import run_dummy_multiple
from src.grid.rucio import rucio, RucioException

# Runners that respond to commands from rucio with various outputs.
@pytest.fixture()
def rucio_good_file_listing():
    responses = {"rucio list-files mc16_13TeV:mc16_13TeV.311313.MadGraphPythia8EvtGen_A14NNPDF31LO_HSS_LLP_mH125_mS35_lthigh.deriv.DAOD_EXOT15.e7270_e5984_s3234_r10724_r10726_p3795":
    {'shell_output': ['''bash-4.2# rucio list-files mc16_13TeV:mc16_13TeV.311313.MadGraphPythia8EvtGen_A14NNPDF31LO_HSS_LLP_mH125_mS35_lthigh.deriv.DAOD_EXOT15.e7270_e5984_s3234_r10724_r10726_p3795
+-----------------------------------------------------+--------------------------------------+-------------+------------+----------+
| SCOPE:NAME                                          | GUID                                 | ADLER32     | FILESIZE   |   EVENTS |
|-----------------------------------------------------+--------------------------------------+-------------+------------+----------|
| mc16_13TeV:DAOD_EXOT15.17545540._000001.pool.root.1 | 46459733-8A1D-EA42-B037-D464BE3809AD | ad:f5da9a8c | 1.981 GB   |    10000 |
| mc16_13TeV:DAOD_EXOT15.17545540._000002.pool.root.1 | B60DCC5E-C81E-7144-A9C2-E21DF2EA5B18 | ad:1c2b11cc | 1.995 GB   |    10000 |
| mc16_13TeV:DAOD_EXOT15.17545540._000003.pool.root.1 | D5BE7787-5552-1240-8963-CA429722A559 | ad:295a4a5b | 1.982 GB   |    10000 |
| mc16_13TeV:DAOD_EXOT15.17545540._000004.pool.root.1 | 7A9152AA-C398-6242-ACC1-5BE0F64E0C4E | ad:63b5a671 | 1.987 GB   |    10000 |
| mc16_13TeV:DAOD_EXOT15.17545540._000005.pool.root.1 | 7603A2A9-9A29-2F49-812C-CE3BE602B88F | ad:cea4316c | 1.989 GB   |    10000 |
| mc16_13TeV:DAOD_EXOT15.17545540._000006.pool.root.1 | 186270AC-C72B-7D4A-A5AF-8CB6F9AD97FC | ad:24bf1844 | 1.979 GB   |    10000 |
| mc16_13TeV:DAOD_EXOT15.17545540._000007.pool.root.1 | A439D4DE-DD57-E140-81C5-3B3C9F20A4FB | ad:16d9688f | 1.988 GB   |    10000 |
| mc16_13TeV:DAOD_EXOT15.17545540._000008.pool.root.1 | 7565AC5F-1F15-4A40-9055-B3B6880AA58F | ad:de4d84ba | 1.988 GB   |    10000 |
| mc16_13TeV:DAOD_EXOT15.17545540._000009.pool.root.1 | 501DCEC9-A3E0-0E4F-9569-DB7A3A0946F2 | ad:8818f0ef | 1.992 GB   |    10000 |
| mc16_13TeV:DAOD_EXOT15.17545540._000010.pool.root.1 | CC389980-14D1-CA4F-B297-AAF079BFD282 | ad:ab32c6ac | 1.973 GB   |    10000 |
| mc16_13TeV:DAOD_EXOT15.17545540._000011.pool.root.1 | 2B34B292-072A-2440-9022-BFD188B914BA | ad:9e2a7cf7 | 7.939 GB   |    40000 |
| mc16_13TeV:DAOD_EXOT15.17545540._000012.pool.root.1 | 1BD26F0D-E8BB-1A4D-886F-1142719B7992 | ad:f76cee29 | 7.927 GB   |    40000 |
| mc16_13TeV:DAOD_EXOT15.17545540._000013.pool.root.1 | 1DCBECFA-EDC0-5840-A25A-8277CA9A31D4 | ad:c14ee390 | 5.956 GB   |    30000 |
+-----------------------------------------------------+--------------------------------------+-------------+------------+----------+
Total files : 13
Total size : 41.677 GB
Total events : 210000
'''], 'shell_result': 0}}
    yield run_dummy_multiple(responses)

@pytest.fixture()
def rucio_bad_ds_name():
    responses = {"rucio list-files mc16_13TeV:mc16_13TeV.311313.MadGraphPythia8EvtGen_A14NNPDF31LO_HSS_LLP_mH125_mS35_lthigh.deriv.DAOD_EXOT15.bogus":
    {'shell_output': ['''bash-4.2# rucio list-files mc16_13TeV:mc16_13TeV.311313.MadGraphPythia8EvtGen_A14NNPDF31LO_HSS_LLP_mH125_mS35_lthigh.deriv.DAOD_EXOT15.bogus
2019-04-24 01:26:37,308 ERROR   Data identifier not found.
Details: Data identifier 'mc16_13TeV:mc16_13TeV.311313.MadGraphPythia8EvtGen_A14NNPDF31LO_HSS_LLP_mH125_mS35_lthigh.deriv.DAOD_EXOT15.bogus' not found
'''], 'shell_result': 12}}
    yield run_dummy_multiple(responses)

@pytest.fixture()
def rucio_bad_internet():
    responses = {"rucio list-files mc16_13TeV:mc16_13TeV.311313.MadGraphPythia8EvtGen_A14NNPDF31LO_HSS_LLP_mH125_mS35_lthigh.deriv.DAOD_EXOT15.e7270_e5984_s3234_r10724_r10726_p3795":
    {'shell_output': ['''bash-4.2# rucio list-files mc16_13TeV:mc16_13TeV.311313.MadGraphPythia8EvtGen_A14NNPDF31LO_HSS_LLP_mH125_mS35_lthigh.deriv.DAOD_EXOT15.e7270_e5984_s3234_r10724_r10726_p3795
2019-04-24 01:28:24,278 ERROR   Cannot connect to the Rucio server.
'''], 'shell_result': 78}}
    yield run_dummy_multiple(responses)

@pytest.fixture()
def rucio_no_cert():
    responses = {"rucio list-files mc16_13TeV:mc16_13TeV.311313.MadGraphPythia8EvtGen_A14NNPDF31LO_HSS_LLP_mH125_mS35_lthigh.deriv.DAOD_EXOT15.e7270_e5984_s3234_r10724_r10726_p3795":
    {'shell_output': ['''bash-4.2# rucio list-files mc16_13TeV:mc16_13TeV.311313.MadGraphPythia8EvtGen_A14NNPDF31LO_HSS_LLP_mH125_mS35_lthigh.deriv.DAOD_EXOT15.e7270_e5984_s3234_r10724_r10726_p3795
given client cert (/usr/usercertfile) doesn't exist
2019-04-24 00:42:07,065 ERROR   Cannot authenticate.
Details: x509 authentication failed
2019-04-24 00:42:07,065 ERROR   Please verify that your proxy is still valid and renew it if needed.'''], 'shell_result': 1}}
    yield run_dummy_multiple(responses)

#######################
def test_rucio_ctor():
    _ = rucio()

def test_good_runner(rucio_good_file_listing):
    r = rucio_good_file_listing.shell_execute("rucio list-files mc16_13TeV:mc16_13TeV.311313.MadGraphPythia8EvtGen_A14NNPDF31LO_HSS_LLP_mH125_mS35_lthigh.deriv.DAOD_EXOT15.e7270_e5984_s3234_r10724_r10726_p3795")
    assert None is not r
    assert 0 == r.shell_result
    assert 21 == len(r.shell_output)

def test_good_file_list(rucio_good_file_listing):
    r = rucio(executor = rucio_good_file_listing)
    files = r.get_file_listing("mc16_13TeV:mc16_13TeV.311313.MadGraphPythia8EvtGen_A14NNPDF31LO_HSS_LLP_mH125_mS35_lthigh.deriv.DAOD_EXOT15.e7270_e5984_s3234_r10724_r10726_p3795")
    assert 13 == len(files)
    f_dict = {info.filename: info for info in files}
    assert 30000 == f_dict["mc16_13TeV:DAOD_EXOT15.17545540._000013.pool.root.1"].events
    assert int(5.956*1024*1024*1024) == f_dict["mc16_13TeV:DAOD_EXOT15.17545540._000013.pool.root.1"].size

def test_bad_ds_name(rucio_bad_ds_name):
    r = rucio(executor = rucio_bad_ds_name)
    assert None is r.get_file_listing("mc16_13TeV:mc16_13TeV.311313.MadGraphPythia8EvtGen_A14NNPDF31LO_HSS_LLP_mH125_mS35_lthigh.deriv.DAOD_EXOT15.bogus")

def test_no_internet(rucio_bad_internet):
    try:
        r = rucio(executor = rucio_bad_internet)
        _ = r.get_file_listing("mc16_13TeV:mc16_13TeV.311313.MadGraphPythia8EvtGen_A14NNPDF31LO_HSS_LLP_mH125_mS35_lthigh.deriv.DAOD_EXOT15.e7270_e5984_s3234_r10724_r10726_p3795")
    except RucioException as e:
        assert "Try again" in str(e)
        return
    assert False

def test_no_cert(rucio_no_cert):
    try:
        r = rucio(executor = rucio_no_cert)
        _ = r.get_file_listing("mc16_13TeV:mc16_13TeV.311313.MadGraphPythia8EvtGen_A14NNPDF31LO_HSS_LLP_mH125_mS35_lthigh.deriv.DAOD_EXOT15.e7270_e5984_s3234_r10724_r10726_p3795")
    except RucioException as e:
        assert "Try again" in str(e)
        return
    assert False

def test_logging(rucio_good_file_listing):
    r = rucio(executor = rucio_good_file_listing)
    lines = []
    files = r.get_file_listing("mc16_13TeV:mc16_13TeV.311313.MadGraphPythia8EvtGen_A14NNPDF31LO_HSS_LLP_mH125_mS35_lthigh.deriv.DAOD_EXOT15.e7270_e5984_s3234_r10724_r10726_p3795", log_func=lambda l: lines.append(l))
    assert len(lines) == 21

