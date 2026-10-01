# macOS実機検証記録（2026-10-01）

この記録は、配布された`yt-dlp-gui-macos`実行ファイルに対する実機検証の途中経過をまとめたものです。**実際のGUI起動・動画ダウンロード・再生検証は未実施**であり、このドキュメントはそれらが成功したことを示すものではありません。未確認の項目は「未実施」「未確認」として明記しています。

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
| SHA-256 | `1be6f9d76af13ef744df188a5012a3441a053d09e51a4fcf49de50b59bc1dc69` |

SHA-256とファイルサイズは、GitHub Releasesで配布されているv0.2.0のmacOSアセットと一致することを確認しました。これは配布物との同一性を示すものであり、Appleによる公証や安全性の保証を意味するものではありません。

参照:

- [v0.2.0配布ページ](https://github.com/ktico/yt-dlp-gui/releases/tag/v0.2.0)
- [v0.2.0配布メタデータ](https://api.github.com/repos/ktico/yt-dlp-gui/releases/tags/v0.2.0)
- [v0.2.0のapp.py](https://github.com/ktico/yt-dlp-gui/blob/v0.2.0/app.py)

> **注記**: 本検証時点の最新配布バージョンは[v0.2.1](https://github.com/ktico/yt-dlp-gui/releases/tag/v0.2.1)であり、ad-hoc署名の付与はv0.2.1から適用されています。上記のv0.2.0のファイルはその修正を含んでいません。

## 検証手順（計画）

1. 未署名ファイルをユーザー権限で起動してよいことを確認する。
2. 実行権限のみを付与する。

   ```sh
   chmod u+x ~/Downloads/yt-dlp-gui-macos
   ```

3. Finderから対象ファイルを起動する。
4. Gatekeeperでブロックされた場合はその表示を記録し、必要であればユーザー本人の確認・操作のもとで**対象ファイルのみ**をシステム設定の「プライバシーとセキュリティ」から「このまま開く」で許可する。隔離属性の一括削除やGatekeeper全体の無効化は標準手順にしない。
5. GUIウインドウの表示とyt-dlp更新チェック結果を記録する。
6. 検証用保存先を作成する。

   ```sh
   mkdir -p ~/Downloads/yt-dlp-gui-verification
   ```

7. GUIの`Video URL`にW3Cの公開デモ動画URLを入力する。

   ```text
   https://media.w3.org/2010/05/sintel/trailer.mp4
   ```

   出典: [W3C HTML5 Video Events and API](https://www.w3.org/2010/05/video/mediaevents.html)。このURLで確認できるのは直接URLからのダウンロード動作のみであり、YouTube等の個別サイト抽出の動作確認を兼ねるものではない。

8. `Save to`を上記保存先、`Download as`を`Video (MP4)`、解像度を`Best available`、ビットレートを`No limit`に設定し、`Download`を実行する。
9. 完了ダイアログの表示だけで判断せず、保存先の動画ファイルが存在し0 bytesでないこと、QuickTime等で再生できることを確認する。

## 検証記録（本記録作成時点では未実施）

| 確認項目 | 結果 |
| --- | --- |
| ユーザーの起動確認 | 回答待ち |
| 実行権限付与 | 未実施 |
| GUI起動 | 未実施 |
| Gatekeeperの表示・操作 | 未実施 |
| yt-dlp更新チェック | 未実施 |
| テストURL | Sintel trailer（上記）を予定 |
| GUIダウンロード完了 | 未実施 |
| 保存ファイル名・サイズ | 未確認 |
| コンテナ・動画/音声情報 | 未確認 |
| QuickTimeでの再生 | 未実施 |

この表の項目は、実機での起動・操作が完了した時点で実測値に更新する必要があります。未実施のまま「ダウンロード成功」や「検証完了」として扱わないでください。
