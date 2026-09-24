"""
Build a portable Image Sorter drive folder.

Downloads portable Python runtimes, ExifTool and GeoNames location data, and lays out:

    <out>/
        Start-ImageSorter.bat           Windows launcher
        Start-ImageSorter.command       macOS launcher
        start-image-sorter.sh           Linux launcher (also used by the macOS one)
        HOW-TO-USE.txt
        Unsorted/  Sorted/  Duplicates/
        app/
            image-sorter/               this program
            python/<platform>/          portable Python per OS
            exiftool/windows/           exiftool.exe (Windows)
            exiftool/perl/              exiftool Perl script (macOS/Linux)
            geodata/                    cities.tsv, countries.tsv
            lib/                        tzdata (timezone database for Windows)

Copy <out> to the root of an exFAT-formatted drive, or pass the drive as --out.
Rebuilding onto an existing drive replaces the program files only; Unsorted, Sorted,
Duplicates, app/state and app/logs are left alone.

Uses only the Python standard library:
    python scripts/build_drive.py
    python scripts/build_drive.py --out E:\\ --platforms windows-x64,macos-arm64
"""

# Standard Library imports
import argparse
import io
import json
import os
import shutil
import sys
import tarfile
import urllib.request
import zipfile
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parents[1]

PYTHON_PLATFORMS = {
    "windows-x64": "x86_64-pc-windows-msvc",
    "macos-arm64": "aarch64-apple-darwin",
    "macos-x64": "x86_64-apple-darwin",
    "linux-x64": "x86_64-unknown-linux-gnu",
    "linux-arm64": "aarch64-unknown-linux-gnu",
}
DEFAULT_PYTHON_VERSION = "3.12"
PYTHON_RELEASES_API = "https://api.github.com/repos/astral-sh/python-build-standalone/releases"

EXIFTOOL_VERSION_URL = "https://exiftool.org/ver.txt"
EXIFTOOL_PERL_URL = "https://sourceforge.net/projects/exiftool/files/Image-ExifTool-{version}.tar.gz/download"
EXIFTOOL_WINDOWS_URL = "https://sourceforge.net/projects/exiftool/files/exiftool-{version}_64.zip/download"

GEONAMES_CITIES_URL = "https://download.geonames.org/export/dump/cities{size}.zip"
GEONAMES_COUNTRIES_URL = "https://download.geonames.org/export/dump/countryInfo.txt"
# Neighbourhoods and historical/abandoned/destroyed places make poor folder names.
EXCLUDED_FEATURE_CODES = {"PPLX", "PPLH", "PPLQ", "PPLW", "PPLCH"}

TZDATA_PYPI_URL = "https://pypi.org/pypi/tzdata/json"

USER_AGENT = "image-sorter-build/1.0"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a portable Image Sorter drive folder.")
    parser.add_argument("--out", default=str(REPO_DIR / "dist" / "ImageSorter"),
                        help="Output folder or drive root (default: dist/ImageSorter).")
    parser.add_argument("--cache", default=str(REPO_DIR / "dist" / ".cache"),
                        help="Download cache folder (default: dist/.cache).")
    parser.add_argument("--platforms", default=",".join(PYTHON_PLATFORMS),
                        help=f"Comma-separated Python platforms to bundle, from: {', '.join(PYTHON_PLATFORMS)}.")
    parser.add_argument("--no-python", action="store_true",
                        help="Do not bundle Python (the launchers then use Python installed on the computer).")
    parser.add_argument("--python-version", default=DEFAULT_PYTHON_VERSION,
                        help=f"Python minor version to bundle (default: {DEFAULT_PYTHON_VERSION}).")
    parser.add_argument("--python-release", default="latest",
                        help="python-build-standalone release tag, e.g. 20260901 (default: latest).")
    parser.add_argument("--cities", default="1000", choices=["500", "1000", "5000", "15000"],
                        help="GeoNames city list: places with at least this many inhabitants (default: 1000).")
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Downloads
# ---------------------------------------------------------------------------

def fetch_bytes(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


def download(url: str, cache_dir: Path, filename: str) -> Path:
    """Download url into the cache (once) and return the cached file."""
    target = cache_dir / filename
    if target.is_file() and target.stat().st_size > 0:
        print(f"  cached    {filename}")
        return target

    print(f"  download  {filename}")
    cache_dir.mkdir(parents=True, exist_ok=True)
    partial = target.with_suffix(target.suffix + ".part")
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=120) as response, open(partial, "wb") as file_handle:
        shutil.copyfileobj(response, file_handle, length=1024 * 1024)
    partial.replace(target)
    return target


def check_archive(path: Path, kind: str) -> None:
    """Fail clearly if a mirror returned an HTML page instead of the archive."""
    with open(path, "rb") as file_handle:
        magic = file_handle.read(4)
    expected = {"zip": b"PK\x03\x04", "gzip": b"\x1f\x8b"}[kind]
    if not magic.startswith(expected):
        path.unlink()
        raise SystemExit(f"Downloaded {path.name} is not a {kind} file. Try again later.")


# ---------------------------------------------------------------------------
# Build steps
# ---------------------------------------------------------------------------

def copy_program(app_dir: Path) -> None:
    print("Program")
    target = app_dir / "image-sorter"
    replace_dir(target)
    shutil.copy2(REPO_DIR / "main.py", target / "main.py")
    for name in ("README.md", "LICENSE"):
        if (REPO_DIR / name).is_file():
            shutil.copy2(REPO_DIR / name, target / name)
    shutil.copytree(
        REPO_DIR / "src",
        target / "src",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    print(f"  copied    {target}")


def write_launchers(out_dir: Path) -> None:
    print("Launchers")
    launchers = REPO_DIR / "launchers"
    for name, newline in (
        ("Start-ImageSorter.bat", "\r\n"),
        ("Start-ImageSorter.command", "\n"),
        ("start-image-sorter.sh", "\n"),
        ("HOW-TO-USE.txt", "\r\n"),
    ):
        text = (launchers / name).read_text(encoding="utf-8").replace("\r\n", "\n")
        target = out_dir / name
        with open(target, "w", encoding="utf-8", newline=newline) as file_handle:
            file_handle.write(text)
        if name.endswith((".sh", ".command")):
            target.chmod(0o755)
        print(f"  wrote     {name}")


def build_geodata(app_dir: Path, cache_dir: Path, cities_size: str) -> None:
    print("Location data (GeoNames)")
    cities_zip = download(GEONAMES_CITIES_URL.format(size=cities_size), cache_dir, f"cities{cities_size}.zip")
    check_archive(cities_zip, "zip")
    countries_txt = download(GEONAMES_COUNTRIES_URL, cache_dir, "countryInfo.txt")

    target = app_dir / "geodata"
    replace_dir(target)

    city_count = 0
    with zipfile.ZipFile(cities_zip) as archive, open(
        target / "cities.tsv", "w", encoding="utf-8", newline="\n"
    ) as out:
        with archive.open(f"cities{cities_size}.txt") as source:
            for raw_line in io.TextIOWrapper(source, encoding="utf-8"):
                columns = raw_line.rstrip("\n").split("\t")
                if len(columns) < 18 or columns[7] in EXCLUDED_FEATURE_CODES:
                    continue
                name, latitude, longitude = columns[1], columns[4], columns[5]
                country_code, population, timezone_name = columns[8], columns[14] or "0", columns[17]
                out.write(f"{name}\t{country_code}\t{latitude}\t{longitude}\t{timezone_name}\t{population}\n")
                city_count += 1

    with open(countries_txt, encoding="utf-8") as source, open(
        target / "countries.tsv", "w", encoding="utf-8", newline="\n"
    ) as out:
        for line in source:
            if line.startswith("#") or not line.strip():
                continue
            columns = line.rstrip("\r\n").split("\t")
            out.write(f"{columns[0]}\t{columns[4]}\n")

    (target / "ATTRIBUTION.txt").write_text(
        "Location data from GeoNames (https://www.geonames.org), licensed under CC BY 4.0.\n",
        encoding="utf-8",
    )
    print(f"  wrote     {city_count} cities")


def build_exiftool(app_dir: Path, cache_dir: Path, platforms: list[str]) -> None:
    print("ExifTool")
    version = fetch_bytes(EXIFTOOL_VERSION_URL).decode().strip()
    print(f"  version   {version}")

    target = app_dir / "exiftool"
    replace_dir(target)

    if not platforms or any(not p.startswith("windows") for p in platforms):
        # Perl version: used on macOS/Linux, which ship with Perl.
        archive_path = download(EXIFTOOL_PERL_URL.format(version=version), cache_dir, f"Image-ExifTool-{version}.tar.gz")
        check_archive(archive_path, "gzip")
        prefix = f"Image-ExifTool-{version}/"
        perl_dir = target / "perl"
        with tarfile.open(archive_path) as archive:
            for member in archive.getmembers():
                if not member.isfile() or not member.name.startswith(prefix):
                    continue
                relative = member.name[len(prefix):]
                if relative == "exiftool" or relative.startswith("lib/"):
                    write_member(archive, member, perl_dir / relative)
        (perl_dir / "exiftool").chmod(0o755)
        print(f"  unpacked  {perl_dir}")

    if not platforms or any(p.startswith("windows") for p in platforms):
        archive_path = download(EXIFTOOL_WINDOWS_URL.format(version=version), cache_dir, f"exiftool-{version}_64.zip")
        check_archive(archive_path, "zip")
        windows_dir = target / "windows"
        with zipfile.ZipFile(archive_path) as archive:
            for info in archive.infolist():
                if info.is_dir():
                    continue
                # Drop the top folder ("exiftool-13.59_64/") and the "(-k)" pause-on-exit suffix.
                relative = info.filename.split("/", 1)[1] if "/" in info.filename else info.filename
                if relative == "exiftool(-k).exe":
                    relative = "exiftool.exe"
                destination = safe_join(windows_dir, relative)
                destination.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(info) as source, open(destination, "wb") as out:
                    shutil.copyfileobj(source, out)
        print(f"  unpacked  {windows_dir}")


def build_python(app_dir: Path, cache_dir: Path, platforms: list[str], version: str, release: str) -> None:
    print(f"Python {version}")
    api_url = f"{PYTHON_RELEASES_API}/latest" if release == "latest" else f"{PYTHON_RELEASES_API}/tags/{release}"
    release_info = json.loads(fetch_bytes(api_url))
    print(f"  release   {release_info['tag_name']}")
    assets = {asset["name"]: asset["browser_download_url"] for asset in release_info["assets"]}

    for platform in platforms:
        triple = PYTHON_PLATFORMS[platform]
        asset_name = find_python_asset(assets, version, triple)
        archive_path = download(assets[asset_name], cache_dir, asset_name)
        check_archive(archive_path, "gzip")

        target = app_dir / "python" / platform
        replace_dir(target)
        extract_python(archive_path, target)
        trim_python(target, platform, version)
        print(f"  unpacked  {target}")


def find_python_asset(assets: dict[str, str], version: str, triple: str) -> str:
    # Prefer the smaller "stripped" build (no debug symbols).
    for suffix in ("install_only_stripped.tar.gz", "install_only.tar.gz"):
        for name in assets:
            if name.startswith(f"cpython-{version}.") and f"-{triple}-{suffix}" in name:
                return name
    raise SystemExit(f"No Python {version} build for {triple} in this release. Try --python-release.")


def extract_python(archive_path: Path, target: Path) -> None:
    """
    Extract a python-build-standalone archive (top folder "python/") into target.
    Symlinks and hard links become real copies, because exFAT drives have no links.
    """
    links: list[tuple[Path, Path]] = []
    with tarfile.open(archive_path) as archive:
        for member in archive.getmembers():
            if not member.name.startswith("python/"):
                continue
            relative = member.name[len("python/"):]
            if not relative:
                continue
            destination = safe_join(target, relative)
            if member.isdir():
                destination.mkdir(parents=True, exist_ok=True)
            elif member.issym():
                links.append((destination, safe_join(target, str(Path(relative).parent / member.linkname))))
            elif member.islnk():
                links.append((destination, safe_join(target, member.linkname[len("python/"):])))
            elif member.isfile():
                write_member(archive, member, destination)

    # Resolve links after all regular files exist; repeat for links pointing at links.
    pending = links
    while pending:
        remaining = []
        for destination, source in pending:
            if source.is_file():
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
            elif source.is_dir():
                shutil.copytree(source, destination, dirs_exist_ok=True)
            else:
                remaining.append((destination, source))
        if len(remaining) == len(pending):
            for destination, source in remaining:
                print(f"  warning   could not resolve link {destination.name} -> {source}")
            break
        pending = remaining


def trim_python(target: Path, platform: str, version: str) -> None:
    """
    Remove parts of the runtime the sorter never uses (GUI toolkit, test suite, pip,
    C headers, duplicate executables) to keep the drive small.
    """
    if platform.startswith("windows"):
        stdlib = target / "Lib"
        removable = [
            target / "tcl", target / "include", target / "libs", target / "Scripts",
            *(target / "DLLs" / name for name in ("tcl86t.dll", "tk86t.dll", "_tkinter.pyd")),
        ]
    else:
        stdlib = target / "lib" / f"python{version}"
        removable = [
            target / "include", target / "share", target / "lib" / "pkgconfig",
            *(path for path in (target / "bin").iterdir() if path.name != "python3"),
            *(target / "lib").glob("tcl*"), *(target / "lib").glob("tk*"),
            *(target / "lib").glob("itcl*"), *(target / "lib").glob("thread*"),
            *(target / "lib").glob("libtcl*"), *(target / "lib").glob("libtk*"),
            *stdlib.glob("config-*"),
            *(stdlib / "lib-dynload").glob("_tkinter*"),
        ]
        if platform.startswith("linux"):
            # The Linux interpreter is statically linked; the shared library is unused.
            removable += list((target / "lib").glob("libpython*"))

    removable += [
        stdlib / name
        for name in ("test", "idlelib", "tkinter", "turtledemo", "ensurepip", "lib2to3")
    ]
    removable += list((stdlib / "site-packages").glob("*"))

    for path in removable:
        if path.is_dir():
            shutil.rmtree(path)
        elif path.exists():
            path.unlink()


def install_tzdata(app_dir: Path, cache_dir: Path) -> None:
    """
    zoneinfo needs a timezone database; macOS/Linux have one, Windows does not.
    The pure-Python tzdata package fills the gap and works on every OS.
    """
    print("Timezone data (tzdata)")
    info = json.loads(fetch_bytes(TZDATA_PYPI_URL))
    wheel = next(item for item in info["urls"] if item["packagetype"] == "bdist_wheel")
    wheel_path = download(wheel["url"], cache_dir, wheel["filename"])
    check_archive(wheel_path, "zip")

    target = app_dir / "lib"
    replace_dir(target)
    with zipfile.ZipFile(wheel_path) as archive:
        for info_item in archive.infolist():
            if info_item.filename.startswith("tzdata/") and not info_item.is_dir():
                destination = safe_join(target, info_item.filename)
                destination.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(info_item) as source, open(destination, "wb") as out:
                    shutil.copyfileobj(source, out)
    print(f"  unpacked  {target / 'tzdata'}")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def replace_dir(path: Path) -> None:
    """Empty a generated folder so stale files from an older build do not linger."""
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)


def safe_join(base: Path, relative: str) -> Path:
    """Join an archive member path to base, refusing paths that escape it."""
    destination = (base / relative).resolve()
    if not destination.is_relative_to(base.resolve()):
        raise SystemExit(f"Refusing unsafe archive path: {relative}")
    return destination


def write_member(archive: tarfile.TarFile, member: tarfile.TarInfo, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    source = archive.extractfile(member)
    if source is None:
        return
    with source, open(destination, "wb") as out:
        shutil.copyfileobj(source, out)
    if member.mode & 0o111 and os.name != "nt":
        destination.chmod(0o755)


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out).resolve()
    cache_dir = Path(args.cache).resolve()
    platforms = [] if args.no_python else [p.strip() for p in args.platforms.split(",") if p.strip()]

    unknown = [p for p in platforms if p not in PYTHON_PLATFORMS]
    if unknown:
        print(f"Unknown platform(s): {', '.join(unknown)}. Choose from: {', '.join(PYTHON_PLATFORMS)}")
        return 2

    print(f"Building Image Sorter drive in {out_dir}\n")
    app_dir = out_dir / "app"
    for folder in ("Unsorted", "Sorted", "Duplicates"):
        (out_dir / folder).mkdir(parents=True, exist_ok=True)
    app_dir.mkdir(parents=True, exist_ok=True)

    copy_program(app_dir)
    write_launchers(out_dir)
    build_geodata(app_dir, cache_dir, args.cities)
    build_exiftool(app_dir, cache_dir, platforms)
    install_tzdata(app_dir, cache_dir)
    if platforms:
        build_python(app_dir, cache_dir, platforms, args.python_version, args.python_release)

    print(f"\nDone. Copy the contents of {out_dir} to the root of your drive.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
