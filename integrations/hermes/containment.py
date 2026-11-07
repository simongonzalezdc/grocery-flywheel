"""Bounded strict JSON and descriptor-relative POSIX profile storage."""
from __future__ import annotations

import contextlib
import errno
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import uuid

STATE_LIMIT = 60000
ARG_LIMIT = 65536
RESULT_LIMIT = 262144
HTML_LIMIT = 2097152
NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}\.json\Z", re.ASCII)


class BoundaryError(Exception):
    def __init__(self, code="INVALID_INPUT"):
        self.code = code
        super().__init__(code)


def require(condition, code="INVALID_INPUT"):
    if not condition:
        raise BoundaryError(code)


def size(text, limit):
    require(isinstance(text, str))
    try:
        value = text.encode("utf-8")
    except UnicodeError:
        raise BoundaryError() from None
    require(len(value) <= limit, "LIMIT_EXCEEDED")
    return value


def strict_json(text, limit=STATE_LIMIT):
    size(text, limit)

    def pairs(rows):
        result = {}
        for key, value in rows:
            require(key not in result)
            result[key] = value
        return result

    def constant(_):
        raise BoundaryError()

    try:
        value = json.loads(text, object_pairs_hook=pairs, parse_constant=constant)
    except (ValueError, RecursionError):
        raise BoundaryError() from None
    require(isinstance(value, dict))
    stack = [(value, 0)]
    nodes = 0
    while stack:
        obj, depth = stack.pop()
        nodes += 1
        require(depth <= 32 and nodes <= 10000, "LIMIT_EXCEEDED")
        if isinstance(obj, str):
            size(obj, 8192)
        elif isinstance(obj, dict):
            stack.extend((x, depth + 1) for pair in obj.items() for x in pair)
        elif isinstance(obj, list):
            require(len(obj) <= 500, "LIMIT_EXCEEDED")
            stack.extend((x, depth + 1) for x in obj)
        elif isinstance(obj, float):
            import math
            require(math.isfinite(obj))
    return value


def _directory(parent, name, create=False, private=False):
    if create:
        try:
            os.mkdir(name, 0o700, dir_fd=parent)
        except FileExistsError:
            pass
    fd = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
    if private:
        info = os.fstat(fd)
        if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o700:
            os.close(fd)
            raise BoundaryError("UNSAFE_PATH")
    return fd


@contextlib.contextmanager
def data_directory(kind):
    # Resolve the public profile home each time, then implement the documented
    # plugin_data_dir layout through anchored descriptors. plugin_data_dir itself
    # uses path.mkdir (follows symlinks), so must not be invoked on untrusted storage.
    from hermes_constants import get_hermes_home
    require(os.name == "posix" and hasattr(os, "O_NOFOLLOW"), "UNSAFE_PATH")
    home = Path(os.path.abspath(get_hermes_home()))
    fds = [os.open("/", os.O_RDONLY | os.O_DIRECTORY)]
    try:
        for part in home.parts[1:]:
            fds.append(_directory(fds[-1], part))
        for part in ("plugin-data", "grocery-flywheel", kind):
            fds.append(_directory(fds[-1], part, create=True, private=True))
        yield fds[-1]
    finally:
        for fd in reversed(fds):
            os.close(fd)


def read_state(name):
    require(isinstance(name, str) and NAME.fullmatch(name) is not None, "UNSAFE_PATH")
    with data_directory("state") as directory:
        try:
            fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
        except FileNotFoundError:
            raise BoundaryError("STATE_NOT_FOUND") from None
        try:
            info = os.fstat(fd)
            require(stat.S_ISREG(info.st_mode), "UNSAFE_PATH")
            require(info.st_size <= STATE_LIMIT, "LIMIT_EXCEEDED")
            raw = os.read(fd, STATE_LIMIT + 1)
            require(len(raw) <= STATE_LIMIT, "LIMIT_EXCEEDED")
            try:
                return raw.decode("utf-8")
            except UnicodeError:
                raise BoundaryError() from None
        finally:
            os.close(fd)


def write_dashboard(html):
    raw = size(html, HTML_LIMIT)
    with data_directory("dashboards") as directory:
        # flock on the anchored directory avoids a persistent lock-file/symlink surface.
        try:
            fcntl.flock(directory, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise BoundaryError("BUSY") from None
        name = "dashboard-" + uuid.uuid4().hex + ".html"
        temporary = "." + name + ".tmp"
        published = False
        fd = None
        try:
            fd = os.open(temporary, os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=directory)
            with os.fdopen(fd, "w+b", closefd=False) as stream:
                stream.write(raw)
                stream.flush()
                os.fsync(fd)
                stream.seek(0)
                require(stream.read() == raw, "IO_ERROR")
            os.link(temporary, name, src_dir_fd=directory, dst_dir_fd=directory, follow_symlinks=False)
            published = True
            check = os.open(name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=directory)
            try:
                require(os.read(check, HTML_LIMIT + 1) == raw, "IO_ERROR")
            finally:
                os.close(check)
            return {"artifact": "dashboards/" + name, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
        except BaseException:
            if published:
                os.unlink(name, dir_fd=directory)
            raise
        finally:
            if fd is not None:
                os.close(fd)
                os.unlink(temporary, dir_fd=directory)
            fcntl.flock(directory, fcntl.LOCK_UN)


def io_error(exc):
    return "UNSAFE_PATH" if exc.errno in (errno.ELOOP, errno.ENOTDIR) else "IO_ERROR"
