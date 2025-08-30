# Rest API client for Ghostfolio

Unofficial REST API for [Ghostfolio](https://ghostfol.io/).

Supports documented and undocumented APIs

## Installation

```bash
pip install ghostfolio
```

## Usage

```python
from ghostfolio import Ghostfolio

client = Ghostfolio(token="your_token")

```

Or if you want to connect to your self-hosted Ghostfolio instance:

```python
from ghostfolio import Ghostfolio

client = Ghostfolio(token="your_token", host="https://your-ghostfolio-instance.com")
```

## Generate Documentation

```shell
pdoc --html --output-dir docs ghostfolio --force
```
