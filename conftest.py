# Disable web3 pytest plugin to avoid import errors
import sys
from unittest.mock import MagicMock

# Block the web3.tools module from being imported by pytest
# This must happen before pytest tries to load the plugin
sys.modules['web3.tools'] = MagicMock()
sys.modules['web3.tools.pytest_ethereum'] = MagicMock()
sys.modules['web3.tools.pytest_ethereum.deployer'] = MagicMock()
