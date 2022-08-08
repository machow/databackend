```python
import numpy as np
import pandas as pd

from siuba.data import mtcars

# imported from tidy.py in this folder
from tidy import tidy
```

## fit statsmodels ----


```python
import statsmodels.api as sm
import statsmodels.formula.api as smf

results = smf.ols('mpg ~ hp', data=mtcars).fit()

tidy_sm = tidy(results)

tidy_sm
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
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>term</th>
      <th>estimate</th>
      <th>std_err</th>
      <th>statistic</th>
      <th>p_value</th>
      <th>conf_int_low</th>
      <th>conf_int_high</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Intercept</td>
      <td>30.098861</td>
      <td>1.633921</td>
      <td>18.421246</td>
      <td>6.642736e-18</td>
      <td>26.761949</td>
      <td>33.435772</td>
    </tr>
    <tr>
      <th>1</th>
      <td>hp</td>
      <td>-0.068228</td>
      <td>0.010119</td>
      <td>-6.742389</td>
      <td>1.787835e-07</td>
      <td>-0.088895</td>
      <td>-0.047562</td>
    </tr>
  </tbody>
</table>
</div>



## fit scikit ----


```python
from sklearn.linear_model import LinearRegression

X = mtcars[['hp']]
y = mtcars['mpg']

# y = 1 * x_0 + 2 * x_1 + 3
reg = LinearRegression().fit(X, y)

tidy_sk = tidy(reg)

tidy_sk
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
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>term</th>
      <th>estimate</th>
      <th>std_error</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>30.098861</td>
      <td>&lt;NA&gt;</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>-0.068228</td>
      <td>&lt;NA&gt;</td>
    </tr>
  </tbody>
</table>
</div>



## fit pymc3 ----


```python
from pymc3 import Model, HalfCauchy, Normal, sample

x = mtcars['hp'].values
y = mtcars['mpg'].values

data = dict(x=x, y=y)

np.random.seed(999999)
with Model() as model: # model specifications in PyMC3 are wrapped in a with-statement
    # Define priors
    sigma = HalfCauchy('sigma', beta=10, testval=1.)
    intercept = Normal('intercept', 0, sigma=20)
    x_coeff = Normal('hp', 0, sigma=20)

    # Define likelihood
    likelihood = Normal('mpg', mu=intercept + x_coeff * x,
                        sigma=sigma, observed= y)

    # Inference!
    trace = sample(500, cores=2, progressbar = False) # draw 3000 posterior samples using NUTS sampling
    
tidy_pymc3 = tidy(trace)

tidy_pymc3
```

    /Users/machow/.virtualenvs/databackend/lib/python3.8/site-packages/deprecat/classic.py:215: FutureWarning: In v4.0, pm.sample will return an `arviz.InferenceData` object instead of a `MultiTrace` by default. You can pass return_inferencedata=True or return_inferencedata=False to be safe and silence this warning.
      return wrapped_(*args_, **kwargs_)
    Auto-assigning NUTS sampler...
    Initializing NUTS using jitter+adapt_diag...
    Multiprocess sampling (2 chains in 2 jobs)
    NUTS: [hp, intercept, sigma]
    /Users/machow/.virtualenvs/databackend/lib/python3.8/site-packages/scipy/stats/_continuous_distns.py:624: RuntimeWarning: overflow encountered in _beta_ppf
      return _boost._beta_ppf(q, a, b)
    /Users/machow/.virtualenvs/databackend/lib/python3.8/site-packages/scipy/stats/_continuous_distns.py:624: RuntimeWarning: overflow encountered in _beta_ppf
      return _boost._beta_ppf(q, a, b)
    Sampling 2 chains for 1_000 tune and 500 draw iterations (2_000 + 1_000 draws total) took 3 seconds.
    The acceptance probability does not match the target. It is 0.8794624791437439, but should be close to 0.8. Try to increase the number of tuning steps.





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
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>term</th>
      <th>estimate</th>
      <th>std_err</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>intercept</td>
      <td>30.051721</td>
      <td>1.705625</td>
    </tr>
    <tr>
      <th>1</th>
      <td>hp</td>
      <td>-0.068023</td>
      <td>0.010389</td>
    </tr>
    <tr>
      <th>2</th>
      <td>sigma</td>
      <td>4.030565</td>
      <td>0.557375</td>
    </tr>
  </tbody>
</table>
</div>


