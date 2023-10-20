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

- [x] list key differ
- [x] dict key differ
- [x] diff-action mapper
- [ ] markup parsing
- [ ] refactor
- [ ] final user-configuration interfaces

- [ ] custom doc-generation with pdoc3
- [ ] documentation

- [ ] integration/compatiblity with dynaconf
- [ ] benchmark
- [ ] final touches

## Preview

The test are organized in Case classes (under `tests/cases`), which condensate basic setup, input and output data for testing and documentation.

```python
$ pip install -e .
$ pytest -sv --no-summary # overview
```

## About merging stragegies and the implementation logic

Merge Strategy refers to a specific way in which two object will join togheter, more
specifically, a way in which the new object will be merged on the old object, that
will be mutated.

In the context of Dynaconf, it mostly applies for cases involving **container object**
(list and dict types), as Dynaconf will always use a replace strategy when there is at
least one  **terminal object** (non-container) or, in general, two object of
different types (e.g, merge a list in a dict is not supported).

The current framework tries to generalize these **object-types combinations** in order to
make it a very predictable process. As a consequence, it should be straighfoward to
customize the default object-type mappings to allow less common merge strategies.

Another way in which this tries to be configurable is by defining some **context-specific
hooks** that can modify the merging strategy for that scope and/or for descendent scopes.

An example is that the specific builtin behavior of the **root-level** (level-0)
of Dynaconf, which has a distinc default behavior: it merges by default on root, but
not in it descendents. This is achived by specifying a hook that modifies the **local
merge policy** to True when the **traversal path**  is at `/root`, that is, when
the container the algorithm is located at a given moment is working on how to merge
the new-root into the old-root.

### Merging Algorithm

It is worth noting that a merge takes two parts, and old object (that will be mutated)
and a new object that will be merged on the old.

Also, merge only makes sense when trying to merge two object that have the same path-key.
E.g, we won't try to merge `a.b.c=[1,2,3]` into `a.b.d=[4,5,6]`, because they have
different path-keys `(a.b.c != a.b.d)`. On the other hand, it can potentially be merged
if at least the path-key are the same, as in `a.b.c=[1,2,3]` into `a.b.c=[4,5,6]`.

I've called this step of evaluating if we will bother trying to merge two objects
Conflict Cases Analysis (that's word is not explicit in the code). We can represent three
cases when comparing the keys of two container objects, so we can choose what we'll
try to do.


**1) Conflict case**

```python
(key='a', "valueA", "valueB")
```

Both containers have a value for key 'a'. It doesnt metter at this point
if `valueA==valueB` or not. This just represents the conflict at 'a'.

**2) New-Only case**

```python
 (key='a', None, "valueB")
```

Only the new container have a value for key 'a', which is `valueB`.
`None` in this case represent that the old container does not contain any key 'a'.

The default interpretation for this is that we can safely add the key-value
`{'a': "valueB"}` to the old container by simple subscription: `old_container['a']="valueB"`
(altough this is not done in this step yet).


**3) Old-Only case**

```python
(key='a', "valueA", None)
```

Similar to the above, but only the old-container have the key 'a'.

The default interpretation is that Nothing needs to be done, but this generalization
open the possibility to add some "mask-mode": if `'a'` is not present in the new container,
then it should be deleted, so only match values are kept in the old container. 

#### Lists don't have keys (WIP)

This logic works great for dictionaries, but it is not very clear for lists. If we
assume the index is the key, we'll have a not very common way of merging, which is
strictly positional. Usually one tends to have items appended, or appended only if
unique. But we can do some tricks to describe those cases in terms of different
things we'll call "keys", which I'll call **pseudo keys**.

One way is the positional one, which uses index as key. If we want to always append,
we can use a pseudo-key in the format `{old|new}{index}`, so they'll never conflict.

```python
$ diff(["foo", "bar"], ["spam", "eggs"])
(key="old-0", "foo", None) # default to no-ops
(key="old-1", "bar", None) # default to no-ops
(key="new-0", None, "spam") # default to append
(key="new-1", None, "eggs") # default to append
```

It is like we were doing (actually, thats what the implemenation does):

```python
$ diff({"old-0", "foo","old-1": "bar"}, {"new-0": "spam", "new-1": "eggs"})
```

We can do it if we want append if unique strategy too:
(WIP)




