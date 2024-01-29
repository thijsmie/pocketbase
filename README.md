<a name="readme-top"></a>

[![Static Badge](https://img.shields.io/badge/status-beta-blue?style=for-the-badge&label=status)](https://github.com/thijsmie/pocketbase-async)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](https://github.com/thijsmie/pocketbase-async/blob/main/LICENSE.txt)
[![Checks status](https://img.shields.io/github/actions/workflow/status/thijsmie/pocketbase-async/checks?style=for-the-badge&label=Checks)](https://github.com/thijsmie/pocketbase-async/actions)
[![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/thijsmie/a41c81ee9f5d3944d2f9946c3eae4aae/raw/coverage.json)](https://github.com/thijsmie/pocketbase-async/actions)
[![GitHub Release](https://img.shields.io/github/v/release/thijsmie/pocketbase-async?style=for-the-badge)](https://github.com/thijsmie/pocketbase-async/releases)

<div align="center">
  <hr/>
  <a href="https://github.com/thijsmie/pocketbase-async">
    <img src="images/logo.svg" alt="Logo" width="80" height="80">
  </a>
  <h3 align="center">pocketbase-async</h3>

  <p align="center">
    An async Python 3.11+ PocketBase SDK 
    <hr/>
    <a href="https://github.com/thijsmie/pocketbase-async"><strong>Repository</strong></a>
    <br />
    <a href="https://github.com/thijsmie/pocketbase-async/issues">Report Bug</a>
    ·
    <a href="https://github.com/thijsmie/pocketbase-async/issues">Request Feature</a>
  </p>
</div>


<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#about">About</a></li>
    <li><a href="#installation">Installation</a></li></li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#attributions">Attributions</a></li>
  </ol>
</details>

## About

PocketBase is an amazing tool to have in your developers backpack for a quick backend for your project. I found it pleasant to work with in Python but Vaphes existing Python SDK is in sync code while most of my application development is async these days. I started with a fork of Vaphes' SDK and tried to add async support but I gave up quite quickly and just started from scratch. You see the results here.

## Installation

Note that this package is compatible with Python 3.11 and up. You can install this package directly from PyPi:
```bash
pip install pocketbase-async
# or if you use poetry
poetry add pocketbase-async
```

## Usage

The API is mostly the same as the official JS SDK and the Vaphes Python SDK, with some exceptions. Authentication methods are namespaced under an extra `.auth`. More info to come.

## Roadmap

See the [project board](https://github.com/thijsmie/pocketbase-async/projects?query=is%3Aopen) for the list of planned work. See the [open issues](https://github.com/thijsmie/pocketbase-async/issues) for a full list of proposed features (and known issues).

## Contributing

Contributions are welcome and appreciated, be it typo-fix, feature or extensive rework. I recommend you to open an issue if you plan to spend significant effort on making a pull request, to avoid dual work or getting your work rejected if it really doesn't fit this project.

Don't forget to give the project a star! Thanks again!

1. Fork the project
2. Create your feature branch (`git checkout -b feat/some-nice-feature`)
3. Commit your changes (`git commit -m 'feat: Add some AmazingFeature'`)
4. Push to the pranch (`git push -u origin feat/some-nice-feature`)
5. Open a pull request


## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

## Attributions

The `pocketbase-async` package was inspired and guided in implementation by several other projects:

- The official js sdk: https://github.com/pocketbase/js-sdk
- The Python SDK by Vaphes: https://github.com/vaphes/pocketbase
- The official documentation: https://pocketbase.io/docs/

Furthermore, a lot of the API tests were adapted from Vaphes' work (licensed MIT).


<hr/>
<a href="#readme-top">:arrow_up_small: Back to top</a>
