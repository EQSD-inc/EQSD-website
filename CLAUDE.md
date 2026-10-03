# EQSD-website（本番リポジトリ）

株式会社EQSD 公式ウェブサイト（https://eqsd.jp）の**本番**リポジトリ。
ここへの push は、そのまま公開サイトに反映される。

## このリポジトリの役割

- 置いてよいのは、**プレビュー用リポジトリ（`eqsd-inc/eqsd-HP-preview`）で確認が済んだファイルだけ**。
- プレビューで確認していない変更を、直接このリポジトリに加えない。
- `index.html` とアイコンのファイルは、プレビュー用リポジトリと**同一のもの**にする。
- push は、利用者の明示的な指示があった場合だけ行う。

## このリポジトリの構成

- `index.html` … Claude Design から書き出したファイルを、そのまま置く
- `favicon.ico` / `favicon-16x16.png` / `favicon-32x32.png` / `apple-touch-icon.png` … アイコン
- `tools/add_head_tags.py` … アイコンの指定を index.html に書き足すスクリプト
- `.github/workflows/deploy.yml` … push のたびに、上のスクリプトを実行して GitHub Pages に公開する自動処理

## 守ること

1. **作業の前に必ず `git pull` する。** GitHub 側にしかないファイル（特に `CNAME`）を、手元の古い状態で上書き・削除しないため。
2. **`index.html` は Claude Design の書き出しをそのまま置く。** デザインの定数（WORKS / SLIDES / NEWS / PAPERS / COMPANY / PROFILE など）や本文を、ここで手作業で編集しない。修正は Claude Design で行う。
3. **`tools/add_head_tags.py` は手元で実行しない。** アイコンの書き足しは、push 後に自動処理（deploy.yml）が行う。リポジトリの index.html は書き出したままの状態で保管する。
4. **`tools/` と `.github/workflows/` のファイル名・位置を変えない。** 自動処理がこの場所を前提にしている。
5. **公開リポジトリなので、非公開の情報を入れない。** 許可のメール、社内のメモ、個人情報、パスワード、APIキーなどは置かない。`.gitignore` に含まれないファイルを新しく追加するときは、公開してよいものか確認する。
6. **`CNAME` を削除・変更しない。**（カスタムドメインの設定が入っている場合）
7. **コミットメッセージは日本語で、何を変えたかを1行で書く。**（例：「スマホのスライド下の段の折り返しを修正」）

## push 後の確認

- GitHub の「Actions」で、Deploy site が成功（緑のチェック）したことを確認する。失敗した場合は、エラーの内容を報告して作業を止める。
