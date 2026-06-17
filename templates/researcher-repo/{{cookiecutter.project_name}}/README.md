# {{ cookiecutter.project_name }}

{{ cookiecutter.subproject_description }}

## Setup

```bash
uv sync
```

## Catalog access

Authenticate to the EyeAI Deriva catalog:

```bash
deriva-globus-auth-utils login --host www.eye-ai.org
```

## Requesting catalog changes

If your work requires a new column or feature in the EyeAI catalog, open a
[Feature Registration Request](https://github.com/eye-ai-usc/data-curation/issues/new?template=feature-registration.md)
in the data-curation repo. Do not modify catalog schema from this repo.

## Stack

- `eye-ai` {{ cookiecutter.eye_ai_version }}
- `deriva-ml` {{ cookiecutter.deriva_ml_version }}
- Python {{ cookiecutter.python_version }}

See the [compatibility matrix](https://github.com/eye-ai-usc/eye-ai-platform/blob/main/docs/releases/compatibility-matrix.md)
before updating dependencies.
