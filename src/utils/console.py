# Standard Library imports
import sys


class Progress:
    """
    A single console line that updates in place, e.g. "  Reading metadata... 120/980".
    """

    def __init__(self, label: str):
        self.label = label
        self._last_shown = -1

    def __call__(self, done: int, total: int) -> None:
        # Output redirected to a file or pipe: only print the final count.
        if not sys.stdout.isatty() and done != total:
            return
        # Redraw at most ~100 times per stage to keep slow consoles fast.
        step = max(1, total // 100)
        if done != total and done - self._last_shown < step:
            return
        self._last_shown = done
        sys.stdout.write(f"\r  {self.label}... {done}/{total}")
        if done == total:
            sys.stdout.write("\n")
        sys.stdout.flush()


def confirm(question: str) -> bool:
    """Ask a yes/no question; anything but y/yes counts as no."""
    try:
        answer = input(f"{question} [y/N] ")
    except EOFError:
        return False
    return answer.strip().lower() in ("y", "yes")
