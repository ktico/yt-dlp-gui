# yt-dlp GUI

A small Windows GUI for downloading one video at a time with [yt-dlp](https://github.com/yt-dlp/yt-dlp).

## Build the standalone executable

On Windows with Python 3.10 or later, run:

```powershell
.\build.ps1
```

The script downloads build-time dependencies, the official `yt-dlp.exe`, and FFmpeg, then creates `dist\yt-dlp-gui.exe`. The produced EXE embeds yt-dlp, FFmpeg, and FFprobe; end users only need that EXE.

## Privacy and disk access

The program accesses disk only to:

- read its bundled runtime files while starting;
- write the requested download and its temporary processing files into the folder the user selected.
- when a network connection is available, check the official yt-dlp GitHub Release and only write a newer `yt-dlp.exe` to `%LOCALAPPDATA%\yt-dlp-gui`.

It does not create a settings file, download history, cache, telemetry, or background folders. The `%LOCALAPPDATA%\yt-dlp-gui` folder exists solely for the automatic yt-dlp update required to keep extractor support current.

## Use

1. Enter one `http://` or `https://` URL.
2. Select an existing output folder.
3. Choose **Video (MP4)** or **Audio (MP3)**, then select its maximum resolution and bitrate.
4. Select **Download**.

Video downloads use the best available video and audio streams matching the selected limits, then merge them to MP4. Audio downloads are converted to MP3 at the selected bitrate with the embedded FFmpeg. On launch, the app checks the official yt-dlp release when online; it atomically replaces its locally cached engine only after the downloaded executable passes a version check. If the check or update fails, the embedded version remains in use.
