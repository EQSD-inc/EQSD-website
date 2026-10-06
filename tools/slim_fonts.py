"""
slim_fonts.py
Claude Design から書き出した index.html から、埋め込まれたフォント（約5.6MB）を取り除き、
代わりに Google Fonts から読み込む指定を入れるスクリプト。

なぜ必要か：
  書き出した index.html には、日本語フォントなど135個のフォントファイルが丸ごと埋め込まれていて、
  ページを開くたびに全部をダウンロード・展開（Unpacking）している。
  スマホでは表示まで20秒以上かかることがある。
  Google Fonts から読み込むようにすると、必要な文字の分だけが配信され、表示が大幅に速くなる。

使い方：
  python slim_fonts.py index.html
  （GitHub の自動公開の中で、add_head_tags.py の前に自動で実行される）

安全のための動き：
  ・想定と違う形のファイルだった場合は、何も変更せずに終了する（公開は止めない）
  ・すでに処理済みのファイルに実行しても、何も変わらない
"""

import json
import re
import sys
from pathlib import Path

# 使っているフォントと太さ（書き出しファイルの @font-face から確認した組み合わせ）
GOOGLE_FONTS = (
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
    'family=Barlow:wght@400;700&family=Geist:wght@400;500;600&family=Noto+Sans+JP:wght@400;500'
    '&display=swap">\n'
)
MARK = '<!-- fonts:google -->'


def main():
    path = Path(sys.argv[1] if len(sys.argv) > 1 else 'index.html')
    html = path.read_text(encoding='utf-8')

    # --- 埋め込みデータの一覧（manifest）と、ページの本体（template）を探す ---
    mm = re.search(r'(<script type="__bundler/manifest"[^>]*>)(.*?)(</script>)', html, re.S)
    tm = re.search(r'(<script type="__bundler/template"[^>]*>)(.*?)(</script>)', html, re.S)
    if not mm or not tm:
        print('想定と違う形のファイルなので、フォントの処理は行いませんでした。')
        return

    template = json.loads(tm.group(2))
    if MARK in template:
        print('すでに処理済みです。')
        return

    # --- ① 埋め込みデータの一覧から、フォントだけを取り除く ---
    manifest = json.loads(mm.group(2))
    font_ids = {k for k, v in manifest.items() if str(v.get('mime', '')).startswith('font/')}
    if not font_ids:
        print('埋め込みフォントがないので、処理は不要でした。')
        return
    manifest = {k: v for k, v in manifest.items() if k not in font_ids}

    # --- ② ページの本体から、取り除いたフォントを指す @font-face を消す ---
    def drop_face(m):
        block = m.group(0)
        return '' if any(fid in block for fid in font_ids) else block
    template = re.sub(r'(/\*[^*]*\*/\s*)?@font-face\s*{[^}]*}\s*', drop_face, template)

    # --- ③ ページの本体の <head> に、Google Fonts の読み込みを入れる ---
    head = re.search(r'<head[^>]*>', template, re.I)
    if not head:
        print('<head> が見つからないので、フォントの処理は行いませんでした。')
        return
    template = template[:head.end()] + '\n' + MARK + '\n' + GOOGLE_FONTS + template[head.end():]

    # --- 書き戻す（「</」は「<\/」にして、<script> の途中で閉じられないようにする） ---
    new_manifest = json.dumps(manifest, separators=(',', ':')).replace('</', '<\\/')
    new_template = json.dumps(template, ensure_ascii=False).replace('</', '<\\/')
    # 後ろの方（template）から先に置き換えると、前の位置がずれない
    starts = sorted([(mm.start(2), mm.end(2), new_manifest), (tm.start(2), tm.end(2), new_template)], reverse=True)
    for s, e, text in starts:
        html = html[:s] + text + html[e:]

    path.write_text(html, encoding='utf-8')
    print(f'埋め込みフォント {len(font_ids)} 個を取り除き、Google Fonts に切り替えました。')


if __name__ == '__main__':
    main()
