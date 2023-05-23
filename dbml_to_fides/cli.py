import tempfile

import click
import yaml

from pydbml import PyDBML
from fideslang.manifests import ingest_manifests, write_manifest

from dbml_to_fides.transform import (
    dbml_to_fides_dataset_dict,
    merge_fides_dataset_dicts,
)


@click.command()
@click.argument("dbml", type=click.File("r"))
@click.option(
    "--include-fides-keys",
    is_flag=True,
    show_default=True,
    default=False,
    help="Include full Fides dataset manifest key structure, generally most helpful for initial conversion.",
)
@click.option(
    "--base-dataset",
    type=click.Path(exists=True),
    help="Base dataset, if provided the resulting converted DBML act as an update over this.",
)
@click.option(
    "--output-file", type=click.Path(), help="Target file for writing the result."
)
def transform_and_merge(dbml, include_fides_keys, base_dataset, output_file):
    """Convert a given DBML to a Fides dataset manifest

    DBML is the path to the source file.
    """
    _dbml = PyDBML(dbml)
    _fides_dataset_dict = dbml_to_fides_dataset_dict(
        _dbml, include_fides_keys=include_fides_keys
    )

    if base_dataset is not None:
        _base_dataset_dict = ingest_manifests(base_dataset)
        _fides_dataset_dict = merge_fides_dataset_dicts(
            _base_dataset_dict, _fides_dataset_dict
        )

    if output_file is None:
        click.echo(yaml.dump(_fides_dataset_dict, sort_keys=False, indent=2), nl=False)
    else:
        with open(output_file, "w") as f:
            yaml.dump(_fides_dataset_dict, f, sort_keys=False, indent=2)


if __name__ == "__main__":
    transform_and_merge()
