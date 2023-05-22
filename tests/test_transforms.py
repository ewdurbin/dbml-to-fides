import json
from pprint import pprint as pp

import pytest

from fideslang.manifests import ingest_manifests

from dbml_to_fides.transform import unlistify, relistify


@pytest.mark.parametrize(
    ("dataset_file",),
    [
        ("tests/data/demo_dataset.yml",),
        ("tests/data/fides_db_dataset.yml",),
        ("tests/data/fides_redis_dataset.yml",),
        ("tests/data/sample_dataset.yml",),
    ],
)
def test_roundtrip_listify(dataset_file):
    manifest = ingest_manifests(dataset_file)
    assert manifest == relistify(unlistify(manifest))
