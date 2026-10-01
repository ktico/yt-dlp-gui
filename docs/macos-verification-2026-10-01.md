# macOS実機検証記録（2026-10-01）

この記録は、配布された`yt-dlp-gui-macos`実行ファイルに対する実機検証結果をまとめたものです。**ユーザー本人が確認した項目**と、**Codex（computer use）が実測した項目**を区別して記載しています。確認できていない項目は「未確認」「未実施」と明記し、成功したとは記載していません。

## 検証対象と環境

| 項目 | 実測値 |
| --- | --- |
| OS | macOS 26.5.2 / Build 25F84 |
| CPU | arm64（Apple Silicon） |
| 検証対象ファイル | `~/Downloads/yt-dlp-gui-macos` |
| ファイル形式 | Mach-O 64-bit executable arm64 |
| サイズ | 75,198,640 bytes |
| 初期権限 | `-rw-r--r--`（実行権限なし） |
| コード署名 | ad-hoc / TeamIdentifierなし |
| 隔離属性 | `com.apple.quarantine`あり |
| 配布バージョン | v0.2.0 |
| SHA-256（権限変更前後で一致） | `1be6f9d76af13ef744df188a5012a3441a053d09e51a4fcf49de50b59bc1dc69` |

SHA-256とファイルサイズは、GitHub Releasesで配布されているv0.2.0のmacOSアセットと一致することを確認しました。これは配布物との同一性を示すものであり、Appleによる公証や安全性の保証を意味するものではありません。

参照:

- [v0.2.0配布ページ](https://github.com/ktico/yt-dlp-gui/releases/tag/v0.2.0)
- [v0.2.0配布メタデータ](https://api.github.com/repos/ktico/yt-dlp-gui/releases/tags/v0.2.0)
- [v0.2.0のapp.py](https://github.com/ktico/yt-dlp-gui/blob/v0.2.0/app.py)

> **注記**: 検証対象はv0.2.0のバイナリでした。v0.2.1でad-hoc署名を追加済みで、本記録で判明したSSL証明書エラーはv0.3.0で修正しています（下記「判明した不具合と対応」を参照）。

## 実施した手順

1. ユーザーが未署名ファイルの起動に同意。
2. 実行権限を付与。

   ```sh
   chmod u+x ~/Downloads/yt-dlp-gui-macos
   ```

   結果: 成功。権限は`-rwxr--r--`に変化。

3. Finderから対象ファイルを起動。
4. GUIの`Video URL`にW3Cの公開デモ動画URLを使用（CLI補助検証）。

   ```text
   https://media.w3.org/2010/05/sintel/trailer.mp4
   ```

   出典: [W3C HTML5 Video Events and API](https://www.w3.org/2010/05/video/mediaevents.html)。このURLで確認できるのは直接URLからのダウンロード動作のみであり、YouTube等の個別サイト抽出の動作確認を兼ねるものではない。

## 検証記録

| 確認項目 | 結果 |
| --- | --- |
| ユーザーの起動確認 | 了承済み |
| 実行権限付与 | 成功。`chmod u+x`後は`-rwxr--r--` |
| Finderから指定ファイルを起動 | 成功（Codexが起動プロセスを確認） |
| GUIの表示 | **ユーザー確認**：GUIが表示されていると回答 |
| GUIのDownloadボタンの動作 | **ユーザー確認**：「ダウンロードボタンも機能していた」と回答。ただし使用したURL・設定・保存ファイルの詳細は申告なし |
| computer useによるGUI直接操作（入力・Downloadクリック） | **未実施**。`getApp`が`Invalid app`／`timeoutReached`で失敗し、Codexから直接操作できなかった |
| Gatekeeperの表示・操作 | Codexでは警告表示を確認していない。隔離属性の削除・保護設定の変更は実施していない |
| アプリ起動時のyt-dlp自動更新チェック結果 | GUIへ接続できず未確認。ただし下記のとおりSSL証明書エラーが発生することを別途スクリーンショットで確認（「判明した不具合と対応」参照） |
| 同梱yt-dlpバージョン | `2026.08.19`（同梱実行ファイルの`--version`で確認） |
| CLI補助検証のテストURL | `https://media.w3.org/2010/05/sintel/trailer.mp4` |
| 同梱エンジン（yt-dlp + FFmpeg）によるCLIダウンロード | **Codex実測**：成功。終了コード0、ログに`PROGRESS:100.0%` |
| GUIのダウンロード完了ダイアログ | 未確認（CLI補助検証では非該当） |
| CLI補助検証の保存先・サイズ | `~/Downloads/yt-dlp-gui-verification/trailer [trailer].mp4`、4,372,373 bytes |
| コンテナ・動画情報 | MP4、H.264、854×480、24 fps（ffprobeで確認） |
| 音声トラック | AACあり（ffprobeで確認）。実際の聴音は未確認 |
| 再生時間 | 52.209秒（ffprobe）、QuickTimeでは00:52 |
| QuickTimeでの再生 | **Codex実測**：再生状態on、タイムラインが0から約18.5秒へ進行、映像をスクリーンショットで確認。その後00:52で再生終了をAXで確認 |

### GUI接続（computer use）の制約

単体のMach-Oファイルはcomputer useの`getApp`で認識されず、`.app`ラッパー経由でも操作対象の取得がタイムアウトした。このため、GUIのDownloadボタンの直接操作はCodexによる実測ではなく、ユーザー本人の確認によるものである。この接続の制約は、アプリやDownloadボタン自体の不具合とは判断していない。

### 同梱エンジンによる補助検証（CLI）

起動した指定バイナリが展開したPyInstallerランタイム内の`yt-dlp/yt-dlp`と`ffmpeg/ffprobe`を使用し、Homebrewやシステムの別エンジンでは代用していない。実行時の一時展開先はアプリ終了後に消えるため、恒久的な利用手順ではない。

```sh
runtime_dir='<PyInstallerのonefile展開先>'
"$runtime_dir/yt-dlp/yt-dlp" \
  --no-playlist --no-warnings --windows-filenames \
  --ffmpeg-location "$runtime_dir/ffmpeg" \
  --output '~/Downloads/yt-dlp-gui-verification/%(title).180B [%(id)s].%(ext)s' \
  --progress-template 'download:PROGRESS:%(progress._percent_str)s' \
  --format 'bestvideo+bestaudio/best' --merge-output-format mp4 \
  https://media.w3.org/2010/05/sintel/trailer.mp4
```

この直接MP4は映像・音声を含むため、別ストリームの結合やMP3変換の検証を兼ねるものではない。YouTube等のサイト抽出動作も未検証。

## 判明した不具合と対応

実機検証とは別に、ユーザーが実際にGUIを起動した際のスクリーンショットで、ステータス行に以下のエラーが表示されることを確認しました。

```text
yt-dlp update unavailable; using bundled version
(<urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed:
unable to get local issuer certificate (_ssl.c:1010)>).
```

**原因**: PyInstallerでバンドルされたPython実行ファイルは、macOSのシステム証明書ストア（Keychain）にアクセスできません。`app.py`の`update_yt_dlp()`が明示的なCA証明書バンドルを指定せず`urlopen()`を呼んでいたため、GitHub APIへのHTTPS接続のTLS証明書検証に失敗していました。

**挙動への影響**: このエラーが出ても、同梱されたyt-dlpエンジンでのダウンロード自体は正常に動作します（上記のCLI補助検証でも実証済み）。影響は「起動時の最新版自動チェックができない」点のみです。

**修正内容**（本検証を踏まえてv0.3.0で対応）:

- `requirements.txt`に`certifi`を追加。
- `app.py`で`ssl.create_default_context(cafile=certifi.where())`によるSSLコンテキストを作成し、yt-dlpの更新チェック・ダウンロードで使う2箇所の`urlopen()`呼び出しに明示的に渡すよう変更。
- PyInstallerの`pyinstaller-hooks-contrib`に含まれる`hook-certifi.py`により、`certifi`のCA証明書バンドル（`cacert.pem`）はビルド時に自動同梱されることを確認。
- ローカルでPyInstallerビルドした検証用バイナリで、修正後は実際にGitHub APIへのHTTPS接続がステータス200で成功することを確認済み。

## 元バイナリへの変更範囲

検証中に`~/Downloads/yt-dlp-gui-macos`へ行った変更は実行権限の付与のみ。内容・ソース・隔離属性は変更しておらず、検証前後でSHA-256が一致することを確認済み。

## 追記（v0.3.1）: 配布形式を`.app`バンドルに変更

本検証はv0.2.0の「生のUnix実行ファイル」（`yt-dlp-gui-macos`）を対象に実施したものですが、この形式はFinderでの実行権限ロストやUTF-8誤認エラーの原因でもありました。Codexによる動作確認用の`.app`ラップ版（`yt-dlp Verification.app`）が問題なく動作することが確認できたため、v0.3.1よりリリース形式を標準的なmacOS `.app`バンドル（`yt-dlp-gui-macos.app.zip`として配布）に変更しました。ビルドは`PyInstaller --onedir --windowed`で生成される`.app`をad-hoc署名し、`ditto`でzip化しています。ローカルビルドで署名検証・起動を確認済みです。
