# dbml-to-fides

This tool converts [DBML](https://dbml.dbdiagram.io/docs/#project-definition)
to [Fides dataset manifests](https://ethyca.github.io/fideslang/resources/dataset/).

It optionally has support for merging the result from DBML into an existing
Fides dataset manifest.

Combined, this can be used in automation to ensure that datasets are kept
up-to-date with the latest schema changes in continuous integration.

## Usage

### Basic

Given a sample DBML in `sample.dbml`:

```dbml
Table users {
  id integer [primary key]
  username varchar
  role varchar
  created_at timestamp
}

Table posts {
  id integer [primary key]
  title varchar
  body text [note: 'Content of the post']
  user_id integer
  status post_status
  created_at timestamp
}

Enum post_status {
  draft
  published
  private [note: 'visible via URL only']
}

Ref: posts.user_id > users.id // many-to-one
```

`dbml-to-fides` will output what it can infer from the DBML file as a Fides
dataset:

```sh
$ dbml-to-fides sample.dbml
dataset:
- name: public
  collections:
  - name: users
    description: Users
    fields:
    - name: id
      fides_meta:
        primary_key: true
    - name: username
    - name: role
    - name: created_at
  - name: posts
    description: All the content you crave
    fields:
    - name: id
      fides_meta:
        primary_key: true
    - name: title
    - name: body
      description: Content of the post
    - name: user_id
      fides_meta:
        references:
        - dataset: public
          field: users.id
          direction: to
    - name: status
    - name: created_at
```

### Merging with existing Fides dataset

If you have an existing Fides dataset in `.fides/sample_dataset.yml`:

```yaml
dataset:
- fides_key: sample_dataset
  organization_fides_key: default_organization
  name: public
  description: Sample dataset for my system
  meta: null
  data_categories: []
  data_qualifier: aggregated.anonymized.unlinked_pseudonymized.pseudonymized.identified
  retention: 30 days after account deletion
  collections:
  - name: users
    description: User information
    fields:
    - name: id
      fides_meta:
        primary_key: true
      description: User's unique ID
      data_categories:
      - user.unique_id
      data_qualifier: aggregated.anonymized.unlinked_pseudonymized.pseudonymized.identified
    - name: username
      description: User's username
      data_categories:
      - user.name
      data_qualifier: aggregated.anonymized.unlinked_pseudonymized.pseudonymized.identified
      retention: Account termination
    - name: role
      description: User's system level role/privilege
      data_categories:
      - system.operations
      data_qualifier: aggregated.anonymized.unlinked_pseudonymized.pseudonymized.identified
    - name: created_at
      description: User's creation timestamp
      data_categories:
      - system.operations
      data_qualifier: aggregated.anonymized.unlinked_pseudonymized.pseudonymized.identified
  - name: posts
    description: Post information
    fields:
    - name: id
      fides_meta:
        primary_key: true
      description: Post's unique ID
      data_categories:
      - system.operations
      data_qualifier: aggregated.anonymized.unlinked_pseudonymized.pseudonymized.identified
    - name: title
      description: Post's title
      data_categories:
      - system.operations
      data_qualifier: aggregated.anonymized.unlinked_pseudonymized.pseudonymized.identified
    - name: body
      description: Post's body
      data_categories:
      - system.operations
      data_qualifier: aggregated.anonymized.unlinked_pseudonymized.pseudonymized.identified
    - name: user_id
      fides_meta:
        references:
        - dataset: public
          field: users.id
          direction: to
      description: Post creator's unique User ID
      data_categories:
      - user.unique_id
      data_qualifier: aggregated.anonymized.unlinked_pseudonymized.pseudonymized.identified
    - name: status
      description: User's creation timestamp
      data_categories:
      - system.operations
      data_qualifier: aggregated.anonymized.unlinked_pseudonymized.pseudonymized.identified
    - name: created_at
      description: Post's creation timestamp
      data_categories:
      - system.operations
      data_qualifier: aggregated.anonymized.unlinked_pseudonymized.pseudonymized.identified

```

`dbml-to-fides` can be used with the
`--base-dataset` option to merge the results together.
But, in this case there are no differences:

```sh
$ diff -u .fides/sample_dataset.yml <(dbml-to-fides sample.dbml --base-dataset .fides/sample_dataset.yml)
$
```

If we introduce a change to the DBML:

```diff
@@ -3,6 +3,7 @@ Table users {
   username varchar
   role varchar
   created_at timestamp
+  social_security_number varchar
 }
 
 Table posts {
```

Then running our diff again will add the field to our Fides dataset:

```shell
$ diff -u .fides/sample_dataset.yml <(dbml-to-fides sample.dbml --base-dataset .fides/sample_dataset.yml)
--- .fides/sample_dataset.yml	2023-05-22 15:39:24
+++ /dev/fd/63	2023-05-22 15:40:07
@@ -34,6 +34,7 @@
       data_categories:
       - system.operations
       data_qualifier: aggregated.anonymized.unlinked_pseudonymized.pseudonymized.identified
+    - name: social_security_number
   - name: posts
     description: Post information
     fields:
```

### File output

If we wanted to write the output to a file,
we would add the `--output-file` flag:

```shell
$ dbml-to-fides sample.dbml --base-dataset .fides/sample_dataset.yml --output-file .fides/sample_dataset.yml
$ git diff
diff --git a/.fides/sample_dataset.yml b/.fides/sample_dataset.yml
index 594cee4..edc3141 100644
--- a/.fides/sample_dataset.yml
+++ b/.fides/sample_dataset.yml
@@ -34,6 +34,7 @@ dataset:
       data_categories:
       - system.operations
       data_qualifier: aggregated.anonymized.unlinked_pseudonymized.pseudonymized.identified
+    - name: social_security_number
   - name: posts
     description: Post information
     fields:
```

### Initial generation

If you do not have an existing Fides dataset, the `--include-fides-keys` flag will
create a more "fleshed out" version of a
[Fides dataset](https://ethyca.github.io/fideslang/resources/dataset/)
including all keys. See the [docs](https://ethyca.github.io/fideslang/resources/dataset/)
for what each field can/should be populated with.

```shell
$ dbml-to-fides sample.dbml --include-fides-keys
dataset:
- fides_key: null
  name: public
  description: null
  organization_fides_key: null
  meta: {}
  third_country_transfers: []
  joint_controller: []
  retention: null
  data_categories: []
  data_qualifiers: []
  collections:
  - name: users
    description: Users
    data_categories: []
    data_qualifiers: []
    retention: null
    fields:
    - name: id
      description: null
      data_categories: []
      data_qualifier: null
      retention: null
      fides_meta:
        primary_key: true
    - name: username
      description: null
      data_categories: []
      data_qualifier: null
      retention: null
    - name: role
      description: null
      data_categories: []
      data_qualifier: null
      retention: null
    - name: created_at
      description: null
      data_categories: []
      data_qualifier: null
      retention: null
    - name: social
      description: null
      data_categories: []
      data_qualifier: null
      retention: null
  - name: posts
    description: All the content you crave
    data_categories: []
    data_qualifiers: []
    retention: null
    fields:
    - name: id
      description: null
      data_categories: []
      data_qualifier: null
      retention: null
      fides_meta:
        primary_key: true
    - name: title
      description: null
      data_categories: []
      data_qualifier: null
      retention: null
    - name: body
      description: Content of the post
      data_categories: []
      data_qualifier: null
      retention: null
    - name: user_id
      description: null
      data_categories: []
      data_qualifier: null
      retention: null
      fides_meta:
        references:
        - dataset: public
          field: users.id
          direction: to
    - name: status
      description: null
      data_categories: []
      data_qualifier: null
      retention: null
    - name: created_at
      description: null
      data_categories: []
      data_qualifier: null
      retention: null
```
