# yt-dlp GUI

A small Windows GUI for downloading one video at a time with [yt-dlp](https://github.com/yt-dlp/yt-dlp).

## Download

Download the latest platform-specific file from the repository's **Releases** tab:

- `yt-dlp-gui.exe` for Windows;
- `yt-dlp-gui-macos` for macOS.

Both are PyInstaller packages containing Python, yt-dlp, FFmpeg, and FFprobe. Python is not installed or required on the end-user computer.

### macOS: "Apple could not verify ... is free of malware"

The macOS build is not notarized by Apple (that requires a paid Apple Developer account), so Gatekeeper blocks it on first launch. To run it anyway:

1. Try double-clicking `yt-dlp-gui-macos` once; Gatekeeper will show the warning and offer only **Done** / **Move to Trash**.
2. Open **System Settings > Privacy & Security**, scroll to the **Security** section, and click **Open Anyway** next to the message about `yt-dlp-gui-macos`.
3. Confirm **Open Anyway** again in the dialog that appears, then enter your password/Touch ID if prompted.

If **Open Anyway** is not shown, remove the quarantine attribute from Terminal instead:

```sh
xattr -cr /path/to/yt-dlp-gui-macos
chmod +x /path/to/yt-dlp-gui-macos
```

Then double-click the file again to launch it.

## Build the Windows executable

On Windows with Python 3.10 or later, run:

```powershell
.\build.ps1
```

The script downloads build-time dependencies, the official `yt-dlp.exe`, and FFmpeg, then creates `dist\yt-dlp-gui.exe`. Tagged GitHub Actions builds produce the Windows and macOS release files automatically.

## Privacy and disk access

The program accesses disk only to:

- read its bundled runtime files while starting;
- write the requested download and its temporary processing files into the folder the user selected.
- when a network connection is available, check the official yt-dlp GitHub Release and only write a newer engine to the OS app-data folder: `%LOCALAPPDATA%\yt-dlp-gui` on Windows or `~/Library/Application Support/yt-dlp-gui` on macOS.

It does not create a settings file, download history, cache, telemetry, or background folders. The OS app-data update folder exists solely for the automatic yt-dlp update required to keep extractor support current.

## Use

1. Enter one `http://` or `https://` URL.
2. Select an existing output folder.
3. Choose **Video (MP4)** or **Audio (MP3)**, then select its maximum resolution and bitrate.
4. Select **Download**.

Video downloads use the best available video and audio streams matching the selected limits, then merge them to MP4. Audio downloads are converted to MP3 at the selected bitrate with the embedded FFmpeg. On launch, the app checks the official yt-dlp release when online; it atomically replaces its locally cached engine only after the downloaded executable passes a version check. If the check or update fails, the embedded version remains in use.
