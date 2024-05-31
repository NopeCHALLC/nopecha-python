# NopeCHA

API bindings for the [NopeCHA](https://nopecha.com) CAPTCHA service.

![PyPI - Version](https://img.shields.io/pypi/v/nopecha?label=PyPI)
![NPM Version](https://img.shields.io/npm/v/nopecha?label=NPM)
![GitHub Release](https://img.shields.io/github/v/release/NopeCHALLC/nopecha-extension?label=Extension%20Release&color=4a4)
![Chrome Web Store Version](https://img.shields.io/chrome-web-store/v/dknlfmjaanfblgfdfebhijalfmhmjjjo?label=Chrome%20Web%20Store&color=4a4)
![Mozilla Add-on Version](https://img.shields.io/amo/v/noptcha?label=Mozilla%20Add-on&color=4a4)

## Installation

To install from PyPI, run `python3 -m pip install nopecha`.

## API Usage

This package provides API wrappers for the following http packages:

- [`requests`](https://pypi.org/project/requests/) (sync)
- [`aiohttp`](https://pypi.org/project/aiohttp/) (async)
- [`httpx`](https://pypi.org/project/httpx/) (sync & async)
- [`urllib`](https://docs.python.org/3/library/urllib.html) (sync, built-in)

Note: You will need to install the http package you want to use separately
(except for `urllib`, as it's built-in but not recommended).

### Requests example

```python
from nopecha.api.requests import RequestsAPIClient

api = RequestsAPIClient("YOUR_API_KEY")
solution = api.solve_hcaptcha("b4c45857-0e23-48e6-9017-e28fff99ffb2", "https://nopecha.com/demo/hcaptcha#easy")

print("token is", solution["data"])
```

### Async HTTPX example

```python
from nopecha.api.httpx import AsyncHTTPXAPIClient

async def main():
    api = AsyncHTTPXAPIClient("YOUR_API_KEY")
    solution = await api.solve_hcaptcha("b4c45857-0e23-48e6-9017-e28fff99ffb2", "https://nopecha.com/demo/hcaptcha#easy")
    print("token is", solution["data"])

asyncio.run(main())
```

## Extension builder

This package also provides a extension builder for
[Automation builds](https://developers.nopecha.com/guides/extension_advanced/#automation-build)
which includes:

1. downloading the extension
2. updating the extension
3. updating the extension's manifest to include your settings

### Example

```python
from nopecha.extension import build_chromium

# will download the extension to the current working directory
output = build_chromium({
    "key": "YOUR_API_KEY",
})

# custom output directory
from pathlib import Path
output = build_chromium({
    "key": "YOUR_API_KEY",
}, Path("extension"))
```

You can plug the output path directly into your browser's extension manager to
load the extension:

```python
import undetected_chromedriver as uc
from nopecha.extension import build_chromium

output = build_chromium({
    "key": "YOUR_API_KEY",
})

options = uc.ChromeOptions()
options.add_argument(f"load-extension={output}")
```

## Building

To build from source, you will need to install
[`build`](https://packaging.python.org/en/latest/key_projects/#build)
(`python3 -m pip install --upgrade build `).

Then simply run `python3 -m build` to build the package.

#### Uploading to PyPI

To upload to PyPI, you will need to install
[`twine`](https://packaging.python.org/en/latest/key_projects/#twine)
(`python3 -m pip install --upgrade twine`).

Then simply run `python3 -m twine upload dist/*` to upload the package.

## Migrate from v1

If you are migrating from v1, you will need to update your code to use the new
client classes.

V1 was synchronous only, using the requests HTTP library. V2 supports both
synchronous and asynchronous code, and multiple HTTP libraries.

To migrate, you will need to:

1. Install the http library you want to use (requests, aiohttp, httpx) or use
   the built-in urllib.
2. Replace `nopecha.api_key` with creating a client instance.

```py
# Before
import nopecha

nopecha.api_key = "YOUR_API_KEY"

# Now
from nopecha.api.requests import RequestsAPIClient

client = RequestsAPIClient("YOUR_API_KEY")
```

3. Replace
   `nopecha.Token.solve()`/`nopecha.Recognition.solve()`/`nopecha.Balance.get()`
   with the appropriate method on the client instance.

```py
# Before
import nopecha
nopecha.api_key = "..."

clicks = nopecha.Recognition.solve(
    type='hcaptcha',
    task='Please click each image containing a cat-shaped cookie.',
    image_urls=[f"https://nopecha.com/image/demo/hcaptcha/{i}.png" for i in range(9)],
)
print(clicks)

token = nopecha.Token.solve(
    type='hcaptcha',
    sitekey='ab803303-ac41-41aa-9be1-7b4e01b91e2c',
    url='https://nopecha.com/demo/hcaptcha',
)
print(token)

balance = nopecha.Balance.get()
print(balance)

# Now
from nopecha.api.requests import RequestsAPIClient

client = RequestsAPIClient("YOUR_API_KEY")

clicks = client.recognize_hcaptcha(
    'Please click each image containing a cat-shaped cookie.',
    [f"https://nopecha.com/image/demo/hcaptcha/{i}.png" for i in range(9)],
)
print(clicks)

token = client.solve_hcaptcha(
    'ab803303-ac41-41aa-9be1-7b4e01b91e2c',
    'https://nopecha.com/demo/hcaptcha',
)
print(token)

balance = client.status()
print(balance)
```
