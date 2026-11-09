#!/usr/bin/env python3
"""检查 C2 紧凑报告格式。只用 Python 3.6+ 标准库。
用法: python3 check_compact.py 报告.txt [--allow-ip]"""
import io
import re
import sys
import unicodedata

MAX_COLS = 100
MAX_LINES = 60
MAX_KEY_FIELDS = 10
MAX_SHOW = 15
SECRET = re.compile(
    r'(?i)(?<![a-z])(pass|password|passwd|pwd|secret|token|api[_-]?key|access[_-]?key)\s*[=:]\s*(?!NA\b)\S'
    r'|-----BEGIN [A-Z ]*PRIVATE KEY-----|AKIA[0-9A-Z]{16}|://[^/\s:@]+:[^@\s]+@'
    r'|requirepass\s+\S|Bearer\s+\S{8,}|--pass(word)?[ =]\S'
    r'|(口令|密码|密钥|令牌|私钥)\s*[=:：]\s*(?!NA\b)\S')
TABLE = re.compile(r'^\s*\|.*\|\s*$|\|\s*:?-{3,}\s*\||\+-{3,}\+|[\u2500-\u259f]|^```')
IP = re.compile(r'(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])')
EMPTY = re.compile(r'=\s*(?:;|\||$)|=-(?!\d)')
BAD_NA = ('', '-', '--', '\u2014', '无', 'n/a', 'null', 'none', '/', '?')
HEAD = re.compile(r'^FMT=C2 \| RPT=\S+ \| TZ=[+-]\d{2}(:?\d{2})? \| 日期=\d{4}-\d{2}-\d{2} \| 作者=\S+$')


def cols(s):
    return sum(2 if unicodedata.east_asian_width(c) in 'WFA' else 1 for c in s)


def check(lines, allow_ip=False):
    errs = []

    def add(n, msg):
        errs.append('第%d行: %s' % (n, msg))

    if not lines:
        return ['文件为空']
    if len(lines) > MAX_LINES:
        errs.append('全文%d行,超过%d行;先删次要的证据和时间线' % (len(lines), MAX_LINES))
    for n, s in enumerate(lines, 1):
        if not s.strip():
            add(n, '空行,删除')
            continue
        if cols(s) > MAX_COLS:
            add(n, '超过%d列(现在%d列,中文和全角符号算2列),拆到下一个序号' % (MAX_COLS, cols(s)))
        if '\t' in s:
            add(n, '有Tab,改成一个空格')
        if '  ' in s or '\u3000' in s or '\xa0' in s:
            add(n, '有连续空格或全角空格,只留一个半角空格')
        if s != s.rstrip():
            add(n, '行尾有空格,删除')
        if TABLE.search(s):
            add(n, '像表格线、框线或代码块标记,改成纯文本行')
        if SECRET.search(s):
            add(n, '疑似密钥/口令/令牌/连接串密码,删除')
        if not allow_ip and IP.search(s):
            add(n, '疑似IP地址,改成别名 node-A 等(现场允许写IP时加 --allow-ip)')
        if n > 1 and EMPTY.search(s):
            add(n, '等号后缺值,写 NA')
    if not HEAD.match(lines[0]):
        add(1, '第1行必须是 FMT=C2 | RPT=编号 | TZ=+08 | 日期=YYYY-MM-DD | 作者=名字')
    if len(lines) < 2 or not lines[1].startswith('#图例'):
        add(2, '第2行必须以 #图例 开头')
    key_n = None
    sec, seq, numbered = -1, 0, 0
    end_seen = False
    defined, used = {}, {}
    for n, s in enumerate(lines[2:], 3):
        if not s.strip():
            continue
        if end_seen:
            add(n, '§END 之后禁止再写任何字')
            continue
        m = re.match(r'^§END 节=0-(\d+) 编号行=(\d+)$', s)
        if m:
            end_seen = True
            if int(m.group(1)) != sec:
                add(n, '§END 节数写的是0-%s,实际是0-%d' % (m.group(1), sec))
            if int(m.group(2)) != numbered:
                add(n, '§END 编号行写的是%s,实际是%d' % (m.group(2), numbered))
            continue
        m = re.match(r'^§(\d+)(?: (\S.*))?$', s)
        if m:
            k = int(m.group(1))
            if k != sec + 1:
                add(n, '节号应为§%d,现在是§%d' % (sec + 1, k))
            sec, seq = k, 0
            if k == 0:
                km = re.match(r'^§0 KEY 字段序: (\S.*)$', s)
                if not km:
                    add(n, '§0 必须写成 §0 KEY 字段序: 字段1 | 字段2 | ...')
                else:
                    key_n = len(km.group(1).split('|'))
                    if key_n > MAX_KEY_FIELDS:
                        add(n, '§0 最多%d个字段,现在%d个' % (MAX_KEY_FIELDS, key_n))
            elif not m.group(2) or len(m.group(2).split()) < 2:
                add(n, '节标题写成 §数字 英文名 中文名')
            continue
        m = re.match(r'^(\d+)\.(\d+) (\S.*)$', s)
        if not m:
            add(n, '没有编号的行;改成 节号.序号 开头,或并入上一行')
            continue
        numbered += 1
        a, b = int(m.group(1)), int(m.group(2))
        if a != sec:
            add(n, '编号%d.%d不在当前节§%d里' % (a, b, sec))
        if b != seq + 1:
            add(n, '序号应为%d.%d,现在是%d.%d' % (sec, seq + 1, a, b))
        seq = b
        body = m.group(3)
        for e in re.findall(r'\[E-(\d+)\b', body):
            if e in defined:
                add(n, 'E-%s 已在第%d行定义过,每个E编号只用一次' % (e, defined[e]))
            else:
                defined[e] = n
        for e in re.findall(r'(?<!\[)\bE-(\d+)\b', body):
            used.setdefault(e, n)
        if sec == 0 and key_n is not None:
            if body.count('|') != body.count(' | '):
                add(n, '§0 字段之间用 " | " 分隔(两边各一个空格)')
            f = [v.strip() for v in body.split('|')]
            if len(f) != key_n:
                add(n, '§0 字段数应为%d,现在是%d' % (key_n, len(f)))
            for v in f:
                if v.lower() in BAD_NA:
                    add(n, '§0 缺值必须写 NA,不能写"%s"' % v)
    for e, n in sorted(used.items(), key=lambda x: x[1]):
        if e not in defined:
            add(n, '引用了E-%s,但§证据节里没有 [E-%s ...] 行' % (e, e))
    if key_n is None:
        errs.append('缺少 §0 KEY 节')
    if not end_seen:
        errs.append('最后一行缺少 §END 节=0-N 编号行=M')
    return errs


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    args = [a for a in sys.argv[1:] if a != '--allow-ip']
    if len(args) != 1:
        print('用法: python3 check_compact.py 报告.txt [--allow-ip]')
        return 2
    try:
        with open(args[0], encoding='utf-8-sig') as fh:
            lines = fh.read().splitlines()
    except (IOError, OSError):
        print('ERR 找不到文件: ' + args[0])
        return 2
    except UnicodeDecodeError:
        print('ERR 文件不是UTF-8,请另存为UTF-8')
        return 2
    while lines and not lines[-1].strip():
        lines.pop()
    errs = check(lines, '--allow-ip' in sys.argv)
    if errs:
        print('ERR 共%d处' % len(errs))
        print('\n'.join(errs[:MAX_SHOW]))
        if len(errs) > MAX_SHOW:
            print('其余%d处,先改这些再运行' % (len(errs) - MAX_SHOW))
        return 1
    print('OK 行数=%d' % len(lines))
    return 0


if __name__ == '__main__':
    sys.exit(main())
