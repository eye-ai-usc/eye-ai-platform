# Experiment Tracing Guide

DerivaML traces every experiment run back to the exact catalog state and code version used.

---

## Why tracing matters

The EyeAI catalog evolves continuously. Without tracing, results cannot be reproduced
because you cannot reconstruct what data existed at training time.

DerivaML links each execution to the exact dataset, workflow definition, library versions,
and git commit of your research repo.

---

## Minimal tracing pattern

```python
from eye_ai import EyeAI

ea = EyeAI(hostname='www.eye-ai.org', catalog_id=1)

with ea.execution(workflow_rid='<workflow-RID>') as exec:
    dataset = exec.get_dataset('<dataset-RID>')
    # ... train model ...
    exec.log_metric('auc', 0.92)
    exec.upload_asset('model.pth', asset_type='Model')
```

---

## Guided workflow

```
/deriva-ml:execution-lifecycle
```

Covers pre-flight validation, running, uploading results, and debugging.

---

## See also

- [etl-workflow.md](etl-workflow.md)
- [deriva-ml docs](https://github.com/informatics-isi-edu/deriva-ml)
