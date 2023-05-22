from collections import defaultdict
from copy import deepcopy
from typing import Dict

from deepmerge import always_merger
from pydbml.database import Database


def unlistify(manifest):
    unlistified = {"dataset": {}}
    for dataset in deepcopy(manifest["dataset"]):
        collections = {}
        for collection in dataset["collections"]:
            collections[collection["name"]] = collection
            collections[collection["name"]]["fields"] = {
                field["name"]: field
                for field in collections[collection["name"]]["fields"]
            }
        dataset["collections"] = collections
        unlistified["dataset"][dataset["name"]] = dataset
    return unlistified


def relistify(manifest):
    relistified = {"dataset": []}
    for dataset in deepcopy(manifest["dataset"]).values():
        collections = []
        for collection in dataset["collections"].values():
            collection["fields"] = list(collection["fields"].values())
            collections.append(collection)
        dataset["collections"] = collections
        relistified["dataset"].append(dataset)
    return relistified


def merge_fides_dataset_dicts(existing, new):
    _existing = unlistify(existing)
    _new = unlistify(new)

    updated = always_merger.merge(_existing, _new)

    return relistify(updated)


def dbml_to_fides_dataset_dict(dbml: Database) -> Dict:
    collections = defaultdict(list)
    for table in dbml.tables:
        collection = {}
        collection["name"] = table.name
        if table.note:
            collection["description"] = str(table.note)

        fields = []
        for column in table.columns:
            field = {}
            field["name"] = column.name

            fidesops_meta = {}
            if column.pk:
                fidesops_meta["primary_key"] = True

            fidesops_meta_references = []
            for reference in column.get_refs():
                if reference.table1 == table:
                    direction = "to"
                    ref_field = f"{reference.table2.name}.{reference.col2[0].name}"
                    ref_dataset = reference.table2.schema
                elif reference.table2 == table:
                    direction = "from"
                    ref_field = f"{reference.table1.name}.{reference.col1[0].name}"
                    ref_dataset = reference.table1.schema
                reference = {
                    "dataset": ref_dataset,
                    "field": ref_field,
                    "direction": direction,
                }
                fidesops_meta_references.append(reference)

            if fidesops_meta_references:
                fidesops_meta["references"] = fidesops_meta_references

            if fidesops_meta:
                field["fidesops_meta"] = fidesops_meta

            fields.append(field)

        if fields:
            collection["fields"] = fields

        collections[table.schema].append(collection)

    return {
        "dataset": [
            {"name": schema, "collections": _collections}
            for schema, _collections in collections.items()
        ]
    }
