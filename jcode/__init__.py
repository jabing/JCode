#MY|"""
#JP|JCode v3.0 - OMO Governance Extension Layer
#HW|
#XT|A code governance system for OpenCode with 6-agent workflow
#KZ|and 4-level switch mechanism.
#MX|"""
#HN|
__version__ = "3.0.0"
from core.switch_manager import SwitchManager, create_switch_manager
#JT|
#PZ|# Import commonly used modules
#NH|from core.switch_manager import SwitchManager, create_switch_manager
#BQ|
__all__ = [
    #__version__
    "__version__",
    "SwitchManager",
    "create_switch_manager",
]
