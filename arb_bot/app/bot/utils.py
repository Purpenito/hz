def next_notifications_state(current_button_text: str | None) -> bool:
    """Return toggled notifications state based on button status."""
    text = current_button_text or ""
    current_enabled = "✅" in text
    return not current_enabled
