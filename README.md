# Merge Engine Prototype for Dynaconf 3.x

This is a prototype of a new merge engine to dynaconf v3.x

The main goals are:

* Incorporate ideas from https://github.com/dynaconf/dynaconf/issues/299
* Add flexible structural definitions of merge-strategies (by path, depth, type patterns, ...)
* Review in-place marks (dict-scope, list-scope, inline)
* Reference documentation for merge behavior (synced with tests).

The main restrictions are:

* Full compatiblity with existing dynaconf tests
* Similar or better performance

Some possibilities:

* Re-think inspect storage schema.

## Roadmap

- [/] list key differ
- [/] dict key differ
- [ ] diff-action mapper
- [ ] final user-configuration interfaces
- [ ] refactor

- [ ] custom doc-generation with pdoc3
- [ ] documentation

- [ ] integration/compatiblity with dynaconf
- [ ] benchmark
- [ ] final touches

## Preview

```python
$ pip install -e .
$ dynamerge-diff-cases
```

## Configurables assets

* Map of **(type, type):strategy**, where (type, type) is a value conflict representaiton.
* Map of **path:strategy**
* Map of **depth:strategy**
* List identity modes:
  use_index - use index as item id
  use_value_hash - use hash values as item id and pseudo-id for non-hashable
  always_disjoint - consider (old,new) disjoint sets

