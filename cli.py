import tempfile

import click

from pydbml import PyDBML
from fideslang.manifests import ingest_manifests, write_manifest

from dbml_to_fides.transform import dbml_to_fides_dataset_dict, merge_fides_dataset_dicts


@click.command()
@click.argument('dbml', type=click.File('r'))
@click.option('--base-dataset', type=click.Path(exists=True))
@click.option('--output-file', type=click.Path())
def transform_and_merge(dbml, base_dataset, output_file):
    _dbml = PyDBML(dbml)
    _fides_dataset_dict = dbml_to_fides_dataset_dict(_dbml)

    if base_dataset is not None:
        _base_dataset_dict = ingest_manifests(base_dataset)
        _fides_dataset_dict = merge_fides_dataset_dicts(_base_dataset_dict, _fides_dataset_dict)

    if output_file is None:
        with tempfile.NamedTemporaryFile() as f:
            write_manifest(f.name, _fides_dataset_dict, "dataset")
            click.echo(f.read())
    else:
        write_manifest(output_file, _fides_dataset_dict, "dataset")

if __name__ == '__main__':
    transform_and_merge()
