"""Rich-based UI widgets for NOVA-X.

Provides reusable visual components: header panels, sidebar mode lists,
chat message bubbles, welcome and help screens, statistics panels, and
assignment overview panels.
"""

from typing import Any, Dict, List, Optional

from rich.align import Align
from rich.console import Console, ConsoleOptions, RenderResult
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.columns import Columns


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

def create_header(title: str = "NOVA-X", mode: str = "Chat", user: str = "Student") -> Panel:
    """Create the application header panel.

    Args:
        title: Application title.
        mode: Current mode name.
        user: User display name.

    Returns:
        A Rich : class:`Panel` for the header area.
    """
    header_text = Text()
    header_text.append(f"  {title}  ", style="nova.header")
    header_text.append("  |  ")
    header_text.append(f"Mode: {mode}", style="nova.mode")
    header_text.append("  |  ")
    header_text.append(f"User: {user}", style="nova.info")
    return Panel(header_text, style="nova.border", padding=(0, 1))


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

def create_sidebar(modes: List[str], current_mode: str) -> Panel:
    """Create the sidebar panel listing modes and shortcuts.

    Args:
        modes: List of available mode names.
        current_mode: The currently active mode (gets highlighted).

    Returns:
        A Rich : class:`Panel` for the sidebar.
    """
    text = Text()
    text.append("  [bold]MODES[/bold]\n", style="nova.accent")
    text.append("  " + "─" * 18 + "\n")
    for i, mode in enumerate(modes, 1):
        if mode == current_mode:
            text.append(f"  ▸ {mode.capitalize():15}\n", style="nova.sidebar.highlight")
        else:
            text.append(f"  {i}. {mode.capitalize():14}\n", style="nova.sidebar")
    text.append("\n")
    text.append("  [bold]SHORTCUTS[/bold]\n", style="nova.accent")
    text.append("  " + "─" * 18 + "\n")
    shortcuts = [
        ("/quit", "Exit"), ("/help", "Help"), ("/mode", "Switch mode"),
        ("/clear", "Clear chat"), ("/save", "Export chat"),
        ("/history", "Past sessions"), ("/subjects", "Subjects"),
        ("/stats", "Statistics"), ("/welcome", "Welcome"),
    ]
    for cmd, desc in shortcuts:
        text.append(f"  {cmd:10} ", style="nova.sidebar.highlight")
        text.append(f"{desc}\n", style="nova.sidebar")
    return Panel(text, title="Menu", style="nova.border", padding=(0, 0))


# ---------------------------------------------------------------------------
# Chat message
# ---------------------------------------------------------------------------

def create_chat_message(role: str, content: str) -> Panel:
    """Create a styled chat message panel.

    Args:
        role: ``user`` or ``assistant``.
        content: Message text content.

    Returns:
        A Rich : class:`Panel` representing the message.
    """
    if role == "user":
        prefix = "You"
        style = "nova.user_msg"
        border = "green"
    elif role == "system":
        prefix = "System"
        style = "nova.system_msg"
        border = "yellow"
    else:
        prefix = "NOVA-X"
        style = "nova.ai_msg"
        border = "cyan"
    text = Text()
    text.append(f"{prefix}: ", style=f"bold {style}")
    text.append(content, style=style)
    return Panel(text, border_style=border, padding=(0, 1))


# ---------------------------------------------------------------------------
# Welcome screen
# ---------------------------------------------------------------------------

def create_welcome_screen(user_name: str = "") -> Panel:
    """Create the welcome / quick-start screen.

    Args:
        user_name: Display name of the user (optional).

    Returns:
        A Rich : class:`Panel` with ASCII art and quick-start guide.
    """
    ascii_art = r"""
    _   _______  _____  __   _________  __
   / | / / __ \/   \ \/ /  / ____/   |/  /
  /  |/ / / / / /| |\  /  / / __/ /|_/  /
 / /|  / /_/ / ___ |/ /  / /_/ / /  /  /
/_/ |_/_____/_/  |_/_/   \____/_/  /__/

   Next-Gen Omniscient Virtual Assistant
              e X t r e m e
"""
    text = Text()
    text.append(ascii_art, style="nova.accent")
    greeting = f"Welcome, {user_name}!" if user_name else "Welcome to NOVA-X!"
    text.append(f"\n  {greeting}\n\n", style="bold nova.header")
    text.append("  Your AI-powered homework assistant is ready.\n\n", style="nova.main")
    text.append("  [bold]Quick Start:[/bold]\n", style="nova.accent")
    text.append("  • Type a message to chat with the AI\n", style="nova.main")
    text.append("  • Use /mode <name> to switch modes (math, essay, code, etc.)\n", style="nova.main")
    text.append("  • Use /help to see all available commands\n", style="nova.main")
    text.append("  • Use /quit to exit\n\n", style="nova.main")
    text.append("  [bold]Available Modes:[/bold]\n", style="nova.accent")
    modes_info = [
        ("chat", "General conversation and Q&A"),
        ("math", "Step-by-step math problem solving"),
        ("essay", "Essay planning, drafting, and feedback"),
        ("code", "Programming help and code debugging"),
        ("research", "Web research and source synthesis"),
        ("quiz", "Interactive quiz generation"),
        ("explain", "Simplified concept explanations"),
    ]
    for mode, desc in modes_info:
        text.append(f"  {mode:10} — {desc}\n", style="nova.info")
    return Panel(text, title="Welcome", style="nova.border", padding=(0, 1))


# ---------------------------------------------------------------------------
# Help screen
# ---------------------------------------------------------------------------

def create_help_screen() -> Panel:
    """Create the comprehensive help screen.

    Returns:
        A Rich : class:`Panel` listing all commands and shortcuts.
    """
    text = Text()
    text.append("  [bold underline]NOVA-X Command Reference[/bold underline]\n\n", style="nova.accent")

    text.append("  [bold]General Commands[/bold]\n", style="nova.header")
    text.append("  " + "─" * 50 + "\n")
    general = [
        ("/quit, /exit", "Exit NOVA-X"),
        ("/help", "Show this help screen"),
        ("/welcome", "Show welcome screen"),
        ("/clear", "Clear current conversation"),
        ("/save [format]", "Export chat (txt/md/docx/pdf)"),
        ("/history", "List past chat sessions"),
        ("/stats", "Show usage statistics"),
    ]
    for cmd, desc in general:
        text.append(f"  {cmd:18} {desc}\n", style="nova.main")

    text.append("\n  [bold]Mode Commands[/bold]\n", style="nova.header")
    text.append("  " + "─" * 50 + "\n")
    modes = [
        ("/mode chat", "General conversation (default)"),
        ("/mode math", "Math problem solver"),
        ("/mode essay", "Essay writing assistant"),
        ("/mode code", "Code helper and debugger"),
        ("/mode research", "Research assistant"),
        ("/mode quiz", "Quiz generator"),
        ("/mode explain", "Concept explainer"),
    ]
    for cmd, desc in modes:
        text.append(f"  {cmd:18} {desc}\n", style="nova.main")

    text.append("\n  [bold]Subject & Assignment Commands[/bold]\n", style="nova.header")
    text.append("  " + "─" * 50 + "\n")
    subject_cmds = [
        ("/subjects", "List tracked subjects"),
        ("/subjects add <name>", "Add a subject"),
        ("/subjects remove <name>", "Remove a subject"),
        ("/assignments", "List upcoming assignments"),
    ]
    for cmd, desc in subject_cmds:
        text.append(f"  {cmd:25} {desc}\n", style="nova.main")

    text.append("\n  [bold]Mode-Specific Commands[/bold]\n", style="nova.header")
    text.append("  " + "─" * 50 + "\n")
    specific = [
        ("math: check <work>", "Check your work for errors"),
        ("essay: outline <topic>", "Generate an essay outline"),
        ("essay: draft <outline>", "Expand outline into draft"),
        ("code: write <description>", "Write code from description"),
        ("code: debug <code>", "Debug provided code"),
        ("code: run <code>", "Run Python code safely"),
        ("research: search <query>", "Search the web"),
        ("research: deep <topic>", "Deep research with synthesis"),
        ("quiz: start <subject>", "Generate and start a quiz"),
        ("explain: analogy <topic>", "Explain with analogy"),
        ("explain: summarize <text>", "Summarize text"),
        ("explain: terms <topic>", "Define key terms"),
        ("/provider list", "Show supported AI providers"),
        ("/provider models", "List available models for current provider"),
        ("/provider set <provider> [model]", "Switch AI provider and optionally model"),
        ("/provider info", "Show current provider, model, and endpoint"),
        ("/provider validate", "Validate current provider host/model configuration"),
        ("/host", "Show current Ollama/OpenAI endpoint"),
        ("/status", "Show active mode, provider, model, and theme"),
    ]
    for cmd, desc in specific:
        text.append(f"  {cmd:28} {desc}\n", style="nova.main")

    return Panel(text, title="Help", style="nova.border", padding=(0, 1))


def create_status_panel(provider: str, model: str, mode: str, theme: str, user: str) -> Panel:
    """Create a status panel showing current AI and session information."""
    text = Text()
    text.append("  [bold]Command Center Status[/bold]\n\n", style="nova.accent")
    text.append(f"  User:     {user}\n", style="nova.main")
    text.append(f"  Mode:     {mode}\n", style="nova.main")
    text.append(f"  Provider: {provider}\n", style="nova.main")
    text.append(f"  Model:    {model}\n", style="nova.main")
    text.append(f"  Theme:    {theme}\n", style="nova.main")
    text.append("\n  Use /provider set <provider> [model] to switch providers.\n", style="nova.info")
    text.append("  Use /status to refresh this overview.\n", style="nova.info")
    return Panel(text, title="Control Center", style="nova.border", padding=(0, 1))


# ---------------------------------------------------------------------------
# Stats panel
# ---------------------------------------------------------------------------

def create_stats_panel(profile_stats: Dict[str, Any]) -> Panel:
    """Create a statistics display panel.

    Args:
        profile_stats: Dictionary from :meth:`UserProfile.get_stats`.

    Returns:
        A Rich : class:`Panel` with formatted statistics.
    """
    text = Text()
    text.append("  [bold]Your Learning Statistics[/bold]\n\n", style="nova.accent")
    name = profile_stats.get("name", "Student")
    grade = profile_stats.get("grade_level", "Not set")
    text.append(f"  Name:      {name}\n", style="nova.main")
    text.append(f"  Grade:     {grade}\n\n", style="nova.main")
    text.append("  [bold]Activity[/bold]\n", style="nova.header")
    text.append(f"  Sessions:       {profile_stats.get('total_sessions', 0)}\n", style="nova.main")
    text.append(f"  Total Messages: {profile_stats.get('total_messages', 0)}\n", style="nova.main")
    text.append(f"  Quizzes Taken:  {profile_stats.get('quizzes_taken', 0)}\n", style="nova.main")
    avg = profile_stats.get('quiz_average', 0.0)
    text.append(f"  Quiz Average:   {avg}%\n\n", style="nova.main")
    text.append("  [bold]Subjects[/bold]\n", style="nova.header")
    subjects = profile_stats.get("subjects", [])
    if subjects:
        for subj in subjects:
            text.append(f"  • {subj}\n", style="nova.info")
    else:
        text.append("  (No subjects tracked yet)\n", style="nova.warning")
    weak = profile_stats.get("weak_areas", [])
    if weak:
        text.append("\n  [bold]Focus Areas:[/bold] ", style="nova.warning")
        text.append(", ".join(weak), style="nova.warning")
    return Panel(text, title="Statistics", style="nova.border", padding=(0, 1))


# ---------------------------------------------------------------------------
# Assignments panel
# ---------------------------------------------------------------------------

def create_assignments_panel(assignments: List[Dict[str, Any]]) -> Panel:
    """Create an assignments overview panel.

    Args:
        assignments: List of assignment dicts with keys like ``title``,
            ``subject``, ``due_date``, ``priority``, ``status``.

    Returns:
        A Rich : class:`Panel` showing assignment details.
    """
    text = Text()
    text.append("  [bold]Your Assignments[/bold]\n\n", style="nova.accent")
    if not assignments:
        text.append("  No assignments found!\n", style="nova.success")
        text.append("  Use /subjects to add subjects and assignments.\n", style="nova.main")
    else:
        for a in assignments:
            status = a.get("status", "pending")
            priority = a.get("priority", "medium")
            title = a.get("title", "Untitled")
            subject = a.get("subject", "")
            due = a.get("due_date", "")
            style = "nova.warning" if status in ("overdue", "pending") and priority in ("high", "urgent") else "nova.main"
            text.append(f"  [{'!' if priority in ('high', 'urgent') else ' '}] ", style=style)
            text.append(f"{title}", style="bold " + style)
            if subject:
                text.append(f" ({subject})", style="nova.info")
            if due:
                text.append(f" — Due: {due}", style="nova.info")
            text.append(f" [{priority.upper()}]\n", style="nova.warning" if priority in ("high", "urgent") else "nova.info")
    return Panel(text, title="Assignments", style="nova.border", padding=(0, 1))
