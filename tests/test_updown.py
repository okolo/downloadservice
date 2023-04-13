from typing import Any
import pytest
from flask import Flask, url_for



@pytest.fixture(scope="session")
def app():
    import downloadservice

    downloadservice.app.config.update({
        "TESTING": True,
        "CTADS_DISABLE_ALL_AUTH": True,
        "DEBUG": True,
        "CTADS_CABUNDLE": "cabundle.pem",
    })

    print("config now:", downloadservice.app.config)

    return downloadservice.app


def test_health(client: Any):
    r = client.get(url_for('health'))
    assert r.status_code == 200
    print(r.json)


def test_list(client: Any):
    r = client.get(url_for('list', basepath="pnfs/cta.cscs.ch/lst"))
    assert r.status_code == 200
    print(r.json)


def test_fetch(client: Any):
    r = client.get(url_for('fetch', subpath="pnfs/cta.cscs.ch/lst/md5sum-lst.txt"))
    assert r.status_code == 200
    print(r.json)


def test_apiclient_list(start_service):
    import ctadata

    r = ctadata.list_dir("", downloadservice=start_service['url'])

    print(r)

    ctadata.APIClient.downloadservice = start_service['url']

    with pytest.raises(ctadata.api.StorageException):
        ctadata.list_dir("blablabalfake")
        
    r = ctadata.list_dir("lst")

    n_dir = 0
    n_file = 0
    
    for entry in r:
        print(entry)
        if entry['type'] == 'directory':
            n_dir += 1
            print(ctadata.list_dir(entry['href']))
        else:
            n_file +=1

        if n_dir > 2 and n_file > 3:
            break


def test_apiclient_fetch(start_service, caplog):
    import ctadata

    ctadata.APIClient.downloadservice = start_service['url']
        
    r = ctadata.list_dir("lst")

    for entry in r:
        print(entry)
        if entry['type'] == 'file' and int(entry['size']) > 10000:
            ctadata.fetch_and_save_file(entry['href'], chunk_size=1024*1024*10)
            assert 'in 4 chunks' in caplog.text
            assert 'in 9 chunks' not in caplog.text
            ctadata.fetch_and_save_file(entry['href'], chunk_size=1024*1024*5)
            assert 'in 9 chunks' in caplog.text
            break
