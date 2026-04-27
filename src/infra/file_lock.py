"""Lock simples de arquivo para proteger filas JSON locais.

MantÃ©m o projeto sem dependÃªncias externas e reduz risco de duas execuÃ§Ãµes
sobrescreverem `mcp_status.json` ou `mcp_outbox.json` ao mesmo tempo.
"""
from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def exclusive_file_lock(target: Path):
    lock_path = target.with_suffix(target.suffix + ".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+b") as lock_file:
        lock_file.seek(0)
        if os.name == "nt":
            import msvcrt

            lock_file.write(b"\0")
            lock_file.flush()
            lock_file.seek(0)
            msvcrt.locking(lock_file.fileno(), msvcrt.LK_LOCK, 1)
            try:
                yield
            finally:
                lock_file.seek(0)
                msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


