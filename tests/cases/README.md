# Diff Cases

Because there are many and complex diff behavior cases, this module aims to provide
convenience tools for testing and documenting them.

KeyDiff here refers to a diff that won't peform a full recursive diff, but
will provide enought information for future processing (and possibly future diffs
inside containers).

The ShallDiff object provides some relevant information for post-processing. The
core information are @key_id and @diff_pair.

@key_id is the identify key used for comparision:

* For dicts, it is simply they keys.
* For lists, we can make a trick to generate a pseudo-key, which we'll call its @key_id.

There are several strategies we can use to generate this pseudo-key, such as using the
index, hashing the values, etc. We'll explore some of those here.

@diff_pair is a tuple (old_value, new_value), where 'old' refers to the data that will
receive the merge, and 'new' to the data being merged.
This tuple is related to a single @key_id, and fall intro three cases:

At key_id="a"

```
(old None) - old-only: only old have some value for key 'a'
(None, new) - new-only: only new have some value for key 'a'
(old, new) - conflict: both old and new have values for key 'a'
```

## Examples

```
# list merge [pseudo-key.use_index]
# uses positional comparision (by index)
[1, {...}, 3]
[3, {...}, 1]
------------------
Diff(0,    diff_pair=(1, 3),            real_key_pair=(0, 0))
Diff(1,    diff_pair=({...}, {...}),    real_key_pair=(1, 1))
Diff(2,    diff_pair=(3, 1),            real_key_pair=(2, 2))

# list merge [pseudo-key.use_value_hash]
# - generates id_key from value_hash.
# - uses random uuid4 for unhashable values.
[1, {...}, 3]
[3, {...}, 1]
------------------
Diff(id_key=1,        diff_pair=(1, 1),            real_key_pair=(0, 2))
Diff(id_key=3,        diff_pair=(3, 3),            real_key_pair=(2, 0))
Diff(id_key=uuid-a,   diff_pair=({...}, EMPTY),    real_key_pair=(a, a))
Diff(id_key=uuid-b,   diff_pair=(EMPTY, {...}),    real_key_pair=(a, a))

# list merge [pseudo-key.use_value_hash + special dict-id]
# - generates id_key from value_hash
# - uses id_mark inside dict to produce it's pseudo id_key
[1, {id_mark=x, ...}, 3]
[3, {id_mark=x, ...}, 1]
------------------
Diff(id_key=1,    diff_pair=(1, 1),            real_key_pair=(0, 2))
Diff(id_key=3,    diff_pair=(3, 3),            real_key_pair=(2, 0))
Diff(id_key=x,    diff_pair=({...}, {...}),    real_key_pair=(a, a))
```
