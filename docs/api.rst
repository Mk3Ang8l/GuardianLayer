API Reference
=============

This document is the API reference entry point for the GuardianLayer package.
It is intended to be processed by Sphinx with the `autodoc` and `autosummary`
extensions enabled. Use this file as a lightweight index that pulls in the
most important modules and classes via `automodule` directives.

Notes
-----
- If you want fully generated module files, run `sphinx-apidoc -o . ../src` from
  the `docs/` folder or enable `autosummary_generate = True` in `conf.py`.
- This file provides a compact overview; for deeper details, view the
  generated pages or the source code under `src/`.

Core package
------------
.. automodule:: GuardianLayer
   :members:
   :undoc-members:
   :show-inheritance:

Loop detection
--------------
.. automodule:: GuardianLayer.LoopDetector
   :members:
   :undoc-members:
   :show-inheritance:

Guardian orchestration
----------------------
.. automodule:: GuardianLayer.guardian
   :members:
   :undoc-members:
   :show-inheritance:

Experience & storage
--------------------
.. automodule:: GuardianLayer.experience_layer
   :members:
   :undoc-members:

Validation & MCP
----------------
.. automodule:: GuardianLayer.mcp_facade
   :members:
   :undoc-members:

Advice generation
-----------------
.. automodule:: GuardianLayer.advice_generator
   :members:
   :undoc-members:

Health monitoring
-----------------
.. automodule:: GuardianLayer.health_monitor
   :members:
   :undoc-members:

Caching & providers
-------------------
.. automodule:: GuardianLayer.cache
   :members:
   :undoc-members:

.. automodule:: GuardianLayer.providers
   :members:
   :undoc-members:

Interfaces & utilities
----------------------
.. automodule:: GuardianLayer.interfaces
   :members:
   :undoc-members:

.. automodule:: GuardianLayer.metrics
   :members:
   :undoc-members:

.. automodule:: GuardianLayer.logging_config
   :members:
   :undoc-members:

Additional modules
------------------
If your project grows, add modules below or generate module stubs using
`sphinx-apidoc` so that each module can get its own standalone page.

Quick tips
----------
- To include private members in the docs, remove or adjust `:undoc-members:`
  and modify `autodoc_mock_imports` in `conf.py` if necessary.
- Consider enabling `autosummary` to create summary pages and reduce manual
  maintenance of this index.
