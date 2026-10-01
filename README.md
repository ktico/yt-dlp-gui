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

---

# yt-dlp GUI（日本語）

[yt-dlp](https://github.com/yt-dlp/yt-dlp) を使って一度に1本の動画をダウンロードできる、小さなWindows向けGUIです。

## ダウンロード

リポジトリの **Releases** タブから、お使いのプラットフォーム向けの最新ファイルをダウンロードしてください。

- Windows用: `yt-dlp-gui.exe`
- macOS用: `yt-dlp-gui-macos`

どちらもPython、yt-dlp、FFmpeg、FFprobeを含むPyInstallerパッケージです。利用者のパソコンにPythonをインストールする必要はありません。

### macOS:「"yt-dlp-gui-macos"にMacに損害を与えたり、プライバシーを侵害する可能性のあるマルウェアが含まれていないことを確認できませんでした」

このmacOS版はApple公証（有料のApple Developerアカウントが必要）を受けていないため、初回起動時にGatekeeperがブロックします。実行するには以下の手順を行ってください。

1. 一度`yt-dlp-gui-macos`をダブルクリックします。Gatekeeperの警告が表示され、**OK**（または**ゴミ箱に入れる**）のみが選べる状態になります。
2. **システム設定 > プライバシーとセキュリティ** を開き、**セキュリティ**欄までスクロールして、`yt-dlp-gui-macos`に関するメッセージの横にある **このまま開く** をクリックします。
3. 表示されるダイアログで再度 **このまま開く** を選択し、必要に応じてパスワードまたはTouch IDを入力します。

**このまま開く**が表示されない場合は、ターミナルから隔離属性（quarantine）を削除してください。

```sh
xattr -cr /path/to/yt-dlp-gui-macos
chmod +x /path/to/yt-dlp-gui-macos
```

その後、再度ファイルをダブルクリックして起動します。

## Windows用実行ファイルのビルド

Python 3.10以降がインストールされたWindows環境で、以下を実行します。

```powershell
.\build.ps1
```

このスクリプトはビルド時の依存関係、公式の`yt-dlp.exe`、FFmpegをダウンロードし、`dist\yt-dlp-gui.exe`を生成します。タグ付きのGitHub Actionsビルドでは、Windows版とmacOS版のリリースファイルが自動的に生成されます。

## プライバシーとディスクアクセス

このプログラムがディスクにアクセスするのは、以下の場合のみです。

- 起動時に同梱されたランタイムファイルを読み込む。
- 利用者が選択したフォルダに、要求されたダウンロードファイルとその一時処理ファイルを書き込む。
- ネットワーク接続が利用可能な場合、公式yt-dlpのGitHub Releaseを確認し、より新しいエンジンがある場合のみOSのアプリデータフォルダ（Windowsでは`%LOCALAPPDATA%\yt-dlp-gui`、macOSでは`~/Library/Application Support/yt-dlp-gui`）に書き込む。

設定ファイル、ダウンロード履歴、キャッシュ、テレメトリ、バックグラウンドフォルダなどは一切作成しません。OSのアプリデータ更新フォルダは、エクストラクタの互換性を維持するために必要な自動yt-dlp更新専用です。

## 使い方

1. `http://`または`https://`で始まるURLを1つ入力します。
2. 既存の出力先フォルダを選択します。
3. **Video (MP4)** または **Audio (MP3)** を選び、最大解像度とビットレートを設定します。
4. **Download** を選択します。

動画ダウンロードでは、選択した制限に合う最良の映像・音声ストリームを使用し、MP4に結合します。音声ダウンロードは、内蔵FFmpegを使って選択したビットレートのMP3に変換されます。起動時にオンラインであれば公式yt-dlpリリースを確認し、ダウンロードした実行ファイルがバージョンチェックに合格した場合のみ、ローカルにキャッシュされたエンジンをアトミックに置き換えます。確認または更新に失敗した場合は、同梱版がそのまま使用されます。
