from app.bot.utils import next_notifications_state


def test_next_notifications_state_toggles_from_enabled_to_disabled():
    assert next_notifications_state("Уведомления ✅") is False


def test_next_notifications_state_toggles_from_disabled_to_enabled():
    assert next_notifications_state("Уведомления ❌") is True


def test_next_notifications_state_defaults_to_enable_on_unknown_text():
    assert next_notifications_state("Уведомления") is True
