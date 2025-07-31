"""Configure warnings to be ignored.

This module configures warnings to be ignored.

functions:
    setup_warnings: Configure warnings to be ignored.

"""

import warnings


def setup_warnings() -> None:
    """Configure warnings to be ignored."""
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.filterwarnings("ignore", category=FutureWarning)
    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", category=PendingDeprecationWarning)
