__version__ = "0.0.5"

try:
    from pyfiglet import figlet_format

    __about__ = figlet_format("fluidpythran", font="big")
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

__about__ = __about__.rstrip() + f"{17 * ' '} v. {__version__}\n"
