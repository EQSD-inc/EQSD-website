"""
add_head_tags.py（第3版）
Claude Design から書き出した index.html に、
ファビコン（ブラウザのタブのアイコン）の指定を書き足すスクリプト。

なぜ必要か：
  書き出した index.html は、読み込み後にページ全体（<head> を含む）を
  中に格納されたデザインのHTML（テンプレート）で丸ごと置き換える仕組みになっている。
  そのため、外側の <head> に書き足しただけでは、置き換えの時点で消えてしまい、
  Safari や iPad のブラウザでアイコンが表示されない。
  → 外側の <head> と、置き換え後に使われるテンプレートの <head> の両方に書き足す。

使い方（index.html と同じフォルダで実行）：
  python add_head_tags.py            ← index.html を書き換える
  python add_head_tags.py 別名.html  ← ファイル名を指定する場合

一緒にアップロードするファイル（index.html と同じ階層）：
  favicon.ico / favicon-32x32.png / favicon-16x16.png / apple-touch-icon.png
"""

import json
import re
import sys
from pathlib import Path

# 書き足す内容（ファイル名は index.html からの相対パス。PNG を先に書く）
TAGS = (
    '<link rel="icon" type="image/png" sizes="32x32" href="favicon-32x32.png">\n'
    '<link rel="icon" type="image/png" sizes="16x16" href="favicon-16x16.png">\n'
    '<link rel="shortcut icon" href="favicon.ico">\n'
    '<link rel="apple-touch-icon" sizes="180x180" href="apple-touch-icon.png">\n'
)
MARK = '<!-- head-tags:added -->'
NEEDED = ('favicon.ico', 'favicon-32x32.png', 'favicon-16x16.png', 'apple-touch-icon.png')

# 以前に書き足した分（目印の行と、その直後の <link> 行）を取り除くための正規表現
OLD_BLOCK = re.compile(re.escape(MARK) + r'\n(?:[ \t]*<link[^\n]*\n)*')
# 既存のアイコン指定（デザイン側に残っていた場合に取り除く）
OLD_ICON = re.compile(r'<link\s+rel="(?:icon|shortcut icon|apple-touch-icon)"[^>]*>\s*', re.I)


def add_to_outer_head(html):
    """外側の <head>（最初の </head> の直前）に書き足す"""
    html = OLD_BLOCK.sub('', html)
    pos = html.find('</head>')
    if pos == -1:
        raise ValueError('外側の </head> が見つかりません')
    return html[:pos] + MARK + '\n' + TAGS + html[pos:]


def add_to_template(html):
    """テンプレート（<script type="__bundler/template"> の中のJSON文字列）の <head> に書き足す"""
    m = re.search(r'(<script type="__bundler/template"[^>]*>)(.*?)(</script>)', html, re.S)
    if not m:
        raise ValueError('テンプレートが見つかりません（Claude Design の書き出しか確認してください）')

    template = json.loads(m.group(2))          # JSON文字列 → 普通の文字列に戻す
    template = OLD_BLOCK.sub('', template)      # 以前の書き足しを除去
    template = OLD_ICON.sub('', template)       # デザイン側のアイコン指定も除去

    head = re.search(r'<head[^>]*>', template, re.I)
    if not head:
        raise ValueError('テンプレートの <head> が見つかりません')
    i = head.end()
    template = template[:i] + '\n' + MARK + '\n' + TAGS + template[i:]

    # JSON文字列に戻す。「</」は「<\/」にしておく（<script> の途中で閉じられないようにするため）
    encoded = json.dumps(template, ensure_ascii=False).replace('</', '<\\/')
    return html[:m.start(2)] + encoded + html[m.end(2):]


def main():
    path = Path(sys.argv[1] if len(sys.argv) > 1 else 'index.html')
    if not path.exists():
        print(f'見つかりません：{path}')
        sys.exit(1)

    html = path.read_text(encoding='utf-8')
    try:
        html = add_to_outer_head(html)
        html = add_to_template(html)
    except ValueError as e:
        print(f'中止しました：{e}')
        sys.exit(1)
    path.write_text(html, encoding='utf-8')

    for name in NEEDED:
        if not (path.parent / name).exists():
            print(f'注意：{name} が同じフォルダにありません。アップロードを忘れないでください。')
    print(f'書き足しました：{path}')


if __name__ == '__main__':
    main()
