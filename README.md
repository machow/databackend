
# databackend

The `databackend` package allows you to register a subclass, without
needing to import the subclass itself. This is useful for implementing
actions over optional dependencies.

## Example

### Setup

``` python
from databackend import AbstractBackend

class AbstractPandasFrame(AbstractBackend):
    _backends = [("pandas", "DataFrame")]


class AbstractPolarsFrame(AbstractBackend):
    _backends = [("polars", "DataFrame")]


from pandas import DataFrame

issubclass(DataFrame, AbstractPandasFrame)
isinstance(DataFrame(), AbstractPandasFrame)
```

    True

### Simple use: isinstance to switch behavior

The `fill_na()` function below can handle both pandas and polars
DataFrames.

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

### Advanced use: generic function dispatch

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
