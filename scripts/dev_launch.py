"""Launch FlatCAM in developer mode: traces on stderr, without patching sources."""

import faulthandler
import os
import runpy
import sys
import threading
import time
import traceback

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "source")
ENTRY = os.path.join(SRC, "flatcam.py")
TRACE_PATH = os.path.join(ROOT, "tmp", "last_trace.txt")


def _write_trace(text: str) -> None:
    print(text, file=sys.stderr, flush=True)
    os.makedirs(os.path.dirname(TRACE_PATH), exist_ok=True)
    with open(TRACE_PATH, "w", encoding="utf-8") as fh:
        fh.write(text)


def dump_exception(exc_type, exc_value, exc_tb) -> None:
    _write_trace("".join(traceback.format_exception(exc_type, exc_value, exc_tb)))


def wrap_excepthook() -> None:
    current = sys.excepthook
    if getattr(current, "_flatcam_dev_wrap", False):
        return

    def wrapped(exc_type, exc_value, exc_tb):
        dump_exception(exc_type, exc_value, exc_tb)
        if current not in (wrapped, sys.__excepthook__):
            return current(exc_type, exc_value, exc_tb)
        return sys.__excepthook__(exc_type, exc_value, exc_tb)

    wrapped._flatcam_dev_wrap = True
    sys.excepthook = wrapped


def wrap_thread_hook() -> None:
    current = threading.excepthook
    if getattr(current, "_flatcam_dev_wrap", False):
        return

    def wrapped(args):
        dump_exception(args.exc_type, args.exc_value, args.exc_traceback)
        if current is not wrapped:
            return current(args)
        return threading.__excepthook__(args)

    wrapped._flatcam_dev_wrap = True
    threading.excepthook = wrapped


def keep_handlers() -> None:
    """Qt/VisPy may overwrite signal handlers; restore faulthandler."""
    while True:
        if not faulthandler.is_enabled():
            faulthandler.enable(all_threads=True)
        wrap_excepthook()
        wrap_thread_hook()
        time.sleep(0.5)


def main() -> None:
    if not os.path.isfile(ENTRY):
        raise SystemExit(f"entry point not found: {ENTRY}")

    faulthandler.enable(all_threads=True)
    wrap_excepthook()
    wrap_thread_hook()
    threading.Thread(target=keep_handlers, daemon=True).start()

    print(
        f"[dev] traces go to stderr and {TRACE_PATH}",
        file=sys.stderr,
        flush=True,
    )

    os.chdir(SRC)
    sys.path.insert(0, SRC)
    sys.argv = [ENTRY, *sys.argv[1:]]
    runpy.run_path(ENTRY, run_name="__main__")


if __name__ == "__main__":
    main()
