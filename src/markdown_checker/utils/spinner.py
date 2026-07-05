import itertools
import sys
import threading
from typing import Any
from typing import TextIO


class Spinner:
    """A simple text spinner shown on a stream while a long-running task runs.

    Use via the :func:`spinner` factory / context manager rather than
    constructing directly. The spinner runs on a background thread and only
    animates when the target stream is a TTY (or ``force=True``); otherwise
    :meth:`start` is a no-op so redirected output (e.g. in CI logs) stays clean.
    """

    spinner_cycle = itertools.cycle(["-", "/", "|", "\\"])

    def __init__(
        self, beep: bool = False, disable: bool = False, force: bool = False, stream: TextIO | Any = sys.stdout
    ):
        """
        Args:
            beep: Write a bell character (``\\7``) to ``stream`` when the
                spinner stops.
            disable: Disable the spinner entirely; :meth:`start` becomes a no-op.
            force: Animate even when ``stream`` is not a TTY (e.g. redirected
                to a file).
            stream: The stream to write the spinner animation to.
        """
        self.disable = disable
        self.beep = beep
        self.force = force
        self.stream = stream
        self.stop_running: threading.Event | None = None
        self.spin_thread: threading.Thread | None = None

    def start(self) -> None:
        """Start animating on a background thread, unless disabled or non-TTY (see :attr:`force`)."""
        if self.disable:
            return
        if self.stream.isatty() or self.force:
            self.stop_running = threading.Event()
            self.spin_thread = threading.Thread(target=self.init_spin)
            self.spin_thread.start()

    def stop(self) -> None:
        """Signal the background thread to stop and wait for it to finish."""
        if self.spin_thread and self.stop_running:
            self.stop_running.set()
            self.spin_thread.join()

    def init_spin(self) -> None:
        """Background-thread target: write ``"Checking... "`` then animate until :meth:`stop` is called."""
        self.stream.write("Checking... ")
        if self.stop_running:
            while not self.stop_running.is_set():
                self.stream.write(next(self.spinner_cycle))
                self.stream.flush()
                self.stop_running.wait(0.25)
                self.stream.write("\b")
                self.stream.flush()

    def __enter__(self) -> "Spinner":
        """Start the spinner; see :meth:`start`."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):  # type: ignore[no-untyped-def]
        """Stop the spinner and, if :attr:`beep` is set, write a bell character."""
        if self.disable:
            return False
        self.stop()
        if self.beep:
            self.stream.write("\7")
            self.stream.flush()
        return False


def spinner(
    beep: bool = False, disable: bool = False, force: bool = False, stream: TextIO | Any = sys.stdout
) -> Spinner:
    """This function creates a context manager that is used to display a
    spinner on stdout as long as the context has not exited.

    The spinner is created only if stdout is not redirected, or if the spinner
    is forced using the `force` parameter.

    Args:
        beep (bool):
            Beep when spinner finishes.
        disable (bool):
            Hide spinner.
        force (bool):
            Force creation of spinner even when stdout is redirected.

    Example
    -------

        with spinner():
            do_something()
            do_something_else()

    """
    return Spinner(beep, disable, force, stream)
