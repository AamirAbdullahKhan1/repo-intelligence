import io
import os
import stat
import zipfile
from pathlib import Path
import pytest
from app.ingestion.archive import extract_archive
from app.ingestion.github import parse_url, retrieve
from app.ingestion.snapshot import freeze, fingerprint, cleanup_error

def archive(tmp_path, names):
    path=tmp_path/'input.zip'
    with zipfile.ZipFile(path,'w') as z:
        for name in names:
            z.writestr(name,'data')
    return path

@pytest.mark.parametrize('names',[
    ['../escape.ts'],['/absolute.ts'],['C:/drive.ts'],['a/../../escape.ts'],['a\\..\\escape.ts'],
    ['A/one.ts','a/two.ts'],['a.ts','A.ts'],['dir','dir/a.ts'],['dir/a.ts','dir'],['con.txt'],['a./file.ts'],['a /file.ts'],
    ['a:stream'],['a.ts','a.ts'],['a//b.ts'],['a/./b.ts'],['\\server\\share\\file.ts'],
])
def test_reject_unsafe_paths(tmp_path,names):
    with pytest.raises(ValueError):
        extract_archive(archive(tmp_path,names),tmp_path/'out')
    assert not (tmp_path/'escape.ts').exists()

@pytest.mark.parametrize('kind',[stat.S_IFLNK,stat.S_IFIFO,stat.S_IFCHR,stat.S_IFSOCK])
def test_reject_nonregular(tmp_path,kind):
    item=zipfile.ZipInfo('link');item.create_system=3;item.external_attr=(kind|0o777)<<16
    path=tmp_path/'input.zip'
    with zipfile.ZipFile(path,'w') as z:z.writestr(item,'destination')
    with pytest.raises(ValueError):extract_archive(path,tmp_path/'out')

def test_limits_and_nested_archive(tmp_path,monkeypatch):
    import app.ingestion.archive as module
    path=archive(tmp_path,['a.ts','nested.zip'])
    root=extract_archive(path,tmp_path/'good')
    assert (root/'nested.zip').is_file()
    monkeypatch.setattr(module,'MAX_FILES',1)
    with pytest.raises(ValueError):extract_archive(path,tmp_path/'bad')
    monkeypatch.setattr(module,'MAX_FILES',5000)
    monkeypatch.setattr(module,'MAX_EXPANDED',2)
    with pytest.raises(ValueError):extract_archive(path,tmp_path/'bad2')

def test_bomb_ratio(tmp_path):
    path=tmp_path/'bomb.zip'
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED) as z:z.writestr('a.ts',b'0'*(2*1024*1024))
    with pytest.raises(ValueError):extract_archive(path,tmp_path/'out')

def test_wrapper_and_readonly(tmp_path):
    root=extract_archive(archive(tmp_path,['repo/src/main.ts']),tmp_path/'out')
    identity=freeze(root)
    assert identity==fingerprint(root)
    assert not (root/'src/main.ts').stat().st_mode & stat.S_IWRITE
    # The file flag is a guard against accidental writes, not an OS security boundary.
    os.chmod(root/'src/main.ts',stat.S_IWRITE|stat.S_IREAD)

@pytest.mark.parametrize('url',['http://github.com/a/b','https://github.com.evil/a/b','https://a:b@github.com/a/b','https://github.com/a/b?x=1','https://github.com/a/../b','file:///repo','https://github.com/a/b/tree/main'])
def test_github_allowlist(url):
    with pytest.raises(ValueError):parse_url(url)

def test_github_commit_archive(tmp_path,monkeypatch):
    import app.ingestion.github as module
    import httpx
    sha='a'*40
    visited=[]
    def handler(request):
        visited.append(str(request.url))
        if request.url.host=='api.github.com':return httpx.Response(200,json={'sha':sha})
        return httpx.Response(200,content=b'zip')
    original=httpx.Client
    monkeypatch.setattr(module.httpx,'Client',lambda **kw: original(transport=httpx.MockTransport(handler),**kw))
    result=retrieve('https://github.com/owner/repo.git',tmp_path/'source.zip')
    assert result['commit']==sha
    assert visited==['https://api.github.com/repos/owner/repo/commits/HEAD',f'https://codeload.github.com/owner/repo/zip/{sha}']
