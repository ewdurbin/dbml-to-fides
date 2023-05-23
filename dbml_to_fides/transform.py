from collections import defaultdict
from copy import deepcopy
from typing import Dict

from deepmerge import always_merger
from pydbml.database import Database

dataset_keys = {
    "fides_key": None,
    "name": None,
    "description": None,
    "organization_fides_key": None,
    "meta": {},
    "third_country_transfers": [],
    "joint_controller": [],
    "retention": None,
    "data_categories": [],
    "data_qualifiers": [],
}

collection_keys = {
    "name": None,
    "description": None,
    "data_categories": [],
    "data_qualifiers": [],
    "retention": None,
}

field_keys = {
    "name": None,
    "description": None,
    "data_categories": [],
    "data_qualifier": None,
    "retention": None,
}


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
            for field in collections[collection["name"]]["fields"].values():
                references = {}
                for reference in field.get("fides_meta", {}).get("references", []):
                    references[
                        f"{reference['dataset']}:{reference['field']}"
                    ] = reference
                if references:
                    field["fides_meta"]["references"] = references
        dataset["collections"] = collections
        unlistified["dataset"][dataset["name"]] = dataset
    return unlistified


def relistify(manifest):
    relistified = []
    for dataset in deepcopy(manifest["dataset"]).values():
        collections = []
        for collection in dataset["collections"].values():
            collection["fields"] = list(collection["fields"].values())
            for field in collection["fields"]:
                references = list(
                    field.get("fides_meta", {}).get("references", {}).values()
                )
                if references:
                    field["fides_meta"]["references"] = references
            collections.append(collection)
        dataset["collections"] = collections
        relistified.append(dataset)
    return {"dataset": relistified}


def merge_fides_dataset_dicts(existing, new):
    _existing = unlistify(existing)
    _new = unlistify(new)

    updated = always_merger.merge(_existing, _new)

    return relistify(updated)


def dbml_to_fides_dataset_dict(
    dbml: Database, include_fides_keys: bool = False
) -> Dict:
    collections = defaultdict(list)
    for table in dbml.tables:
        collection = {**(deepcopy(collection_keys) if include_fides_keys else {})}

        collection["name"] = table.name
        if table.note:
            collection["description"] = str(table.note)

        fields = []
        for column in table.columns:
            field = {**(deepcopy(field_keys) if include_fides_keys else {})}

            field["name"] = column.name
            if column.note:
                field["description"] = str(column.note)

            fides_meta = {}
            if column.pk:
                fides_meta["primary_key"] = True

            fides_meta_references = []
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
                fides_meta_references.append(reference)

            if fides_meta_references:
                fides_meta["references"] = fides_meta_references

            if fides_meta:
                field["fides_meta"] = fides_meta

            fields.append(field)

        if fields:
            collection["fields"] = fields

        collections[table.schema].append(collection)

    return {
        "dataset": [
            {
                **(deepcopy(dataset_keys) if include_fides_keys else {}),
                "name": schema,
                "collections": _collections,
            }
            for schema, _collections in collections.items()
        ]
    }
