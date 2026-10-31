from pathlib import Path
import tempfile
from typing import Literal
from fastapi import File, HTTPException, Query, UploadFile
from app.contracts import Analysis, EvidenceResponse, GithubInput, Job, View
from app.graph.projections import architecture_view, entries
from app.graph.exploration import Index
from app.tooling import inspect as inspect_tools
from app.api.presentation_models import EntityPage, RepositoryOverview, ToolReport
from app.ingestion.archive import MAX_COMPRESSED
from app.ingestion.github import parse_url

def register_routes(app, data: Path):
    def graph(snapshot):
        value = app.state.store.analysis(snapshot, graph=True)
        if value is None:
            raise HTTPException(404, 'Analysis not found')
        return value

    @app.get('/api/v1/health')
    def health():
        return {'status': 'ok', 'version': '1.0.0', 'engine': 'static-typescript', 'schema_version': 'repo-intelligence-1'}

    @app.get('/api/v1/tools',response_model=ToolReport)
    def tools():
        return inspect_tools()

    @app.get('/api/v1/analyses/{snapshot}/overview',response_model=RepositoryOverview)
    def overview(snapshot: str):
        return Index(graph(snapshot)).summary()

    @app.get('/api/v1/analyses/{snapshot}/hierarchy',response_model=EntityPage)
    def hierarchy(snapshot: str, parent_id: str | None = None, query: str = Query('',max_length=150),
                  offset: int = Query(0,ge=0), limit: int = Query(30,ge=1,le=60)):
        try:
            return Index(graph(snapshot)).hierarchy(parent_id,query,offset,limit)
        except ValueError as exc:
            raise HTTPException(422,str(exc)) from exc

    @app.get('/api/v1/analyses/{snapshot}/explore/entries',response_model=EntityPage)
    def scoped_entries(snapshot: str, scope_id: str | None = None, query: str = Query('',max_length=150),
                       offset: int = Query(0,ge=0), limit: int = Query(30,ge=1,le=60)):
        try:
            return Index(graph(snapshot)).candidates(scope_id,query,offset,limit)
        except ValueError as exc:
            raise HTTPException(422,str(exc)) from exc

    @app.post('/api/v1/analyze/github', response_model=Job, status_code=202)
    def github(body: GithubInput):
        try:
            _, repository = parse_url(body.url)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
        try:
            return app.state.jobs.submit('github', body.url, repository)
        except ValueError as exc:
            raise HTTPException(429, str(exc)) from exc

    @app.post('/api/v1/analyze/upload', response_model=Job, status_code=202)
    async def upload(file: UploadFile = File(...)):
        if not (file.filename or '').lower().endswith('.zip'):
            raise HTTPException(422, 'Upload a ZIP archive')
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(dir=data, suffix='.zip', delete=False) as stream:
                temporary = Path(stream.name)
                size = 0
                while chunk := await file.read(65536):
                    size += len(chunk)
                    if size > MAX_COMPRESSED:
                        raise HTTPException(413, 'Upload exceeds 50 MiB')
                    stream.write(chunk)
            job = app.state.jobs.submit('zip', temporary, Path(file.filename.replace('\\', '/')).name[:120])
            temporary = None
            return job
        except ValueError as exc:
            raise HTTPException(429, str(exc)) from exc
        finally:
            await file.close()
            if temporary:
                temporary.unlink(missing_ok=True)

    @app.get('/api/v1/jobs/{identifier}', response_model=Job)
    def job(identifier: str):
        value = app.state.store.job(identifier)
        if not value:
            raise HTTPException(404, 'Job not found')
        return value

    @app.post('/api/v1/jobs/{identifier}/cancel', response_model=Job)
    def cancel(identifier: str):
        value = app.state.jobs.cancel(identifier)
        if not value:
            raise HTTPException(404, 'Job not found')
        return value

    @app.get('/api/v1/analyses', response_model=list[Analysis])
    def history():
        return app.state.store.history()

    @app.get('/api/v1/analyses/{snapshot}', response_model=Analysis)
    def analysis(snapshot: str):
        value = app.state.store.analysis(snapshot)
        if not value:
            raise HTTPException(404, 'Analysis not found')
        return value

    @app.get('/api/v1/analyses/{snapshot}/entries')
    def entry_points(snapshot: str):
        return entries(graph(snapshot))

    @app.get('/api/v1/analyses/{snapshot}/view', response_model=View)
    def view(snapshot: str, kind: Literal['system', 'workflow'] = 'system', entry_id: str | None = None,
             depth: int = Query(2, ge=1, le=6), limit: int = Query(24, ge=5, le=80), dependencies: bool = False,
             layer: Literal['source','infrastructure','all'] = 'source', nested: bool = False,
             scope_id: str | None = None, show_unknown: bool = False, connections: bool = False):
        try:
            index=Index(graph(snapshot))
            return (index.system(scope_id,layer,limit,dependencies,connections) if kind=='system' else
                    index.workflow(scope_id,entry_id,depth,limit,dependencies,nested,show_unknown))
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc

    @app.get('/api/v1/analyses/{snapshot}/evidence', response_model=EvidenceResponse)
    def evidence(snapshot: str, record_id: str, kind: Literal['system', 'workflow'] = 'system',
                 layer: Literal['source','infrastructure','all'] = 'source', scope_id: str | None = None,
                 view_limit: int = Query(24,ge=5,le=80), dependencies: bool = False):
        value = graph(snapshot)
        try:
            record=Index(value).evidence_record(record_id,scope_id,layer,view_limit,dependencies)
        except ValueError as exc:
            raise HTTPException(422,str(exc)) from exc
        if record is None:
            raise HTTPException(404, 'Evidence record not found')
        identifiers = set(record.get('evidence_ids', []))
        matches = [e for e in value['evidence'] if e['id'] in identifiers]
        return {'snapshot_id': snapshot, 'record': record, 'evidence': matches[:100], 'truncated': len(matches)>100}

    @app.get('/api/v1/analyses/{snapshot}/unknowns')
    def unknowns(snapshot: str, offset: int = Query(0, ge=0), limit: int = Query(30, ge=1, le=60), scope_id: str | None = None):
        try:
            return Index(graph(snapshot)).issues(scope_id,offset,limit)
        except ValueError as exc:
            raise HTTPException(422,str(exc)) from exc

