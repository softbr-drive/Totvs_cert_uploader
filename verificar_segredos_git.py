"""Verifica arquivos e valores sensíveis no índice do Git antes do commit."""

import re
import subprocess
from pathlib import PurePath

from secrets_manager import load_secrets


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args])


def main() -> int:
    secrets = [
        value.encode("utf-8")
        for key, value in load_secrets().items()
        if value and (key.endswith("_PASSWORD") or key == "GAS_WEBHOOK_URL")
    ]
    paths = git("diff", "--cached", "--name-only", "-z", "--diff-filter=ACMRT")
    blocked = 0
    for raw_path in filter(None, paths.split(b"\0")):
        path = raw_path.decode("utf-8", errors="surrogateescape")
        file = PurePath(path)
        name = file.name.lower()
        if (
            name in {".env", "_secrets.py", "secrets.json", "config.json"}
            or name.startswith(".env.") and name != ".env.example"
            or file.suffix.lower() in {".pfx", ".p12", ".pem", ".key", ".cer", ".crt"}
        ):
            blocked += 1
            continue
        content = git("show", f":{path}")
        if any(secret in content for secret in secrets) or re.search(
            rb"-----BEGIN (?:[A-Z0-9]+ )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}",
            content,
        ):
            blocked += 1

    if blocked:
        print(f"Commit bloqueado. {blocked} arquivo(s) preparado(s) contêm dados sensíveis.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
