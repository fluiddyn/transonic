"""Display progress on the console
==================================

Relies on the rich package if it is installed. If not, fall back to simple
logging messages.

"""
from transonic.log import logger


try:
    import rich
except ImportError:

    def track(sequence, *args, **kwargs):
        return sequence

    def _add_task(description, *args, **kwargs):
        logger.info(description)

    def Progress(*args, **kwargs):
        """Mock all methods of the Progress class except add_task."""
        from unittest.mock import MagicMock

        return MagicMock(name="Progress", add_task=_add_task)

    logger.debug("Install rich for tracking progress.")
else:
    logger.debug("Using rich for tracking progress.")
    from rich.progress import track, Progress
