import json
from pprint import pprint as pp

import pytest

from fideslang.manifests import ingest_manifests
from pydbml import PyDBML

from dbml_to_fides.transform import (
    unlistify,
    relistify,
    dbml_to_fides_dataset_dict,
    merge_fides_dataset_dicts,
)


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


@pytest.mark.parametrize(
    ("dataset_file", "dbml_file"),
    [
        ("tests/data/sample_dataset.yml", "tests/data/sample.dbml"),
        ("tests/data/schema_def_dataset_min.yml", "tests/data/schema_def.dbml"),
    ],
)
def test_merge(dataset_file, dbml_file):
    manifest = ingest_manifests(dataset_file)
    dbml = PyDBML(open(dbml_file, "r").read())

    assert manifest == merge_fides_dataset_dicts(
        manifest, dbml_to_fides_dataset_dict(dbml)
    )
