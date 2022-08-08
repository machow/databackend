
# databackend

The `databackend` package allows you to register a subclass, without
needing to import the subclass itself. This is useful for implementing
actions over optional dependencies.

## Example

For this example, we’ll implement a function, `fill_na()`, that fills in
missing values in a DataFrame. It works with DataFrame objects from two
popular libraries: `pandas` and `polars`. Importantly, neither library
needs to be installed.

### Setup

The code below defines “abstract” parent classes for each of the
DataFrame classes in the two libraries.

``` python
from databackend import AbstractBackend

class AbstractPandasFrame(AbstractBackend):
    _backends = [("pandas", "DataFrame")]


class AbstractPolarsFrame(AbstractBackend):
    _backends = [("polars", "DataFrame")]
```

Note that the abstract classes can be used as stand-ins for the real
thing in `issubclass()` and `isinstance`.

``` python
from pandas import DataFrame

issubclass(DataFrame, AbstractPandasFrame)
isinstance(DataFrame(), AbstractPandasFrame)
```

    True

### Simple fill_na: isinstance to switch behavior

The `fill_na()` function below uses custom handling for pandas and
polars.

``` python
def fill_na(data, x):
    if isinstance(data, AbstractPandasFrame):
        return data.fillna(x)
    elif isinstance(data, AbstractPolarsFrame):
        return data.fill_nan(x)
```

Notice that neither `pandas` nor `polars` need to be imported when
defining `fill_na()`.

Here is an example of calling `fill_na()` on both kinds of DataFrames.

``` python
# handle pandas ----

import pandas as pd

df = pd.DataFrame({"x": [1, 2, None]})
fill_na(df, 3)


# handle polars ----

import polars as pl

df = pl.DataFrame({"x": [1, 2, None]})
fill_na(df, 3)
```

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }

    .dataframe td {
        white-space: pre;
    }

    .dataframe td {
        padding-top: 0;
    }

    .dataframe td {
        padding-bottom: 0;
    }

    .dataframe td {
        line-height: 95%;
    }
</style>
<table border="1" class="dataframe" >
<small>shape: (3, 1)</small>
<thead>
<tr>
<th>
x
</th>
</tr>
<tr>
<td>
i64
</td>
</tr>
</thead>
<tbody>
<tr>
<td>
1
</td>
</tr>
<tr>
<td>
2
</td>
</tr>
<tr>
<td>
null
</td>
</tr>
</tbody>
</table>
</div>

The key here is that a user could have only pandas, or only polars,
installed. Importantly, doing the isinstance checks do not import any
libraries!

### Advanced fill_na: generic function dispatch

`databackend` shines when combined with [generic function
dispatch](https://mchow.com/posts/2020-02-24-single-dispatch-data-science/).
This is a programming approach where you declare a function
(e.g. `fill_na()`), and then register each backend specific
implementation on the function.

Python has a built-in function implementing this called
`functools.singledispatch`.

Here is an example of the previous `fill_na()` function written using
it.

``` python
from functools import singledispatch

@singledispatch
def fill_na2(data, x):
    raise NotImplementedError(f"No support for class: {type(data)}")

# handle pandas ----

@fill_na2.register
def _(data: AbstractPandasFrame, x):
    return data.fillna(x)

@fill_na2.register
def _(data: AbstractPolarsFrame, x):
    return data.fill_nan(x)
```

Note two important decorators:

-   `@singledispatch` defines a default function. This gets called if no
    specific implementations are found.
-   `@fill_na2.register` defines specific versions of the function.

Here’s an example of it in action.

``` python
# example ----

import pandas as pd
import polars as pl

df = pd.DataFrame({"x": [1, 2, None]})
fill_na2(df, 3)

df = pl.DataFrame({"x": [1, 2, None]})
fill_na2(df, 3)
```

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }

    .dataframe td {
        white-space: pre;
    }

    .dataframe td {
        padding-top: 0;
    }

    .dataframe td {
        padding-bottom: 0;
    }

    .dataframe td {
        line-height: 95%;
    }
</style>
<table border="1" class="dataframe" >
<small>shape: (3, 1)</small>
<thead>
<tr>
<th>
x
</th>
</tr>
<tr>
<td>
i64
</td>
</tr>
</thead>
<tbody>
<tr>
<td>
1
</td>
</tr>
<tr>
<td>
2
</td>
</tr>
<tr>
<td>
null
</td>
</tr>
</tbody>
</table>
</div>

### How it works

Under the hood, `AbstractBackend` behaves similarly to python’s builtin
[`abc.ABC` class](https://docs.python.org/3/library/abc.html#abc.ABC).

``` python
from abc import ABC

class MyABC(ABC):
    pass

from io import StringIO
MyABC.register(StringIO)
```

    _io.StringIO

The key difference is that you can specify the virtual subclass using
the tuple `("<mod_name>", "<class_name>")`.

When `issubclass(SomeClass, AbstractBackend)` runs, then…

-   The standard ABC caching mechanism is checked, and potentially
    returns the answer immediately.
-   Otherwise, a subclass hook cycles through registered backends.
-   The hook runs the subclass check for any backends that are imported
    (e.g. are in `sys.modules`).

Technically, `AbstractBackend` inherits all the useful metaclass things
from `abc.ABCMeta`, so these can be used also.
