"""
Canonical system baseline provider.
Used internally by self-repair and diagnostics.
"""

from routes.system_baseline.router import get_baseline_internal


def read_system_baseline():
    """
    Returns canonical baseline snapshot of the system.
    """
    return get_baseline_internal()
