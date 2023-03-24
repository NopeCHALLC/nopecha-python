# NopeCHA Python Library

The NopeCHA Python library provides convenient access to the NopeCHA API
from applications written in the Python language. It includes a
pre-defined set of classes for API resources that initialize
themselves dynamically from API responses.


## Supported CAPTCHA types:
- reCAPTCHA v2
- reCAPTCHA v3
- reCAPTCHA Enterprise
- hCaptcha
- hCaptcha Enterprise
- FunCAPTCHA
- AWS WAF CAPTCHA
- Text-based CAPTCHA


## Documentation

See the [NopeCHA API docs](https://developers.nopecha.com).


## Installation

You don't need this source code unless you want to modify the package. If you just
want to use the package, just run:

```sh
pip install --upgrade nopecha
```

Install from source with:

```sh
python setup.py install
```

## Usage

The library needs to be configured with your account's secret key which is available on the [website](https://nopecha.com/manage). Either set it as the `NOPECHA_API_KEY` environment variable before using the library:

```bash
export NOPECHA_API_KEY='...'
```

Or set `nopecha.api_key` to its value:

```python
import nopecha
nopecha.api_key = "..."

# solve a recognition challenge
clicks = nopecha.Recognition.solve(
    type='hcaptcha',
    task='Please click each image containing a cat-shaped cookie.',
    image_urls=[f"https://nopecha.com/image/demo/hcaptcha/{i}.png" for i in range(9)],
)

# print the grids to click
print(clicks)

# solve a token
token = nopecha.Token.solve(
    type='hcaptcha',
    sitekey='ab803303-ac41-41aa-9be1-7b4e01b91e2c',
    url='https://nopecha.com/demo/hcaptcha',
)

# print the token
print(token)

# get the current balance
balance = nopecha.Balance.get()

# print the current balance
print(balance)
```

## Requirements

- Python 3.7.1+

In general, we want to support the versions of Python that our
customers are using. If you run into problems with any version
issues, please let us know at support@nopecha.com.
