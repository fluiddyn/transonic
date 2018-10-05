__version__ = "0.0.2"

try:
    from pyfiglet import figlet_format

    __about__ = (
        figlet_format("fluidpythran", font="big") + 51 * " " + "v. " + __version__
    )
except ImportError:
    __about__ = r"""

 / _| |     (_)   | |           | | | |
| |_| |_   _ _  __| |_ __  _   _| |_| |__  _ __ __ _ _ __
|  _| | | | | |/ _` | '_ \| | | | __| '_ \| '__/ _` | '_ \
| | | | |_| | | (_| | |_) | |_| | |_| | | | | | (_| | | | |
|_| |_|\__,_|_|\__,_| .__/ \__, |\__|_| |_|_|  \__,_|_| |_|
                    | |     __/ |
                    |_|    |___/

"""
