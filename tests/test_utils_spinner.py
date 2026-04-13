import io

from markdown_checker.utils.spinner import Spinner, spinner


def test_spinner_factory_returns_spinner():
    """The spinner() factory function returns a Spinner instance."""
    s = spinner(disable=True)
    assert isinstance(s, Spinner)


def test_spinner_context_manager():
    """Spinner works as a context manager."""
    with spinner(disable=True) as s:
        assert isinstance(s, Spinner)


def test_spinner_disabled_does_not_start_thread():
    """Disabled spinner does not create a background thread."""
    s = Spinner(disable=True)
    s.start()
    assert s.spin_thread is None
    s.stop()


def test_spinner_force_writes_to_stream():
    """Force-enabled spinner writes to the provided stream."""
    stream = io.StringIO()
    s = Spinner(force=True, stream=stream)
    s.start()
    s.stop()
    output = stream.getvalue()
    assert "Checking..." in output


def test_spinner_stop_without_start():
    """Calling stop without start does not raise."""
    s = Spinner(disable=True)
    s.stop()


def test_spinner_exit_returns_false():
    """__exit__ returns False so exceptions propagate."""
    s = Spinner(disable=True)
    result = s.__exit__(None, None, None)
    assert result is False


def test_spinner_beep_on_exit():
    """Beep option writes bell character on exit."""
    stream = io.StringIO()
    s = Spinner(beep=True, force=True, stream=stream)
    s.start()
    s.stop()
    s.__exit__(None, None, None)
    assert "\7" in stream.getvalue()


def test_spinner_no_tty_no_force_no_thread():
    """Spinner does not start thread when stream is not a TTY and force is False."""
    stream = io.StringIO()
    s = Spinner(force=False, stream=stream)
    s.start()
    assert s.spin_thread is None


def test_spinner_default_params():
    """Default Spinner parameters are correct."""
    s = Spinner()
    assert s.disable is False
    assert s.beep is False
    assert s.force is False
