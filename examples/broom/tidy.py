from databackend import AbstractBackend
from functools import singledispatch

# Abstract backend classes ====================================================


class BaseSklearnModel(AbstractBackend):
    _backends = [("sklearn.linear_model", "LinearRegression")]


class BaseSmRegressionResult(AbstractBackend):
    _backends = [("statsmodels.regression.linear_model", "RegressionResultsWrapper")]


class BasePymcMultiTrace(AbstractBackend):
    _backends = [("pymc3.backends.base", "MultiTrace")]


# Implement generic function: tidy ============================================


@singledispatch
def tidy(fit, *args, **kwargs):
    raise NotImplementedError(f"No tidy method for class {fit.__class__}")


# sklearn ----


@tidy.register
def _tidy_sklearn(fit: BaseSklearnModel, col_names=None):
    from pandas import DataFrame, NA

    estimates = [fit.intercept_, *fit.coef_]

    if col_names is None:
        terms = list(range(len(estimates)))
    else:
        terms = ["intercept", *col_names]

    # pd.DataFrame()
    return DataFrame({"term": terms, "estimate": estimates, "std_error": NA})


# statsmodels ----


@tidy.register
def _tidy_statsmodels(fit: BaseSmRegressionResult):
    from statsmodels.iolib.summary import summary_params_frame

    tidied = summary_params_frame(fit).reset_index()
    rename_cols = {
        "index": "term",
        "coef": "estimate",
        "std err": "std_err",
        "t": "statistic",
        "P>|t|": "p_value",
        "Conf. Int. Low": "conf_int_low",
        "Conf. Int. Upp.": "conf_int_high",
    }

    return tidied.rename(columns=rename_cols)


# pymc3 ----


@tidy.register
def _tidy_trace(fit: BasePymcMultiTrace, robust=False):
    from pymc3 import trace_to_dataframe

    trace_df = trace_to_dataframe(fit)

    agg_funcs = ["median", "mad"] if robust else ["mean", "std"]

    # data frame with columns like: median, mad.
    tidied = trace_df.agg(agg_funcs).T.reset_index()
    tidied.columns = ["term", "estimate", "std_err"]

    return tidied
