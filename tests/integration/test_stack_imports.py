"""
Smoke tests for the blessed stack. These run in CI (unauthenticated) to verify
that the packages install and import correctly. They do not connect to the catalog.
"""


def test_eye_ai_imports():
    import eye_ai  # noqa: F401


def test_deriva_ml_imports():
    import deriva_ml  # noqa: F401


def test_eye_ai_version():
    import importlib.metadata
    version = importlib.metadata.version("eye-ai")
    assert version, "eye-ai version should not be empty"


def test_deriva_ml_version():
    import importlib.metadata
    version = importlib.metadata.version("deriva-ml")
    assert version, "deriva-ml version should not be empty"
