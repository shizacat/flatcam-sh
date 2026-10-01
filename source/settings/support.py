"""Default factories shared by saved settings and session options."""

import gettext
import os

_ = gettext.gettext


def _default_worker_number() -> int:
    """
    Return the worker count derived from the available CPUs.

    :return: worker count
    """
    return min(4, max(2, int(os.cpu_count() / 2))) if os.cpu_count() else 2


def _default_process_number() -> int:
    """
    Return the process count derived from the available CPUs.

    :return: process count
    """
    return int(os.cpu_count() / 4) if os.cpu_count() > 4 else 1
