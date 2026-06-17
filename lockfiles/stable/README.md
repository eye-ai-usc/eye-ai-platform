# lockfiles/stable/

The current blessed dependency stack for EyeAI research repos.

## Files

- **`manifest.toml`** - human-readable version manifest
- **`uv.lock`** - machine-generated lockfile *(to be generated - see instructions below)*

## Generating uv.lock

Run locally and commit the output:

```bash
cd /tmp && uv init --python 3.12 eyeai-stable && cd eyeai-stable && \
uv add \
  "eye-ai @ git+https://github.com/eye-ai-usc/eye-ai-ml.git@v1.5.3" \
  "deriva-ml @ git+https://github.com/informatics-isi-edu/deriva-ml.git@v1.17.10" && \
cat uv.lock
```
