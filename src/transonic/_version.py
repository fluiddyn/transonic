__version__ = "0.5.3"

try:
    from pyfiglet import figlet_format

    __about__ = figlet_format("transonic", font="big")
except ImportError:
    __about__ = r"""
 _                                   _
| |                                 (_)
| |_ _ __ __ _ _ __  ___  ___  _ __  _  ___
| __| '__/ _` | '_ \/ __|/ _ \| '_ \| |/ __|
| |_| | | (_| | | | \__ \ (_) | | | | | (__
 \__|_|  \__,_|_| |_|___/\___/|_| |_|_|\___|

"""

__about__ = __about__.rstrip() + f"{17 * ' '} v. {__version__}\n"
