"""Display progress on the console
==================================

Relies on the rich package if it is installed. If not, fall back to simple
logging messages.

"""
try:
    from transonic.log import logger
    import rich
except ImportError:
    logger.debug("Install rich for tracking progress.")

    def track(sequence, *args, **kwargs):
        return sequence

    class Progress:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self) -> "Progress":
            return self

        def __exit__(self, *exc):
            return False

        def add_task(self, description, *args, **kwargs):
            logger.info(description)

        def remove_task(self, *args, **kwargs):
            pass

        def update(self, *args, **kwargs):
            pass


else:
    logger.debug("Using rich for tracking progress.")
    from rich.progress import track, Progress


progress = Progress()
