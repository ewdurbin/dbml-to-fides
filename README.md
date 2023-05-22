# dbml-to-fides

This tool converts [DBML](https://dbml.dbdiagram.io/docs/#project-definition)
to [Fides dataset manifests](https://ethyca.github.io/fideslang/resources/dataset/).

It optionally has support for merging the result from DBML into an existing
Fides dataset manifest.

Combined, this can be used in automation to ensure that datasets are kept
up-to-date with the latest schema changes in continuous integration.
