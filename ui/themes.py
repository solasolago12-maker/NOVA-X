"""Rich themes for NOVA-X.

Defines four visual themes (dark, light, neon, minimal) as Rich
: class:`Theme` instances. Each theme provides a consistent palette for
headers, sidebars, messages, accents, and status indicators.
"""

from rich.theme import Theme

THEMES: dict[str, Theme] = {
    "dark": Theme({
        "nova.header": "bold bright_white on blue",
        "nova.sidebar": "bright_cyan",
        "nova.sidebar.highlight": "bold bright_yellow",
        "nova.main": "bright_white",
        "nova.footer": "bright_black on grey11",
        "nova.user_msg": "bright_green",
        "nova.ai_msg": "bright_cyan",
        "nova.system_msg": "bright_yellow",
        "nova.accent": "bold bright_yellow",
        "nova.error": "bold bright_red",
        "nova.success": "bold bright_green",
        "nova.warning": "bold bright_yellow",
        "nova.info": "bright_blue",
        "nova.mode": "bold bright_magenta",
        "nova.border": "blue",
    }),
    "light": Theme({
        "nova.header": "bold white on steel_blue",
        "nova.sidebar": "dark_slate_gray1",
        "nova.sidebar.highlight": "bold dark_goldenrod",
        "nova.main": "black",
        "nova.footer": "dim black on white",
        "nova.user_msg": "dark_green",
        "nova.ai_msg": "steel_blue",
        "nova.system_msg": "dark_orange3",
        "nova.accent": "bold dark_goldenrod",
        "nova.error": "bold red3",
        "nova.success": "bold green4",
        "nova.warning": "bold dark_orange3",
        "nova.info": "blue",
        "nova.mode": "bold purple4",
        "nova.border": "steel_blue",
    }),
    "neon": Theme({
        "nova.header": "bold bright_white on magenta",
        "nova.sidebar": "bright_cyan",
        "nova.sidebar.highlight": "bold bright_green",
        "nova.main": "bright_white",
        "nova.footer": "bright_green on black",
        "nova.user_msg": "bright_green",
        "nova.ai_msg": "bright_magenta",
        "nova.system_msg": "bright_yellow",
        "nova.accent": "bold bright_cyan",
        "nova.error": "bold bright_red",
        "nova.success": "bold bright_green",
        "nova.warning": "bold bright_yellow",
        "nova.info": "bright_cyan",
        "nova.mode": "bold bright_magenta",
        "nova.border": "magenta",
    }),
    "minimal": Theme({
        "nova.header": "bold white on black",
        "nova.sidebar": "white",
        "nova.sidebar.highlight": "bold bright_white",
        "nova.main": "white",
        "nova.footer": "dim white on black",
        "nova.user_msg": "bright_white",
        "nova.ai_msg": "white",
        "nova.system_msg": "bright_white",
        "nova.accent": "bold bright_white",
        "nova.error": "bold bright_white",
        "nova.success": "bold bright_white",
        "nova.warning": "bold bright_white",
        "nova.info": "white",
        "nova.mode": "bold bright_white",
        "nova.border": "white",
    }),
}
