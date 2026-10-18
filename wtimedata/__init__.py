"""Non-code files shipped with wtime (declared as package_data in setup.py)."""
import os

_HERE = os.path.dirname(os.path.abspath(__file__))

def _icon(name):
    return os.path.join(_HERE, name)

ICON_PATHS = [
    _icon("wtimeicon.png"),          # 0 - default
    _icon("wtimeicon_ticket.png"),   # 1 - ticket
    _icon("wtimeicon_done.png"),     # 2 - done
    _icon("wtimeicon_error.png"),    # 3 - error
]

ICON_PATH        = ICON_PATHS[0]
ICON_PATH_TICKET = ICON_PATHS[1]
ICON_PATH_DONE   = ICON_PATHS[2]
ICON_PATH_ERROR  = ICON_PATHS[3]
