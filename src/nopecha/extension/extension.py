import typing
from shutil import rmtree
from json import dumps, loads
from pathlib import Path
from io import BytesIO
from zipfile import ZipFile

from ._adapter import request

REPO = "NopeCHALLC/nopecha-extension"

__all__ = [
    "build",
    "build_chromium",
    "build_firefox",
]


def get_latest_release() -> typing.Any:
    releases_url = f"https://api.github.com/repos/{REPO}/releases?per_page=1"
    return loads(request(releases_url))[0]


def download_release(download_url: str, outpath: Path) -> None:
    print(f"[NopeCHA] Downloading {download_url} to {outpath}")

    if outpath.exists():
        rmtree(outpath)
    outpath.mkdir(parents=True, exist_ok=True)

    content = request(download_url)
    with ZipFile(BytesIO(content)) as zip:
        zip.extractall(outpath)

    print(f"[NopeCHA] Downloaded {download_url} to {outpath}")


def build(
    branch: typing.Literal["chromium", "firefox"],
    manifest: typing.Dict[str, typing.Any],
    outpath: typing.Optional[Path] = None,
) -> str:
    if outpath is None:
        outpath = Path(f"nopecha-{branch}")

    latest_release = get_latest_release()

    for asset in latest_release["assets"]:
        if asset["name"] == f"{branch}_automation.zip":
            download_url = asset["browser_download_url"]
            break
    else:
        raise RuntimeError(f"Could not find download link for {branch}")

    if outpath.exists():
        manifest = loads((outpath / "manifest.json").read_text())
        if manifest["version_name"] != latest_release["tag_name"]:
            print(
                f"[NopeCHA] {latest_release['tag_name']} is available, you got {manifest['version_name']}"
            )
            download_release(download_url, outpath)

    else:
        print(f"[NopeCHA] Downloading {latest_release['tag_name']}")
        download_release(download_url, outpath)

    manifest = loads((outpath / "manifest.json").read_text())
    manifest["nopecha"].update(manifest)
    (outpath / "manifest.json").write_text(dumps(manifest, indent=2))

    print(f"[NopeCHA] Built {branch} extension to {outpath}")

    return str(outpath)


def build_chromium(
    manifest: typing.Dict[str, typing.Any], outpath: typing.Optional[Path] = None
) -> str:
    return build("chromium", manifest, outpath)


def build_firefox(
    manifest: typing.Dict[str, typing.Any], outpath: typing.Optional[Path] = None
) -> str:
    return build("firefox", manifest, outpath)
