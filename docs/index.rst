Welcome to GuardianLayer's documentation!
========================================

GuardianLayer
-------------
GuardianLayer is a meta-cognition layer for AI agents designed to detect and prevent infinite or unwanted looping behaviour when interacting with external tools and services.

Quick links
-----------
- :doc:`index`
- :ref:`installation`
- :ref:`quickstart`
- :ref:`api-reference`
- :ref:`contributing`

Installation
------------
.. _installation:

Install from PyPI:

.. code-block:: console

   pip install GuardianLayer

Or install from source (development):

.. code-block:: console

   git clone https://github.com/your-org/GuardianLayer.git
   cd GuardianLayer
   pip install -e '.[dev]'

Quick start
-----------
.. _quickstart:

A minimal example to get started:

.. code-block:: python

   from GuardianLayer import LoopDetector
   detector = LoopDetector()
   result = detector.check({"tool": "search", "query": "test"})
   if result[0]:  # loop detected
       print("Loop detected:", result[1])

For more complete examples, see the `examples/` directory in the repository:
- examples/demo.py
- examples/demo_v2.py
- examples/demo_cache_perf.py

Usage and concepts
------------------
GuardianLayer provides several cooperating components:

- GuardianLayer (high-level orchestration)
- LoopDetector (core loop detection algorithm)
- ExperienceLayer (stores past interactions / successful corrections)
- MCPFacade (tool input/output validation)
- HealthMonitor (circuit breaker / error classification)
- AdviceGenerator (generates suggestions to recover from failure)
- Cache implementations (LRUCache, AdviceCache, ValidationCache, HashCache)
- MetricsCollector (collects runtime metrics)

API reference
-------------
.. _api-reference:

This documentation uses Sphinx `autodoc` to extract docstrings from the package. Below are the most relevant modules and classes for quick reference. Use the links to jump to generated API docs (if `autosummary` is configured it will generate separate pages).

Core package
~~~~~~~~~~~~
.. automodule:: GuardianLayer
   :members:
   :undoc-members:
   :show-inheritance:

Loop detection
~~~~~~~~~~~~~~
.. automodule:: GuardianLayer.LoopDetector
   :members:
   :undoc-members:
   :show-inheritance:

Guardian & orchestration
~~~~~~~~~~~~~~~~~~~~~~~~
.. automodule:: GuardianLayer.guardian
   :members:
   :undoc-members:
   :show-inheritance:

Experience & storage
~~~~~~~~~~~~~~~~~~~~
.. automodule:: GuardianLayer.experience_layer
   :members:
   :undoc-members:

Validation / MCP
~~~~~~~~~~~~~~~~
.. automodule:: GuardianLayer.mcp_facade
   :members:
   :undoc-members:

Health monitoring
~~~~~~~~~~~~~~~~~
.. automodule:: GuardianLayer.health_monitor
   :members:
   :undoc-members:

Advice generation
~~~~~~~~~~~~~~~~~
.. automodule:: GuardianLayer.advice_generator
   :members:
   :undoc-members:

Caching & providers
~~~~~~~~~~~~~~~~~~~
.. automodule:: GuardianLayer.cache
   :members:
   :undoc-members:

.. automodule:: GuardianLayer.providers
   :members:
   :undoc-members:

Metrics & utilities
~~~~~~~~~~~~~~~~~~~
.. automodule:: GuardianLayer.metrics
   :members:
   :undoc-members:

Examples and testing
--------------------
See the `examples/` and `tests/` directories for real usage patterns and test coverage. Running the test suite:

.. code-block:: console

   pytest -q

Contributing
------------
.. _contributing:

We welcome contributions! Please follow these guidelines:

- Create an issue to discuss major changes before implementing them.
- Fork the repository and open a pull request with a clear title and description.
- Add tests for any new functionality.
- Ensure linters and tests pass locally (see `pyproject.toml` and `.github/workflows/ci.yml`).

License
-------
GuardianLayer is licensed under the MIT License. See the `LICENSE` file for details.

Changelog
---------
See `CHANGELOG.md` for a history of notable changes and releases.

Building the docs locally
-------------------------
1. Install requirements: `pip install -r docs/requirements.txt` or at least `sphinx` and `sphinx-rtd-theme`.
2. From the `docs/` directory run:

.. code-block:: console

   sphinx-build -b html . _build/html

The generated HTML will be available in `docs/_build/html`.

If you want `autosummary`-generated API pages, run `sphinx-apidoc` or ensure `sphinx.ext.autosummary` is enabled and `autosummary_generate = True` in `conf.py`.
