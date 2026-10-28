# demo-repo

A small Flask Bookmarks API used only to exercise a reusable CloudGuard CI workflow from another repository. It keeps dependencies to Flask and Werkzeug so scanners have a small, predictable surface.

## Layout

- `app/` — Flask package (`create_app()` factory, in-memory bookmarks store)
- `tests/` — pytest coverage of the HTTP API
- `requirements.in` / `requirements-dev.in` — pinned top-level deps
- `requirements.txt` / `requirements-dev.txt` — hash-locked install files (generate with the Docker `pip-compile` command below; needed before `docker build` and the CI test install)
- `Dockerfile` — non-root Python 3.13 image
- `.github/workflows/security.yml` — caller for the reusable CloudGuard workflow
- `sonar-project.properties` — Sonar sources/tests/coverage paths

## Hash-locked requirements

Generate `requirements.txt` and `requirements-dev.txt` with Python 3.13 in Docker (hashes must match the image platform):

```bash
docker run --rm -v "$PWD":/work -w /work python:3.13-slim sh -c "pip install -q pip-tools && pip-compile --generate-hashes -o requirements.txt requirements.in && pip-compile --generate-hashes -o requirements-dev.txt requirements-dev.in"
```

On Windows PowerShell, use `-v "${PWD}:/work"` instead of `-v "$PWD":/work`.

## Run locally

```bash
python -m venv .venv
.venv/Scripts/activate   # Windows
# source .venv/bin/activate  # macOS/Linux
pip install --require-hashes --only-binary=:all: -r requirements-dev.txt
python -m app.main
```

The app listens on `APP_HOST` (default `127.0.0.1`) and `APP_PORT` (default `8080`).

## Docker

```bash
docker build -t demo-repo .
docker run --rm -p 8080:8080 demo-repo
```

Health: `GET http://127.0.0.1:8080/health`

## Deploying

Publish and deploy run only through CloudGuard reusable workflows (no publish/deploy jobs live in this repo). On push to `main`, `security.yml` calls `cloudguard-publish.yml` with `environment: production`, which should be restricted to the `main` branch.

Set these GitHub repository variables:

- `ACR_LOGIN_SERVER`
- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`
- `AZURE_RESOURCE_GROUP`
- `AZURE_CONTAINER_APP`
- `ENABLE_DEPLOY` — set to `true` to deploy after publish; otherwise the image is published only

The container listens on port **8080** and exposes `GET /health`. See CloudGuard [docs/using-cloudguard.md](https://github.com/avniijain/cloudguard/blob/main/docs/using-cloudguard.md).

## Tests

```bash
pytest -v --cov=app --cov-report=xml --cov-report=term
```

## Secrets and placeholders

Repo secrets (GitHub):

- `SONAR_TOKEN`
- `SONAR_HOST_URL`

Placeholders to fill in before the workflow can run:

- `REPLACE_WITH_BRANCH_OR_TAG` in `.github/workflows/security.yml` — cloudguard reusable workflow ref
- `REPLACE_WITH_SONAR_ORG` in `.github/workflows/security.yml` — Sonar organization
- `REPLACE_WITH_DEMO_KEY` in `sonar-project.properties` — Sonar project key

Do not commit real tokens. Organization is passed by the workflow input, not stored as `sonar.organization`.

## Scenarios to test

### Clean push

1. Fill in the placeholders and add `SONAR_TOKEN` / `SONAR_HOST_URL` repo secrets.
2. Push `main` (or the default branch) with the stock Flask 3.1.3 / Werkzeug 3.1.9 lockfiles.
3. Confirm the `cloudguard` job completes and the image build/tests/scans succeed.

### Feature branch

1. Create a branch, make a harmless change (for example README wording).
2. Push the branch.
3. Confirm the workflow runs on `push` without a pull request.

### Pull request

1. Open a PR from the feature branch into the default branch.
2. Confirm the workflow runs on `pull_request` and can post security results.

### Vulnerable change

1. Set `Werkzeug==3.1.3` in `requirements.in`.
2. Recompile both lockfiles with Python 3.13:

   ```bash
   docker run --rm -v "$PWD":/work -w /work python:3.13-slim sh -c "pip install -q pip-tools && pip-compile --generate-hashes -o requirements.txt requirements.in && pip-compile --generate-hashes -o requirements-dev.txt requirements-dev.in"
   ```

3. Push or open a PR and confirm the scanner/policy gate flags the known-vulnerable pin.

### Weakened policy

1. Add a policy file (for example `policy.yml`) with `block_score: 90`.
2. Pass it into the reusable workflow via the `policy-file` input in `.github/workflows/security.yml`.
3. Push and confirm the gate uses the weaker threshold.

### Report-only mode

1. Enable report-only (or equivalent non-blocking) mode on the reusable workflow input, if configured in cloudguard.
2. Push a finding-producing change and confirm the job reports issues without failing the gate.

### Sonar secrets removed

1. Remove `SONAR_TOKEN` and/or `SONAR_HOST_URL` from repo secrets.
2. Re-run the workflow pipeline.
3. Confirm Sonar steps fail or skip as designed, without leaking secret values in logs.

Pipeline test.
