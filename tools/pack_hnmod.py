"""Pack the registry's .hnmod: horizon-native.json + mixins/<id>/*.{rs,toml}.

Deterministic: sorted names, no directory entries, deflate, fixed 2026-01-01
timestamps, Unix 0644. Refuses to pack when horizon-native.json is not the
registry's schema 1 (exact 40-hex revisions), or when the id, the version or
the Horizon pin disagree between horizon-native.json, horizon-mixin.toml,
Cargo.toml and the sources. Line endings are packed as LF.

Usage: python tools/pack_hnmod.py [OUT]   (default: dist/<id>-<version>.hnmod)
"""

import json
import pathlib
import re
import sys
import tomllib
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
REVISION = re.compile(r"^[0-9a-f]{40}$")


def fail(message: str) -> None:
    sys.exit(f"pack_hnmod: {message}")


def main() -> None:
    native = json.loads((ROOT / "horizon-native.json").read_text(encoding="utf-8"))
    if set(native) != {"schema", "id", "version", "game", "horizon", "mixins"}:
        fail("horizon-native.json has other keys than the registry's schema 1")
    if native["schema"] != 1:
        fail("schema must be 1")
    for key in ("horizon", "mixins"):
        if not REVISION.match(native[key]):
            fail(f"{key} must be a 40-hex commit")
    mod_id, version = native["id"], native["version"]
    bundle = ROOT / "mixins" / mod_id
    mixin = tomllib.loads((bundle / "horizon-mixin.toml").read_text(encoding="utf-8"))
    cargo = tomllib.loads((ROOT / "Cargo.toml").read_text(encoding="utf-8"))
    runtime = (bundle / "runtime.rs").read_text(encoding="utf-8")
    adapter = (bundle / "native.rs").read_text(encoding="utf-8")
    checks = {
        "horizon-mixin.toml [mod] id": mixin["mod"]["id"] == mod_id,
        "horizon-mixin.toml [mod] version": mixin["mod"]["version"] == version,
        "horizon-mixin.toml horizon_revision":
            mixin["compatibility"]["horizon_revision"] == native["horizon"],
        "Cargo.toml version": cargo["package"]["version"] == version,
        "runtime.rs ID": f'pub const ID: &str = "{mod_id}";' in runtime,
        "runtime.rs VERSION": f'pub const VERSION: &str = "{version}";' in runtime,
        "native.rs header revision": native["horizon"] in adapter.split("\n", 1)[0],
    }
    wrong = [name for name, ok in checks.items() if not ok]
    if wrong:
        fail(f"horizon-native.json disagrees with: {', '.join(wrong)}")
    names = ["horizon-native.json"] + [
        f"mixins/{mod_id}/{p.name}"
        for p in bundle.iterdir()
        if p.is_file() and p.suffix in (".rs", ".toml")
    ]
    out = (
        pathlib.Path(sys.argv[1])
        if len(sys.argv) > 1
        else ROOT / "dist" / f"{mod_id}-{version}.hnmod"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w") as z:
        for name in sorted(names):
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            z.writestr(info, (ROOT / name).read_bytes().replace(b"\r\n", b"\n"))
    print(f"{out} ({len(names)} files)")


if __name__ == "__main__":
    main()
