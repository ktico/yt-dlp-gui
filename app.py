"""A small local GUI frontend for the official yt-dlp executable."""

from __future__ import annotations

import json
import os
import queue
import re
import ssl
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import certifi

GITHUB_LATEST_RELEASE = "https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest"
PROGRESS_PATTERN = re.compile(r"PROGRESS:([0-9]+(?:\.[0-9]+)?)%")
IS_WINDOWS = sys.platform == "win32"
YT_DLP_ASSET_NAME = "yt-dlp.exe" if IS_WINDOWS else "yt-dlp_macos"
ENGINE_FILE_NAME = "yt-dlp.exe" if IS_WINDOWS else "yt-dlp"
FFMPEG_FILE_NAME = "ffmpeg.exe" if IS_WINDOWS else "ffmpeg"

# PyInstaller's frozen Python cannot see the OS certificate store (and there
# is no "Install Certificates.command" step for a bundled app), so without an
# explicit CA bundle every HTTPS request fails with CERTIFICATE_VERIFY_FAILED.
# certifi ships a CA bundle as package data that PyInstaller bundles
# automatically, so point every request at it explicitly.
SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())


def bundle_root() -> Path:
    return Path(getattr(sys, "_MEIPASS", Path(__file__).parent))


def bundled_ffmpeg_location() -> str | None:
    bundled = bundle_root() / "ffmpeg"
    return str(bundled) if (bundled / FFMPEG_FILE_NAME).is_file() else None


def bundled_yt_dlp() -> Path:
    return bundle_root() / "yt-dlp" / ENGINE_FILE_NAME


def update_directory() -> Path:
    if IS_WINDOWS:
        local_app_data = os.environ.get("LOCALAPPDATA")
        if not local_app_data:
            raise OSError("The LOCALAPPDATA environment variable is unavailable.")
        return Path(local_app_data) / "yt-dlp-gui"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "yt-dlp-gui"
    return Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / "yt-dlp-gui"


def current_yt_dlp() -> Path:
    updated = update_directory() / ENGINE_FILE_NAME
    return updated if updated.is_file() else bundled_yt_dlp()


def executable_version(executable: Path) -> str:
    result = subprocess.run(
        [str(executable), "--version"],
        capture_output=True,
        check=True,
        text=True,
        timeout=15,
    )
    return result.stdout.strip()


def is_supported_url(value: str) -> bool:
    parsed = urlparse(value.strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


class DownloaderApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.events: queue.Queue[tuple[str, Any]] = queue.Queue()
        self.cancel_requested = threading.Event()
        self.worker: threading.Thread | None = None
        self.process: subprocess.Popen[str] | None = None

        root.title("yt-dlp GUI")
        root.minsize(640, 360)
        root.columnconfigure(1, weight=1)

        self.url = tk.StringVar()
        self.output_directory = tk.StringVar(value=str(Path.home() / "Downloads"))
        self.download_type = tk.StringVar(value="Video (MP4)")
        self.resolution = tk.StringVar(value="Best available")
        self.bitrate = tk.StringVar(value="No limit")
        self.status = tk.StringVar(value="Checking yt-dlp updates...")
        self.progress = tk.DoubleVar(value=0)

        ttk.Label(root, text="Video URL").grid(row=0, column=0, padx=12, pady=(14, 6), sticky="w")
        self.url_entry = ttk.Entry(root, textvariable=self.url)
        self.url_entry.grid(row=0, column=1, columnspan=2, padx=(0, 12), pady=(14, 6), sticky="ew")

        ttk.Label(root, text="Save to").grid(row=1, column=0, padx=12, pady=6, sticky="w")
        self.directory_entry = ttk.Entry(root, textvariable=self.output_directory)
        self.directory_entry.grid(row=1, column=1, padx=(0, 6), pady=6, sticky="ew")
        self.browse_button = ttk.Button(root, text="Browse...", command=self.choose_directory)
        self.browse_button.grid(row=1, column=2, padx=(0, 12), pady=6)

        ttk.Label(root, text="Download as").grid(row=2, column=0, padx=12, pady=6, sticky="w")
        self.type_picker = ttk.Combobox(
            root,
            textvariable=self.download_type,
            values=("Video (MP4)", "Audio (MP3)"),
            state="readonly",
            width=18,
        )
        self.type_picker.grid(row=2, column=1, padx=(0, 6), pady=6, sticky="w")
        self.type_picker.bind("<<ComboboxSelected>>", self.update_quality_options)

        self.quality_label = ttk.Label(root, text="Maximum resolution")
        self.quality_label.grid(row=3, column=0, padx=12, pady=6, sticky="w")
        self.quality_picker = ttk.Combobox(textvariable=self.resolution, state="readonly", width=18)
        self.quality_picker.grid(row=3, column=1, padx=(0, 6), pady=6, sticky="w")

        self.bitrate_label = ttk.Label(root, text="Maximum video bitrate")
        self.bitrate_label.grid(row=4, column=0, padx=12, pady=6, sticky="w")
        self.bitrate_picker = ttk.Combobox(textvariable=self.bitrate, state="readonly", width=18)
        self.bitrate_picker.grid(row=4, column=1, padx=(0, 6), pady=6, sticky="w")
        self.bitrate_suffix = ttk.Label(root, text="kbps")
        self.bitrate_suffix.grid(row=4, column=2, padx=(0, 12), pady=6, sticky="w")

        self.progress_bar = ttk.Progressbar(root, variable=self.progress, maximum=100)
        self.progress_bar.grid(row=5, column=0, columnspan=3, padx=12, pady=(14, 4), sticky="ew")
        ttk.Label(root, textvariable=self.status, anchor="w").grid(
            row=6, column=0, columnspan=3, padx=12, pady=(0, 8), sticky="ew"
        )

        self.download_button = ttk.Button(root, text="Download", command=self.start_download)
        self.download_button.grid(row=7, column=1, padx=(0, 6), pady=(0, 14), sticky="e")
        self.cancel_button = ttk.Button(root, text="Cancel", command=self.cancel_download, state="disabled")
        self.cancel_button.grid(row=7, column=2, padx=(0, 12), pady=(0, 14), sticky="w")

        self.update_quality_options()
        self.url_entry.focus_set()
        self.root.after(100, self.process_events)
        threading.Thread(target=self.update_yt_dlp, daemon=True).start()

    def update_quality_options(self, _event: Any = None) -> None:
        if self.download_type.get() == "Audio (MP3)":
            self.quality_label.configure(text="Source quality")
            self.quality_picker.configure(values=("Best available",), state="disabled")
            self.resolution.set("Best available")
            self.bitrate_label.configure(text="Audio bitrate")
            self.bitrate_picker.configure(values=("128", "192", "256", "320"), state="readonly")
            self.bitrate.set("192")
            self.bitrate_suffix.configure(text="kbps")
        else:
            self.quality_label.configure(text="Maximum resolution")
            self.quality_picker.configure(
                values=("Best available", "2160p", "1440p", "1080p", "720p", "480p", "360p"),
                state="readonly",
            )
            self.resolution.set("Best available")
            self.bitrate_label.configure(text="Maximum video bitrate")
            self.bitrate_picker.configure(
                values=("No limit", "1000", "2500", "5000", "8000", "12000", "20000"),
                state="readonly",
            )
            self.bitrate.set("No limit")
            self.bitrate_suffix.configure(text="kbps")

    def choose_directory(self) -> None:
        selected = filedialog.askdirectory(initialdir=self.output_directory.get())
        if selected:
            self.output_directory.set(selected)

    def start_download(self) -> None:
        url = self.url.get().strip()
        destination = Path(self.output_directory.get()).expanduser()

        if not is_supported_url(url):
            messagebox.showerror("Invalid URL", "Enter a valid http:// or https:// video URL.")
            return
        if not destination.is_dir():
            messagebox.showerror("Invalid folder", "Choose an existing folder for downloaded files.")
            return
        if not bundled_ffmpeg_location() or not current_yt_dlp().is_file():
            messagebox.showerror("Runtime unavailable", "Bundled yt-dlp or FFmpeg files are missing. Re-download the application.")
            return

        self.cancel_requested.clear()
        self.progress.set(0)
        self.status.set("Starting download...")
        self.set_downloading_state(True)
        self.worker = threading.Thread(target=self.download, args=(url, destination), daemon=True)
        self.worker.start()

    def cancel_download(self) -> None:
        self.cancel_requested.set()
        if self.process and self.process.poll() is None:
            self.process.terminate()
        self.status.set("Cancelling download...")
        self.cancel_button.configure(state="disabled")

    def set_downloading_state(self, downloading: bool) -> None:
        state = "disabled" if downloading else "normal"
        self.url_entry.configure(state=state)
        self.directory_entry.configure(state=state)
        self.browse_button.configure(state=state)
        self.type_picker.configure(state="disabled" if downloading else "readonly")
        self.quality_picker.configure(state="disabled" if downloading else "readonly")
        self.bitrate_picker.configure(state="disabled" if downloading else "readonly")
        self.download_button.configure(state=state)
        self.cancel_button.configure(state="normal" if downloading else "disabled")

    def download_command(self, url: str, destination: Path) -> list[str]:
        command = [
            str(current_yt_dlp()),
            "--no-playlist",
            "--no-warnings",
            "--windows-filenames",
            "--ffmpeg-location",
            bundled_ffmpeg_location() or "",
            "--output",
            str(destination / "%(title).180B [%(id)s].%(ext)s"),
            "--progress-template",
            "download:PROGRESS:%(progress._percent_str)s",
        ]
        if self.download_type.get() == "Audio (MP3)":
            command.extend(
                [
                    "--format",
                    "bestaudio/best",
                    "--extract-audio",
                    "--audio-format",
                    "mp3",
                    "--audio-quality",
                    self.bitrate.get(),
                ]
            )
        else:
            constraints = ""
            if self.resolution.get() != "Best available":
                constraints += f"[height<={self.resolution.get()[:-1]}]"
            if self.bitrate.get() != "No limit":
                constraints += f"[tbr<={self.bitrate.get()}]"
            command.extend(
                [
                    "--format",
                    f"bestvideo{constraints}+bestaudio/best{constraints}",
                    "--merge-output-format",
                    "mp4",
                ]
            )
        command.append(url)
        return command

    def download(self, url: str, destination: Path) -> None:
        errors: list[str] = []
        try:
            self.process = subprocess.Popen(
                self.download_command(url, destination),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            assert self.process.stdout
            for line in self.process.stdout:
                match = PROGRESS_PATTERN.search(line)
                if match:
                    self.events.put(("progress", float(match.group(1))))
                    self.events.put(("status", "Downloading..."))
                elif line.strip():
                    errors.append(line.strip())
            exit_code = self.process.wait()
        except OSError as error:
            self.events.put(("error", f"Could not start yt-dlp: {error}"))
        else:
            if self.cancel_requested.is_set():
                self.events.put(("cancelled", None))
            elif exit_code:
                self.events.put(("error", "\n".join(errors[-6:]) or f"yt-dlp exited with code {exit_code}."))
            else:
                self.events.put(("complete", str(destination)))
        finally:
            self.process = None

    def update_yt_dlp(self) -> None:
        try:
            bundled = bundled_yt_dlp()
            if not bundled.is_file():
                raise FileNotFoundError("The bundled yt-dlp executable is missing.")

            request = Request(
                GITHUB_LATEST_RELEASE,
                headers={
                    "Accept": "application/vnd.github+json",
                    "User-Agent": "yt-dlp-gui",
                },
            )
            with urlopen(request, timeout=5, context=SSL_CONTEXT) as response:
                release = json.load(response)
            latest_version = str(release["tag_name"])
            installed_version = executable_version(current_yt_dlp())
            if installed_version == latest_version:
                self.events.put(("update_status", f"yt-dlp {installed_version} is current."))
                return

            asset = next(asset for asset in release["assets"] if asset["name"] == YT_DLP_ASSET_NAME)
            target_directory = update_directory()
            target_directory.mkdir(parents=True, exist_ok=True)
            temporary_file = target_directory / f"{ENGINE_FILE_NAME}.download"
            target_file = target_directory / ENGINE_FILE_NAME
            download_request = Request(asset["browser_download_url"], headers={"User-Agent": "yt-dlp-gui"})
            with (
                urlopen(download_request, timeout=30, context=SSL_CONTEXT) as response,
                temporary_file.open("wb") as output,
            ):
                while chunk := response.read(1024 * 1024):
                    output.write(chunk)
            if not IS_WINDOWS:
                temporary_file.chmod(0o755)
            executable_version(temporary_file)
            temporary_file.replace(target_file)
            self.events.put(("update_status", f"yt-dlp updated to {latest_version}."))
        except (KeyError, OSError, StopIteration, subprocess.SubprocessError, TimeoutError, ValueError) as error:
            self.events.put(("update_status", f"yt-dlp update unavailable; using bundled version ({error})."))

    def process_events(self) -> None:
        try:
            while True:
                event, value = self.events.get_nowait()
                if event == "progress":
                    self.progress.set(value)
                elif event in {"status", "update_status"}:
                    self.status.set(value)
                elif event == "complete":
                    self.status.set("Download complete.")
                    self.set_downloading_state(False)
                    messagebox.showinfo("Download complete", f"Saved to:\n{value}")
                elif event == "cancelled":
                    self.status.set("Download cancelled.")
                    self.set_downloading_state(False)
                elif event == "error":
                    self.status.set("Download failed.")
                    self.set_downloading_state(False)
                    messagebox.showerror("Download failed", value)
        except queue.Empty:
            pass
        self.root.after(100, self.process_events)


def main() -> None:
    root = tk.Tk()
    DownloaderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
