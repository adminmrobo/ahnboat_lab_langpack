#!/usr/bin/env python3
"""언어팩 v1.3 (global-i18n v2.0 + 패치 VER1.0 구현) — 한국어 HTML 시리즈를 6개 언어판으로.

사용법 (프로젝트 폴더에서):
  python3 langpack/langpack.py extract            번역 단위 뽑기 (모든 대상 HTML, 같은 문장은 하나로)
  python3 langpack/langpack.py roundtrip          번역 없이 다시 끼워 원본과 같은지 확인
  python3 langpack/langpack.py seed               씨앗 번역 메모리(tm_seed/)를 검사한 뒤 작업 메모리에 합치기 (선택)
  python3 langpack/langpack.py pending <L>        번역 메모리에 없는 단위만 묶음으로 → work/<L>_001.json …
                                                  (에이전트 실행에서 Read 한도를 넘으면 <L>_001.p1.json, .p2.json … 조각)
  python3 langpack/langpack.py check <L> <out.json> [묶음]
                                                  검사 → 통과분 흡수, 실패 id는 work/<L>_r001.json 재시도 묶음
  python3 langpack/langpack.py retry              모든 언어의 실패분을 한 묶음 work/retry_001.json 으로 (패치 6장)
  python3 langpack/langpack.py check-retry <out.json>
  python3 langpack/langpack.py merge [<L>|all]    조립 → dist/ (언어 전환·🌐 배너·hreflang·글꼴·CC deed·꼬리표 현지화, README 7개 언어)
  python3 langpack/langpack.py cost-add <L> <묶음> <tokens> <tool_calls> <model>
                                                  번역 비용 한 줄을 work/cost.csv에 더하기
  python3 langpack/langpack.py stats              단위·메모리·씨앗 채움·비용 합계
  python3 langpack/langpack.py codecheck [--run]  번역판 Colab 코드 블록 compile (--run: 실제 실행). 원본에서 되는 블록만
설정: langpack/config.json (config.example.json 참고)
"""
import json, re, sys, os, glob, csv, datetime, signal
class _QuietPipe:
    """`| head`로 출력을 잘라도 명령은 끝까지 돈다 (v1.3). 읽는 쪽이 닫히면 남은 출력만 버린다.
    (v1.2의 SIGPIPE 기본 처리는 프로세스를 조용히 끝내서 seed·pending이 중간에 멈췄다.)"""
    def __init__(self, s): self.s, self.dead = s, False
    def write(self, x):
        if self.dead: return len(x)
        try: return self.s.write(x)
        except (BrokenPipeError, OSError): self.dead = True; return len(x)
    def flush(self):
        if self.dead: return
        try: self.s.flush()
        except (BrokenPipeError, OSError): self.dead = True
    def __getattr__(self, k): return getattr(self.s, k)
if not isinstance(sys.stdout, _QuietPipe): sys.stdout = _QuietPipe(sys.stdout)

PACK = os.path.dirname(os.path.abspath(__file__))
_cfg = os.path.join(PACK, 'config.json')
if not os.path.exists(_cfg): sys.exit('langpack/config.json이 없습니다. config.example.json을 복사해 config.json으로 만들고 pages를 고치세요.')
CFG = json.load(open(_cfg, encoding='utf-8'))
PROJ = os.path.abspath(os.path.join(PACK, CFG.get('projectDir', '..')))
WORK = os.path.join(PACK, 'work'); os.makedirs(WORK, exist_ok=True)
DIST = os.path.join(PROJ, CFG.get('distDir', 'dist'))
LANGS = CFG.get('langs', ['en', 'zh', 'ja', 'ru', 'uz', 'vi'])
HANGUL = re.compile('[가-힣ㄱ-ㅎㅏ-ㅣ]')
INLINE = set('b i em strong span sup sub a br small code u mark abbr q s del ins kbd var'.split())
ATTRS = CFG.get('attrs', ['alt', 'aria-label', 'placeholder', 'title', 'content', 'data-tip'])
DATA_IDS = CFG.get('dataBlocks', {'kg': 'kg-raw', 'meta': 'page-meta'})
SKIP_JSON_IDS = set(CFG.get('skipJsonIds', ['kg-ld', 'refs-csl']))
NATIVE = {'ko': '한국어', 'en': 'English', 'zh': '中文', 'ja': '日本語', 'uz': 'Oʻzbekcha', 'ru': 'Русский', 'vi': 'Tiếng Việt'}

def pages():
    out = []
    for pat in CFG['pages']:
        out += sorted(glob.glob(os.path.join(PROJ, pat)))
    dist_abs = os.path.abspath(DIST)
    out = [p for p in out if not os.path.abspath(p).startswith(dist_abs + os.sep)]
    out = [p for p in out if not re.search(r'\.(%s)\.html$' % '|'.join(LANGS), p)]
    if not out: sys.exit('대상 HTML이 없습니다. config.json의 pages를 확인하세요.')
    return out
def rel(p): return os.path.relpath(p, PROJ)
def load(p): return open(p, encoding='utf-8').read()

# ---------- 스크립트 문자열 찾기 ----------
def js_strings(src, base):
    """문자열 리터럴 목록 (start,end,quote,raw,exprs). 템플릿의 ${…}는 {n}으로 바꾼다."""
    out, i, n, prev = [], 0, len(src), ''
    while i < n:
        c = src[i]
        if c == '/' and i + 1 < n and src[i+1] == '/':
            j = src.find('\n', i); i = n if j < 0 else j; continue
        if c == '/' and i + 1 < n and src[i+1] == '*':
            j = src.find('*/', i + 2); i = n if j < 0 else j + 2; continue
        if c == '/' and (prev in '(,=:[!&|?{};+-*%<>~^' or prev == '' or src[max(0, i-12):i].rstrip().endswith(('return', 'typeof'))):
            j = i + 1; cls = False
            while j < n:
                if src[j] == '\\': j += 2; continue
                if src[j] == '[': cls = True
                elif src[j] == ']': cls = False
                elif src[j] == '/' and not cls: break
                elif src[j] == '\n': break
                j += 1
            i = j + 1; prev = 'r'; continue
        if c in '\'"':
            j = i + 1
            while j < n and src[j] != c and src[j] != '\n':
                if src[j] == '\\': j += 1
                j += 1
            out.append((base + i, base + j + 1, c, src[i+1:j], []))
            i = j + 1; prev = 's'; continue
        if c == '`':
            j = i + 1; exprs = []; buf = ''
            while j < n and src[j] != '`':
                if src[j] == '\\': buf += src[j:j+2]; j += 2; continue
                if src[j] == '$' and j + 1 < n and src[j+1] == '{':
                    depth = 1; k = j + 2
                    while k < n and depth:
                        if src[k] == '{': depth += 1
                        elif src[k] == '}': depth -= 1
                        elif src[k] in '\'"`':
                            q = src[k]; k += 1
                            while k < n and src[k] != q:
                                if src[k] == '\\': k += 1
                                k += 1
                        k += 1
                    buf += '{%d}' % len(exprs); exprs.append(src[j+2:k-1]); j = k; continue
                buf += src[j]; j += 1
            out.append((base + i, base + j + 1, '`', buf, exprs))
            i = j + 1; prev = 's'; continue
        if not c.isspace(): prev = c
        i += 1
    return out

def skipped_js(text, a):
    """설정의 skipCallArgs(함수 인자)·skipVars(변수 값)에 해당하는 문자열인가 (시리즈 3)."""
    before = text[max(0, a - 160):a]
    for fn in CFG.get('skipCallArgs', []):
        if re.search(r'\b%s\s*\((?:[^()]*,)?\s*$' % re.escape(fn), before): return True
    for v in CFG.get('skipVars', []):
        if re.search(r'\b%s\s*=\s*$' % re.escape(v), before): return True
    return False

# ---------- 코드 블록 (v1.3: Colab 코드 줄 단위) ----------
CODE_TYPES = CFG.get('codeTypes', ['text/plain'])
def is_code(attrs):
    m = re.search(r'type="([^"]*)"', attrs); return bool(m and m.group(1) in CODE_TYPES)

def py_scan(line, state=None):
    """파이썬 한 줄을 훑어 '코드 골격'(주석과 문자열 안의 글을 뺀 것 + f-string의 {식})과 줄 끝 상태(열린 삼중따옴표)를 돌려준다.
    state: 줄 시작에 열려 있던 삼중따옴표('"""' 또는 "'''") 또는 None."""
    sk, i, n, st, fs = [], 0, len(line), state, False
    while i < n:
        c = line[i]
        if st:
            if line.startswith(st, i): sk.append(st); i += len(st); st = None; continue
            if c == '\\': i += 2; continue
            if fs and c == '{':
                if line.startswith('{{', i): i += 2; continue
                d, k = 1, i + 1
                while k < n and d:
                    d += {'{': 1, '}': -1}.get(line[k], 0); k += 1
                sk.append(line[i:k]); i = k; continue
            i += 1; continue
        if c == '#': break
        if c in '"\'':
            pre = re.search(r'([A-Za-z]{0,2})$', ''.join(sk)).group(1).lower(); fs = 'f' in pre
            st = c * 3 if line.startswith(c * 3, i) else c; sk.append(st); i += len(st); continue
        sk.append(c); i += 1
    if st and len(st) == 1: st = None          # 닫히지 않은 한 줄 문자열
    return re.sub(r'\s+', '', ''.join(sk)), st

def extract_code(text, s, e, U, spans, skip_chars):
    pos, st = s, None
    for line in text[s:e].split('\n'):
        start = st; _, st = py_scan(line, st)
        core = line.strip()
        if core and HANGUL.search(core) and core not in skip_chars:
            a = pos + (len(line) - len(line.lstrip()))
            spans.append([a, a + len(core), 'code', U.add(core, 'code' + (':' + start if start else '')), None])
        pos += len(line) + 1

# ---------- 추출 ----------
class Units:
    def __init__(self): self.by = {}; self.order = []
    def add(self, t, ctx=''):
        key = t + '\u0001' + ctx
        if key not in self.by:
            self.by[key] = {'id': 'u%04d' % (len(self.by) + 1), 't': t, 'ctx': ctx}
            self.order.append(key)
        return self.by[key]['id']
    def list(self): return [self.by[k] for k in self.order]

def ctx_tag(text, a):
    m = re.search(r'/\*i18n:([\w-]+)\*/\s*$', text[max(0, a - 40):a])   # 패치 3: /*i18n:문맥*/
    return m.group(1) if m else ''

def extract_page(text, U):
    spans = []
    regions = [(m.start(3), m.end(3), m.group(1), m.group(2)) for m in re.finditer(r'<(script|style)\b([^>]*)>(.*?)</\1>', text, re.S)]
    pos, markup = 0, []
    for s, e, k, a in regions: markup.append((pos, s)); pos = e
    markup.append((pos, len(text)))
    skip_chars = set(CFG.get('skipStrings', []))
    # 1) 마크업: 블록 경계 사이의 글 + 인라인 태그 = 한 단위
    for ms, me in markup:
        run = []; nested = []; skip = [False]
        def flush():
            if run:
                s, e = run[0][0], run[-1][1]; raw = text[s:e]
                if HANGUL.search(re.sub(r'<[^>]+>', '', raw)) and not skip[0]:
                    lead = len(raw) - len(raw.lstrip()); trail = len(raw) - len(raw.rstrip())
                    core = raw[lead:len(raw) - trail]
                    if core not in skip_chars:
                        spans.append([s + lead, e - trail, 'html', U.add(core), None])
                        for a in nested: U.add(a[4], 'attr')   # 인라인 태그 속성은 html 단위 안에서 번역 (겹침 방지)
                        nested.clear()
                spans.extend(x[:4] + [None] for x in nested)
            run.clear(); nested.clear()
        for m in re.finditer(r'<!--.*?-->|<[^>]+>|[^<]+', text[ms:me], re.S):
            s, e, t = m.start() + ms, m.end() + ms, m.group(0)
            if t.startswith('<!--'): flush(); continue
            if t.startswith('<'):
                nm = re.match(r'</?\s*([a-zA-Z0-9-]+)', t); nm = nm.group(1).lower() if nm else ''
                inline = nm in INLINE
                if not inline: flush(); skip[0] = 'data-i18n-skip' in t   # 표시한 요소의 글은 다음 블록 태그까지 건너뜀
                if 'data-i18n-skip' not in t:
                    for at in ATTRS:
                        for am in re.finditer(r'\s%s="([^"]*)"' % re.escape(at), t):
                            v = am.group(1)
                            if HANGUL.search(v) and v not in skip_chars:
                                v = v.replace('&quot;', '"').replace('&lt;', '<').replace('&amp;', '&')
                                if inline: nested.append([s + am.start(1), s + am.end(1), 'attr', U.add(v, 'attr'), v])
                                else: spans.append([s + am.start(1), s + am.end(1), 'attr', U.add(v, 'attr'), None])
                if inline: run.append((s, e, t))
            else: run.append((s, e, t))
        flush()
    # 2) <style>: content:"…"
    for s, e, kind, attrs in regions:
        if kind != 'style': continue
        for m in re.finditer(r'content\s*:\s*(["\'])(.*?)\1', text[s:e]):
            if HANGUL.search(m.group(2)):
                spans.append([s + m.start(2), s + m.end(2), 'css', U.add(m.group(2), 'css'), None])
    # 3) <script>
    for s, e, kind, attrs in regions:
        if kind != 'script': continue
        idm = re.search(r'id="([^"]+)"', attrs); sid = idm.group(1) if idm else ''
        if sid == DATA_IDS.get('kg'):
            for nd in json.loads(text[s:e]).get('nodes', []):
                for f in ('label', 'definition'):
                    v = (nd.get(f) or {}).get('ko')
                    if v and HANGUL.search(v): U.add(v, 'kg')
            spans.append([s, e, 'data', sid, None]); continue
        if sid == DATA_IDS.get('meta'):
            obj = json.loads(text[s:e])
            for f in CFG.get('metaFields', ['title', 'series']):
                v = obj.get(f)
                for x in (v if isinstance(v, list) else [v]):
                    if isinstance(x, str) and HANGUL.search(x): U.add(x, 'kg')
            spans.append([s, e, 'data', sid, None]); continue
        if sid in SKIP_JSON_IDS or re.search(r'type="[^"]*json', attrs) or 'data-i18n-skip' in attrs: continue
        if is_code(attrs): extract_code(text, s, e, U, spans, skip_chars); continue
        src = text[s:e]
        for a, b, q, raw, exprs in js_strings(src, s):
            if not HANGUL.search(raw) or raw in skip_chars or skipped_js(text, a): continue
            spans.append([a, b, 'js', U.add(raw, 'js:' + ctx_tag(text, a) if ctx_tag(text, a) else 'js'), {'q': q, 'exprs': exprs}])
    return spans

def add_hints(U, texts):
    byid = {u['id']: u for u in U.list()}; hm, hc = CFG.get('hintMaxLen', 20), CFG.get('hintChars', 30)
    for page, (text, spans) in texts.items():
        for s, e, kind, uid, extra in spans:
            if kind not in ('html', 'attr', 'js', 'css'): continue   # 코드 줄은 줄 자체가 문맥
            u = byid[uid]
            if 'h' in u: continue
            if len(re.sub(r'<[^>]+>', '', u['t'])) < hm or u['t'] != u['t'].strip():
                clean = lambda x: re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', x))
                if kind == 'js':   # 코드 대신 같은 줄의 다른 한글 문자열만 문맥으로 (입력 절약)
                    line_s = text.rfind('\n', 0, s) + 1; line_e = text.find('\n', e); line_e = len(text) if line_e < 0 else line_e
                    near = [m.group(1) for m in re.finditer(r"['\"`]([^'\"`\n]*[가-힣][^'\"`\n]*)['\"`]", text[max(line_s, s - 200):min(line_e, e + 200)]) if m.group(1) != u['t']]
                    if near: u['h'] = ' | '.join(near)[:hc * 2]
                else:
                    u['h'] = clean(text[max(0, s - 120):s])[-hc:] + '⟦⟧' + clean(text[e:e + 120])[:hc]

README_SRC = [None]   # (README 원문 + 생성한 「언어」 절, spans)
def extract_all(save=True):
    U = Units(); texts = {}
    for p in pages():
        t = load(p); texts[rel(p)] = (t, extract_page(t, U))
    add_hints(U, texts)
    if CFG.get('readme'):
        rt = readme_source(); README_SRC[0] = (rt, extract_md(rt, U)) if rt is not None else None
    if save:
        json.dump(U.list(), open(os.path.join(WORK, 'units.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
        print('pages', len(texts), 'units', len(U.list()), 'chars', sum(len(u['t']) for u in U.list()))
    return U, texts

# ---------- 끼워 넣기 ----------
def js_escape(s, q):
    """번역문을 원래 따옴표 문자열 안에 넣을 수 있게. 단위 글은 소스에 적힌 그대로(\\n 같은 이스케이프 포함)라서
    이미 있는 이스케이프(\\x)는 건드리지 않고, 맨 따옴표·실제 줄바꿈·(템플릿이면) 식이 아닌 ${ 만 막는다. (v1.3: 이전에는 \\n이 \\\\n으로 두 겹이 됐다)"""
    out, i, n = [], 0, len(s)
    while i < n:
        c = s[i]
        if c == '\\' and i + 1 < n: out.append(s[i:i+2]); i += 2; continue
        if c == '\\': out.append('\\\\'); i += 1; continue
        if c == q: out.append('\\' + c)
        elif c == '\n': out.append('\\n')
        elif q == '`' and c == '$' and s.startswith('${', i) and not re.match(r'\$\{\d+\}', s[i:]): out.append('\\$')
        else: out.append(c)
        i += 1
    return ''.join(out)
def fill_template(tr, exprs):
    return re.sub(r'\$?\{(\d+)\}', lambda m: ('$' if m.group(0).startswith('$') else '') + '${' + exprs[int(m.group(1))] + '}', js_escape(tr, '`'))

def apply(text, spans, U, T, lang, page):
    byid = {u['id']: u for u in U.list()}
    kgid = {u['t']: u['id'] for u in U.list() if u['ctx'] == 'kg'}
    out = text
    for s, e, kind, uid, extra in sorted(spans, key=lambda x: -x[0]):
        if kind == 'data':
            if lang in (None, '__rt'): continue
            obj = json.loads(out[s:e])
            if uid == DATA_IDS.get('kg'):
                for nd in obj.get('nodes', []):
                    for f in ('label', 'definition'):
                        d = nd.get(f) or {}; v = d.get('ko'); k = kgid.get(v)
                        if not (k and k in T): continue
                        if lang != 'en': d[lang] = T[k]
                        elif f == 'definition' or HANGUL.search(d.get('en', '')): d['en'] = T[k]
            else:
                for f in CFG.get('metaFields', ['title', 'series']):
                    v = obj.get(f); tr1 = lambda x: T.get(kgid.get(x), x)
                    if isinstance(v, list): obj[f] = [tr1(x) if isinstance(x, str) else x for x in v]
                    elif isinstance(v, str) and HANGUL.search(v): obj[f + '_ko'] = v; obj[f] = tr1(v)
                obj['language'] = [lang]; obj['translationOf'] = os.path.basename(page)
            out = out[:s] + json.dumps(obj, ensure_ascii=False).replace('</', '<\\/') + out[e:]; continue
        if lang is None: continue
        tr = T.get(uid, byid[uid]['t'])
        if kind == 'html':
            new = tr
            if lang != '__rt':
                attr_t = {u['t']: T.get(u['id']) for u in U.list() if u['ctx'] == 'attr'}
                new = re.sub(r'(\s(?:%s)=")([^"]*)(")' % '|'.join(map(re.escape, ATTRS)),
                             lambda m: m.group(1) + (attr_t.get(m.group(2).replace('&quot;', '"')) or m.group(2)).replace('"', '&quot;') + m.group(3) if HANGUL.search(m.group(2)) else m.group(0), new)
        elif kind == 'attr': new = out[s:e] if lang == '__rt' else tr.replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;')
        elif kind == 'css': new = tr.replace('\\', '\\\\').replace('"', '\\"')
        elif kind == 'code': new = tr.replace('\n', ' ').replace('</script', '<\\/script')
        else:
            q = extra['q']
            new = '`' + fill_template(tr, extra['exprs']) + '`' if q == '`' else q + js_escape(tr, q) + q
        out = out[:s] + new + out[e:]
    return out

def roundtrip():
    U, texts = extract_all(save=False); ok = True
    T = {u['id']: u['t'] for u in U.list()}
    for page, (t, spans) in texts.items():
        b = apply(t, spans, U, T, '__rt', page)
        if b != t:
            ok = False; i = next(i for i, (x, y) in enumerate(zip(t, b)) if x != y)
            print('FAIL', page); print('  원본', repr(t[i-60:i+60])); print('  복원', repr(b[i-60:i+60]))
    if README_SRC[0]:
        rt, sp = README_SRC[0]
        if apply_md(rt, sp, T) != rt: ok = False; print('FAIL README')
        else: print('README OK', len(sp), '단위')
    print('roundtrip', 'OK' if ok else 'FAIL', len(texts), 'pages')
    return ok

# ---------- 번역 메모리·묶음 ----------
def tmkey(u):
    """번역 메모리 열쇠: 문장. /*i18n:문맥*/ 꼬리표가 있으면 문장+꼬리표 (패치 3)."""
    c = u.get('ctx', ''); return u['t'] + ('\u0001' + c[3:] if c.startswith('js:') else '')

def tm_path(L): d = os.path.join(WORK, L); os.makedirs(d, exist_ok=True); return os.path.join(d, 'tm.json')
def load_tm(L):
    p = tm_path(L); return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}
def save_tm(L, tm): json.dump(tm, open(tm_path(L), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
def glossary():
    g = {}
    for f in sorted(glob.glob(os.path.join(PACK, 'rules', 'glossary', '*.json'))):
        for k, v in json.load(open(f, encoding='utf-8')).items(): g.setdefault(k, {}).update(v)
    return g

RUNNER = CFG.get('runner', 'agent')
BUNDLE_DEFAULT = {'agent': 30000, 'api': 12000}   # v1.2: 에이전트는 고정비가 커서 묶음을 크게, API는 작게
def bundle_chars(): return CFG.get('bundleChars') or BUNDLE_DEFAULT.get(RUNNER, 30000)

def rules_lines(L, code=False, md=False):
    """규칙 파일을 줄 목록으로 (Read 도구는 아주 긴 줄을 자르므로 한 줄에 한 줄씩). 코드 줄·README 줄이 있는 묶음에만 그 규칙을 더한다."""
    out = []
    fs = [os.path.join(PACK, 'rules', 'common.md'), os.path.join(PACK, 'rules', 'lang', L + '.md')]
    if code: fs.append(os.path.join(PACK, 'rules', 'code.md'))
    if md: fs.append(os.path.join(PACK, 'rules', 'readme.md'))
    for f in fs:
        if os.path.exists(f): out += [x for x in open(f, encoding='utf-8').read().splitlines() if x.strip()]
    return out

def bundle_obj(L, b, gl, with_rules):
    text = ' '.join(u['t'] for u in b); obj = {}
    code = [u['id'] for u in b if u['ctx'].startswith('code')]; md = [u['id'] for u in b if u['ctx'] == 'md']
    if with_rules: obj['rules'] = rules_lines(L, bool(code), bool(md))
    obj.update({'lang': L, 'glossary': {k: v[L] for k, v in gl.items() if k in text and L in v},
                'hints': {u['id']: u['h'] for u in b if 'h' in u}})
    if code: obj['code'] = code     # 파이썬 코드 한 줄인 단위 (rules/code.md)
    if md: obj['md'] = md           # README 마크다운 줄 (rules/readme.md)
    obj['units'] = {u['id']: u['t'] for u in b}
    return obj
def dumps(obj): return json.dumps(obj, ensure_ascii=False, indent=0)   # indent=0 → 한 줄에 한 단위
def est_tokens(s): return int(len(s) * CFG.get('tokensPerChar', 0.9))   # 실측: 묶음 JSON 62,555자 = 53,973토큰 (0.86)

def split_parts(L, b, gl, inline):
    """에이전트 실행: 묶음 파일 하나가 Read 한도(bundleMaxTokens)를 넘으면 조각으로 나눈다. 조각은 한 에이전트가 한 번에 모두 읽는다."""
    lim = CFG.get('bundleMaxTokens', 20000)
    if RUNNER != 'agent' or est_tokens(dumps(bundle_obj(L, b, gl, inline))) <= lim: return [b]
    parts, cur = [], []
    for u in b:
        if cur and est_tokens(dumps(bundle_obj(L, cur + [u], gl, inline and not parts))) > lim: parts.append(cur); cur = []
        cur.append(u)
    if cur: parts.append(cur)
    return parts

def write_bundles(L, units, tag='', start=1):
    gl = glossary(); lim = bundle_chars(); inline = CFG.get('inlineRules', True) and RUNNER == 'agent'; bundles, cur, size = [], [], 0
    for u in units:
        if cur and size + len(u['t']) > lim: bundles.append(cur); cur, size = [], 0
        cur.append(u); size += len(u['t'])
    if cur: bundles.append(cur)
    names = []
    for i, b in enumerate(bundles, start):
        base = '%s_%s%03d' % (L, tag, i); parts = split_parts(L, b, gl, inline)
        for j, pb in enumerate(parts, 1):
            name = base + ('.json' if len(parts) == 1 else '.p%d.json' % j)
            s = dumps(bundle_obj(L, pb, gl, inline and j == 1))
            open(os.path.join(WORK, name), 'w', encoding='utf-8').write(s)
            print(name, len(pb), 'units', sum(len(u['t']) for u in pb), 'chars', '파일', len(s), '자 ≈', est_tokens(s), '토큰(어림)')
        names.append(base + '.json')
    return names

def bundle_files(name):
    """묶음 이름(en_001 / en_001.json) → 실제 파일들 (조각이면 .p1 .p2 …)."""
    base = os.path.basename(name); base = base[:-5] if base.endswith('.json') else base
    one = os.path.join(WORK, base + '.json')
    if os.path.exists(one): return [one]
    fs = sorted(glob.glob(os.path.join(WORK, base + '.p*.json')), key=lambda f: int(re.search(r'\.p(\d+)\.json$', f).group(1)))
    if not fs: sys.exit('묶음 파일이 없습니다: ' + base)
    return fs
def bundle_units(name):
    U = {}
    for f in bundle_files(name): U.update(json.load(open(f, encoding='utf-8'))['units'])
    return U

def pending(L):
    U = json.load(open(os.path.join(WORK, 'units.json'), encoding='utf-8')); tm = load_tm(L)
    todo = [u for u in U if tmkey(u) not in tm]
    if not todo: print(L, '번역할 단위 없음 (모두 번역 메모리에 있음)'); return []
    return write_bundles(L, todo)

def seeded_path(L): return os.path.join(os.path.dirname(tm_path(L)), 'seeded.json')
def load_seeded(L):
    p = seeded_path(L); return set(json.load(open(p, encoding='utf-8'))) if os.path.exists(p) else set()

def seed():
    """씨앗 메모리를 합친다. `_`로 시작하는 열쇠(출처 표시)는 건너뛰고, 번역마다 check와 같은 검사를 거친다."""
    up = os.path.join(WORK, 'units.json'); U = json.load(open(up, encoding='utf-8')) if os.path.exists(up) else []
    for L in LANGS:
        p = os.path.join(PACK, 'tm_seed', L + '.json')
        if not os.path.exists(p): continue
        tm = load_tm(L); s = json.load(open(p, encoding='utf-8')); sd = load_seeded(L); n = bad = 0
        before = sum(1 for u in U if tmkey(u) in tm)
        for k, v in s.items():
            if k.startswith('_') or k in tm: continue
            if check_one(k.split('\u0001')[0], v, L): bad += 1; continue
            tm[k] = v; sd.add(k); n += 1
        save_tm(L, tm); json.dump(sorted(sd), open(seeded_path(L), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
        after = sum(1 for u in U if tmkey(u) in tm)
        src = s.get('_source', '?')
        print('seed', L, '+%d' % n, '(검사 탈락 %d)' % bad, '출처', src, '| 이 프로젝트 단위 채움 %d → %d / %d' % (before, after, len(U)) if U else '')

# ---------- 검사 ----------
KMUL = re.compile(r'(\d+(?:\.\d+)?)\s*만(?:\s*(\d+)\s*천)?|(\d+)\s*천')
TMUL = [(r'k\b|K\b|thousand|тыс\.?|тысяч\w*|ming\b|nghìn|ngàn|千', 1000), (r'million\w*|mln\.?|млн\.?|миллион\w*|triệu|百万', 1000000),
        (r'billion\w*|mlrd\.?|млрд\.?|миллиард\w*|tỷ', 1000000000), (r'万|萬', 10000), (r'億|亿', 100000000)]
def nums(s, ko=False):
    s = re.sub(r'<[^>]+>', ' ', s); s = re.sub(r'\{\d+\}', ' ', s)
    if ko:
        s = KMUL.sub(lambda m: str(int(float(m.group(1)) * 10000 + (int(m.group(2)) * 1000 if m.group(2) else 0))) if m.group(1) else str(int(m.group(3)) * 1000), s)
        s = re.sub(r'(\d+)\s*(?:차(?!원)|등(?!분)|번째)', ' ', s)   # 서수는 빼고 비교 (시리즈 4)
    else:
        for pat, mul in TMUL:
            s = re.sub(r'(\d+(?:\.\d+)?)\s*(?:' + pat + ')', lambda m, mul=mul: str(int(round(float(m.group(1)) * mul))), s)
    s = re.sub(r'(?<=\d)[,   ](?=\d{3}\b)', '', s)
    return sorted(x.replace(',', '.') for x in re.findall(r'\d+(?:[.,]\d+)?', s))

def check_one(src, tr, L, ctx=''):
    if not isinstance(tr, str) or not tr.strip(): return ['빈 번역']
    errs = []
    if ctx.startswith('code'):   # v1.3: 코드 골격(주석·문자열 글 밖)과 f-string 식이 원문과 같아야
        st = ctx[5:] or None
        if '\n' in tr: errs.append('줄바꿈')
        if py_scan(src, st) != py_scan(tr, st): errs.append('코드 바뀜')
    if ctx.startswith('js') and sorted(re.findall(r'\\.', src)) != sorted(re.findall(r'\\.', tr)): errs.append('이스케이프')   # v1.3: \\n 등은 그대로
    if ctx == 'md':              # v1.3: README 링크 주소·한글 없는 코드 조각은 그대로
        links = lambda x: sorted(re.findall(r'\]\(([^)\s]+)', x))
        cs, ct = re.findall(r'`[^`]+`', src), re.findall(r'`[^`]+`', tr)
        if links(src) != links(tr): errs.append('링크')
        if len(cs) != len(ct) or any(c not in ct for c in cs if not HANGUL.search(c)): errs.append('코드 조각')
    if HANGUL.search(re.sub(r'<[^>]+>', '', tr)): errs.append('한글 남음')   # 태그 속 한글은 조립 때 속성 단위로 번역
    if sorted(re.findall(r'\{\d+\}', src)) != sorted(re.findall(r'\{\d+\}', tr)): errs.append('자리표시')
    tags = lambda s: sorted(re.sub(r'\s+', ' ', t) for t in re.findall(r'<[^>]+>', s))
    if tags(src) != tags(tr): errs.append('태그')
    if sorted(re.findall(r'&\w+;', src)) != sorted(re.findall(r'&\w+;', tr)): errs.append('엔티티')
    if L not in ('zh', 'ja') and ((src[:1].isspace() != tr[:1].isspace()) or (src[-1:].isspace() != tr[-1:].isspace())): errs.append('앞뒤 공백')
    a, b = nums(src, True), nums(tr)
    if a != b:
        ra = [x for x in a if x not in b]; rb = [x for x in b if x not in a]
        big = lambda xs: [x for x in xs if not (x.isdigit() and int(x) <= 10)]   # 1~10을 낱말로 쓴 경우 허용
        if big(ra) or big(rb): errs.append('숫자 %s→%s' % (ra, rb))
    return errs

def read_out(path): return read_out_text(open(path, encoding='utf-8').read())
def read_out_text(raw):
    raw = re.sub(r'^\s*```(?:json)?\s*|\s*```\s*$', '', raw)
    try: return json.loads(raw)
    except Exception:
        T = {}
        for m in re.finditer(r'"(u\d{4})"\s*:\s*"((?:[^"\\]|\\.)*)"', raw): T[m.group(1)] = json.loads('"' + m.group(2) + '"')
        print('  깨진 JSON → 줄 단위 복구', len(T)); return T

def absorb(L, T, want, Uby):
    tm = load_tm(L); bad = {}
    for uid in sorted(want):
        if uid not in T: bad[uid] = ['빠짐']; continue
        e = check_one(Uby[uid]['t'], T[uid], L, Uby[uid].get('ctx', ''))
        if e: bad[uid] = e
        else: tm[tmkey(Uby[uid])] = T[uid]
    save_tm(L, tm); return bad

def check(L, outfile, bundle=None):
    Uby = {u['id']: u for u in json.load(open(os.path.join(WORK, 'units.json'), encoding='utf-8'))}
    T = read_out(outfile)
    want = set(bundle_units(bundle)) if bundle else set(T)
    bad = absorb(L, T, want, Uby)
    print('check', L, os.path.basename(outfile), '통과', len(want) - len(bad), '/', len(want))
    for k, v in list(bad.items())[:40]: print('  ', k, v, '|', Uby[k]['t'][:50], '→', str(T.get(k, ''))[:50])
    if bad:
        n = len({re.match(r'(%s_r\d+)' % L, os.path.basename(f)).group(1) for f in glob.glob(os.path.join(WORK, '%s_r*.json' % L))
                 if not f.endswith('.out.json') and re.match(r'%s_r\d+' % L, os.path.basename(f))}) + 1
        write_bundles(L, [Uby[k] for k in bad], tag='r', start=n)
    return bad

def retry_all():
    """언어별 남은 단위를 한 묶음으로 (재시도는 한 번만 부른다)."""
    U = json.load(open(os.path.join(WORK, 'units.json'), encoding='utf-8')); gl = glossary(); tasks = {}
    for L in LANGS:
        tm = load_tm(L); todo = [u for u in U if tmkey(u) not in tm]
        if todo:
            text = ' '.join(u['t'] for u in todo)
            tasks[L] = {'glossary': {k: v[L] for k, v in gl.items() if k in text and L in v}, 'units': {u['id']: u['t'] for u in todo}}
    if not tasks: print('재시도할 단위 없음'); return
    n = len([f for f in glob.glob(os.path.join(WORK, 'retry_*.json')) if not f.endswith('.out.json')]) + 1
    name = 'retry_%03d.json' % n
    json.dump({'tasks': tasks}, open(os.path.join(WORK, name), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(name, {L: len(t['units']) for L, t in tasks.items()})

def check_retry(outfile):
    Uby = {u['id']: u for u in json.load(open(os.path.join(WORK, 'units.json'), encoding='utf-8'))}
    O = json.loads(re.sub(r'^\s*```(?:json)?\s*|\s*```\s*$', '', open(outfile, encoding='utf-8').read()))
    for L, T in O.items():
        bad = absorb(L, T, set(T), Uby); print('check-retry', L, '통과', len(T) - len(bad), '/', len(T), bad if bad else '')

# ---------- 조립 ----------
FONTS = CFG.get('fonts', {})
def out_name(page, L):
    r = rel(page)
    if L == 'ko': return r
    if CFG.get('layout', 'suffix') == 'folder': return os.path.join(L, r)
    return r[:-5] + '.' + L + '.html'

HTML_LANG = dict({'zh': 'zh-CN'}, **CFG.get('htmlLang', {}))          # <html lang>·hreflang 코드 (14-1)
def lang_code(L): return HTML_LANG.get(L, L)
ORDER = ['ko', 'en', 'zh', 'ja', 'uz', 'ru', 'vi']                     # 언어 표시 순서 (8장)
def all_langs(): return ['ko'] + [l for l in ORDER[1:] if l in LANGS] + [l for l in LANGS if l not in ORDER]
HOSTS = CFG.get('switcherHosts', [['#langSw', 'append'], ['nav.top .brand', 'after'], ['nav .in', 'append'], ['nav', 'append']])

SWITCHER_CSS = (
 '.i18n-pick{display:inline-flex;align-items:center;gap:4px;margin:0 8px;font:inherit;font-size:13px;white-space:nowrap}'
 '.i18n-pick select{font:inherit;font-size:13px;padding:3px 6px;border-radius:8px;border:1px solid var(--rule,rgba(128,128,128,.5));background:var(--panel,Canvas);color:var(--text,CanvasText)}'
 '.i18n-pick.float{position:fixed;top:calc(8px + env(safe-area-inset-top,0px));right:max(8px,env(safe-area-inset-right,0px));z-index:9998}'
 '#i18nBanner{position:fixed;right:max(14px,env(safe-area-inset-right,0px));bottom:max(14px,env(safe-area-inset-bottom,0px));z-index:9999;font:14px/1.3 var(--font,system-ui,sans-serif)}'
 '#i18nBanner>button{border-radius:999px;padding:9px 14px;border:1px solid var(--rule,#363a52);background:var(--panel,#1c1e2d);color:var(--text,#eceaf3);box-shadow:0 4px 14px rgba(0,0,0,.35);cursor:pointer;font:inherit}'
 '#i18nBanner ul{position:absolute;right:0;bottom:calc(100% + 8px);margin:0;padding:6px;list-style:none;min-width:150px;border-radius:12px;border:1px solid var(--rule,#363a52);background:var(--panel,#1c1e2d);box-shadow:0 8px 24px rgba(0,0,0,.4)}'
 '#i18nBanner ul[hidden]{display:none}'
 '#i18nBanner a{display:block;padding:7px 10px;border-radius:8px;color:var(--text,#eceaf3);text-decoration:none}'
 '#i18nBanner a:hover,#i18nBanner a:focus-visible{background:var(--panel2,#25283a)}'
 '#i18nBanner a[aria-current]{color:var(--amber,#f1b646);font-weight:700}'
 '@media print{#i18nBanner,.i18n-pick{display:none!important}}')

def switcher_js(page, L):
    """언어 전환 (8장). <head>의 <meta charset> 바로 뒤에 넣는다: 저장된 선택·?lang=·브라우저 언어로 이동, 이동 전 HEAD로 파일 확인(404 방지),
    DOM이 준비되면 최상단 메뉴의 🌐 선택 상자와 오른쪽 아래 🌐 배너를 단다."""
    here = os.path.dirname(out_name(page, L)) or '.'
    urls = {l: os.path.relpath(out_name(page, l), here).replace(os.sep, '/') for l in all_langs()}
    cfg = {'langs': [[l, NATIVE[l]] for l in all_langs()], 'urls': urls, 'cur': L, 'auto': CFG.get('autoRedirect', True),
           'key': CFG.get('langStorageKey', 'i18n_lang'), 'hosts': HOSTS, 'banner': CFG.get('banner', True), 'select': CFG.get('menuSelect', True)}
    js = r"""(function(){var C=__CFG__,cur=C.cur,ok={},de=document.documentElement;C.langs.forEach(function(l){ok[l[0]]=1});
function U(l){return C.urls[l]}
function save(l){try{localStorage.setItem(C.key,l)}catch(e){}}
function saved(){try{return localStorage.getItem(C.key)}catch(e){return null}}
function go(l){location.replace(U(l)+'?lang='+l+location.hash)}
var shown=function(){de.style.visibility=''};
function tryGo(l){if(location.protocol==='file:'){go(l);return}
 de.style.visibility='hidden';var t=setTimeout(shown,2500);
 try{fetch(U(l),{method:'HEAD',cache:'no-store'}).then(function(r){if(r.ok)go(l);else{clearTimeout(t);shown()}},function(){clearTimeout(t);shown()})}catch(e){clearTimeout(t);shown()}}
var q=null;try{q=new URLSearchParams(location.search).get('lang')}catch(e){}
if(q&&ok[q]){save(q);if(q!==cur){tryGo(q);}}
else if(cur==='ko'&&C.auto){var s=saved(),to=null;
 if(s&&ok[s]){if(s!=='ko')to=s;}
 else if(location.protocol!=='file:'){var same=false;try{same=!!document.referrer&&new URL(document.referrer).origin===location.origin}catch(e){}
  if(!same){var nav=(navigator.languages||[navigator.language||'']).map(function(x){return String(x).slice(0,2).toLowerCase()});
   for(var i=0;i<nav.length;i++){if(nav[i]==='ko')break;if(ok[nav[i]]){to=nav[i];break;}}}}
 if(to)tryGo(to);}
function pick(l){save(l);location.href=U(l)+'?lang='+l+location.hash;}
function name(l){for(var i=0;i<C.langs.length;i++)if(C.langs[i][0]===l)return C.langs[i][1];return l}
function mount(){if(document.getElementById('i18nSel'))return;
 if(C.select){var w=document.createElement('span');w.className='i18n-pick';w.innerHTML='<span aria-hidden="true">🌐</span>';
  var s=document.createElement('select');s.id='i18nSel';s.setAttribute('aria-label','Language');
  C.langs.forEach(function(l){var o=document.createElement('option');o.value=l[0];o.textContent=l[1];if(l[0]===cur)o.selected=true;s.appendChild(o);});
  s.addEventListener('change',function(){pick(s.value)});w.appendChild(s);var put=false;
  for(var i=0;i<C.hosts.length&&!put;i++){var h=document.querySelector(C.hosts[i][0]);if(!h)continue;var m=C.hosts[i][1];
   if(m==='after')h.insertAdjacentElement('afterend',w);else if(m==='before')h.insertAdjacentElement('beforebegin',w);else h.appendChild(w);put=true;}
  if(!put){w.classList.add('float');document.body.appendChild(w);}}
 if(C.banner&&!document.getElementById('i18nBanner')){var b=document.createElement('div');b.id='i18nBanner';
  var bt=document.createElement('button');bt.type='button';bt.setAttribute('aria-haspopup','true');bt.setAttribute('aria-expanded','false');bt.textContent='🌐 '+name(cur);
  var ul=document.createElement('ul');ul.hidden=true;ul.setAttribute('role','menu');
  C.langs.forEach(function(l){var li=document.createElement('li'),a=document.createElement('a');a.href=U(l[0])+'?lang='+l[0];a.textContent=l[1];a.lang=l[0];a.setAttribute('role','menuitem');
   if(l[0]===cur)a.setAttribute('aria-current','true');a.addEventListener('click',function(e){e.preventDefault();pick(l[0])});li.appendChild(a);ul.appendChild(li);});
  function close(){ul.hidden=true;bt.setAttribute('aria-expanded','false')}
  bt.addEventListener('click',function(e){e.stopPropagation();ul.hidden=!ul.hidden;bt.setAttribute('aria-expanded',String(!ul.hidden))});
  document.addEventListener('click',function(e){if(!b.contains(e.target))close()});
  document.addEventListener('keydown',function(e){if(e.key==='Escape'){close();bt.focus&&!ul.hidden&&bt.focus()}});
  b.appendChild(ul);b.appendChild(bt);document.body.appendChild(b);}}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',mount);else mount();})();"""
    return ('<!-- i18n:switcher --><style data-i18n-sw>' + SWITCHER_CSS + '</style><script data-i18n-skip>'
            + js.replace('__CFG__', json.dumps(cfg, ensure_ascii=False)) + '</script><!-- /i18n:switcher -->')

CC_DEED = dict({'ko': 'deed.ko', 'en': 'deed.en', 'zh': 'deed.zh-hans', 'ja': 'deed.ja', 'uz': 'deed.en', 'ru': 'deed.ru', 'vi': 'deed.vi'}, **CFG.get('ccDeed', {}))
CC_RE = re.compile(r'(https?://creativecommons\.org/licenses/[a-z-]+/\d(?:\.\d)+/)(deed\.[A-Za-z-]+|legalcode(?:\.[A-Za-z-]+)?)?')
def cc_deed(out, L):
    """CC 라이선스 링크를 언어별 deed로 (14-1). legalcode 링크는 그대로."""
    d = CC_DEED.get(L)
    if not d: return out
    return CC_RE.sub(lambda m: m.group(0) if (m.group(2) or '').startswith('legalcode') else m.group(1) + d, out)

def css_var_patch(out, L):
    """fontVars(예: --font, --sans)의 맨 앞에 언어 글꼴을, cssVarFallback(예: vi의 --px)에 대체 글꼴을 첫 글꼴 바로 뒤에 넣는다 (14-2)."""
    f = FONTS.get(L); fam = None
    if f: fam = f['stack'].split(',')[0].strip()
    def first_after(val, add):
        parts = val.split(',', 1)
        return val if add in val else (parts[0] + ',' + add + (',' + parts[1] if len(parts) > 1 else ''))
    for v in CFG.get('fontVars', []):
        if fam: out = re.sub(r'(%s\s*:\s*)([^;}]+)' % re.escape(v), lambda m: m.group(0) if fam in m.group(2) else m.group(1) + fam + ',' + m.group(2), out)
    for v, add in CFG.get('cssVarFallback', {'vi': {'--px': '"IBM Plex Sans"'}}).get(L, {}).items():
        out = re.sub(r'(%s\s*:\s*)([^;}]+)' % re.escape(v), lambda m: m.group(1) + first_after(m.group(2), add), out)
    return out

def post_replace(out, L):
    for a, b in CFG.get('postReplace', {}).get('all', []) + CFG.get('postReplace', {}).get(L, []): out = out.replace(a, b)
    for a, b in CFG.get('postReplaceRegex', {}).get('all', []) + CFG.get('postReplaceRegex', {}).get(L, []): out = re.sub(a, b, out)
    return out

def decorate(out, page, L):
    """언어 속성, hreflang, 글꼴, 줄바꿈, CC deed, 언어 전환을 끼워 넣는다 (원본 HTML은 고치지 않는다)."""
    code = lang_code(L)
    out = re.sub(r'<html\b([^>]*)\blang="[^"]*"', lambda m: '<html%slang="%s"' % (m.group(1), code), out, count=1) if re.search(r'<html\b[^>]*\blang=', out) else out.replace('<html', '<html lang="%s"' % code, 1)
    head_add = ''
    if CFG.get('hreflang', True):
        here = os.path.dirname(out_name(page, L)) or '.'
        href = lambda l: os.path.relpath(out_name(page, l), here).replace(os.sep, '/')
        for l in all_langs(): head_add += '<link rel="alternate" hreflang="%s" href="%s">' % (lang_code(l), href(l))
        head_add += '<link rel="alternate" hreflang="x-default" href="%s">' % href('ko')
    f = FONTS.get(L)
    if f and L != 'ko':
        head_add += '<link rel="stylesheet" href="%s"><style data-i18n-font>%s{font-family:%s}</style>' % (f['css'], CFG.get('fontSelector', 'body,button,input,select,textarea'), f['stack'])
    if L in ('zh', 'ja'):
        head_add += '<style data-i18n-cjk>*{word-break:normal!important;line-break:strict}%s</style>' % ('h1,h2,h3{word-break:auto-phrase!important}' if L == 'ja' else '')
    if head_add: out = out.replace('</head>', head_add + '\n</head>', 1)
    if L != 'ko': out = css_var_patch(cc_deed(out, L), L)
    out = post_replace(out, L)
    if CFG.get('switcher', True) and not any(m in out for m in CFG.get('switcherExistsMarkers', ['i18n:switcher'])):
        sw = switcher_js(page, L); m = re.search(r'<meta\s+charset[^>]*>', out, re.I) or re.search(r'<head[^>]*>', out, re.I)
        out = out[:m.end()] + sw + out[m.end():] if m else sw + out
    return out

def merge(which='all'):
    U, texts = extract_all(save=False)
    report = []
    for L in (LANGS if which == 'all' else [which]):
        tm = load_tm(L); T = {u['id']: tm[tmkey(u)] for u in U.list() if tmkey(u) in tm}
        for page, (t, spans) in texts.items():
            used = {sp[3] for sp in spans if sp[2] != 'data'}
            miss = [u for u in U.list() if u['id'] in used and tmkey(u) not in tm]
            out = decorate(apply(t, spans, U, T, L, page), os.path.join(PROJ, page), L)
            dst = os.path.join(DIST, out_name(os.path.join(PROJ, page), L)); os.makedirs(os.path.dirname(dst), exist_ok=True)
            open(dst, 'w', encoding='utf-8').write(out)
            left, kept = hangul_left(out)
            report.append((L, page, len(miss), left, kept))
    for page, (t, spans) in texts.items():     # 한국어 원본에도 언어 전환·hreflang
        dst = os.path.join(DIST, page); os.makedirs(os.path.dirname(dst), exist_ok=True)
        open(dst, 'w', encoding='utf-8').write(decorate(t, os.path.join(PROJ, page), 'ko'))
    for L, page, miss, left, kept in report: print('merge', L, page, '번역 없음', miss, '마크업에 남은 한글', left, '(의도적으로 남김 %d)' % kept)
    if any(code_blocks(t) for t, _ in texts.values()): codecheck(quiet=True)
    if CFG.get('readme'): merge_readme(which)
    return report

def hangul_left(out):
    """번역판 마크업의 한글 글자 수를 (남은 것, 의도적으로 남긴 것)으로 나눈다.
    의도적: data-i18n-skip 요소의 글, 번역 대상이 아닌 속성(ATTRS 밖, onclick 등), skipStrings, allowVisibleHangul, 언어 메뉴의 '한국어'.
    스크립트·스타일·주석 안은 세지 않는다 (skipCallArgs·skipVars 문자열은 스크립트 안이라 여기서 빠진다)."""
    vis = re.sub(r'<script\b[^>]*>.*?</script>|<style\b[^>]*>.*?</style>|<!--.*?-->', '', out, flags=re.S)
    allow = [re.compile(r) for r in CFG.get('allowVisibleHangul', [])]
    keep_strs = set(CFG.get('skipStrings', [])) | {NATIVE['ko']}
    def split_text(s):
        k = 0
        for x in sorted(keep_strs, key=len, reverse=True): k += len(HANGUL.findall(x)) * s.count(x); s = s.replace(x, '')
        for r in allow:
            for m in r.finditer(s): k += len(HANGUL.findall(m.group(0)))
            s = r.sub('', s)
        return len(HANGUL.findall(s)), k
    left = kept = 0; skip = False
    for m in re.finditer(r'<[^>]+>|[^<]+', vis):
        t = m.group(0)
        if t.startswith('<'):
            nm = re.match(r'</?\s*([a-zA-Z0-9-]+)', t); nm = nm.group(1).lower() if nm else ''
            if nm not in INLINE: skip = 'data-i18n-skip' in t
            for am in re.finditer(r'\s([\w:-]+)="([^"]*)"', t):
                n = len(HANGUL.findall(am.group(2)))
                if not n: continue
                if am.group(1) in ATTRS and 'data-i18n-skip' not in t:
                    a, b = split_text(am.group(2)); left += a; kept += b
                else: kept += n
        elif skip: kept += len(HANGUL.findall(t))
        else:
            a, b = split_text(t); left += a; kept += b
    return left, kept

# ---------- README 7개 언어 조립 (v1.3, 13장) ----------
def readme_path(): return os.path.join(PROJ, CFG.get('readme', 'README.md'))
def index_page():
    ps = [rel(p) for p in pages()]
    want = CFG.get('readmeIndex', 'index.html')
    return want if want in ps else ps[0]

def lang_section():
    idx = index_page(); site = CFG.get('siteUrl', '').rstrip('/')
    link = lambda f: (site + '/' + f) if site else f
    fname = lambda l: out_name(os.path.join(PROJ, idx), l).replace(os.sep, '/')
    pat = '`언어코드/이름.html`' if CFG.get('layout', 'suffix') == 'folder' else '`이름.언어코드.html`'
    rows = ['| %s | `%s` | [바로 보기](%s) |' % (NATIVE[l], fname(l), link(fname(l))) for l in all_langs()]
    return '\n'.join(['## 언어', '',
        '이 시리즈는 한국어 원본과 외국어판 %d개로 볼 수 있다.' % len(LANGS), '',
        '- 고르는 방법: 화면 최상단 메뉴의 🌐 언어 선택 상자나 오른쪽 아래 🌐 배너에서 고른다. 고른 언어는 브라우저에 기억된다.',
        '- 자동 전환: 한국어 페이지에 처음 들어오면, 브라우저 언어가 지원 언어일 때 그 언어판으로 옮겨 간다. 번역판 주소로 들어오면 그대로 연다.',
        '- 주소 끝에 `?lang=en`처럼 붙이면 그 언어로 바로 연다.',
        '- 언어판 파일은 %s 꼴이다.' % pat, '',
        '<!-- i18n:langtable -->', '| 언어 | 파일 이름 | 바로 보기 |', '|---|---|---|'] + rows + ['<!-- /i18n:langtable -->', '', ''])

def readme_source():
    p = readme_path()
    if not os.path.exists(p): print('README 없음:', rel(p)); return None
    t = load(p)
    if CFG.get('readmeLangSection', True) and not re.search(r'^##\s*언어\s*$', t, re.M):
        m = re.search(CFG.get('readmeLangSectionBefore', r'^## '), t, re.M)
        t = t[:m.start()] + lang_section() + t[m.start():] if m else t.rstrip('\n') + '\n\n' + lang_section()
    return t

MD_PREFIX = re.compile(r'^(\s*(?:#{1,6}\s+|>\s*|[-*+]\s+(?:\[[ xX]\]\s+)?|\d+[.)]\s+)*)')
def extract_md(text, U):
    spans, pos, fence, skip = [], 0, False, set(CFG.get('skipStrings', []))
    for line in text.split('\n'):
        st = line.strip()
        if st.startswith('```') or st.startswith('~~~'): fence = not fence
        elif not fence and HANGUL.search(line) and not st.startswith('<!--'):
            if st.startswith('|'):
                for m in re.finditer(r'(?:^|(?<!\\)\|)([^|]*)', line):
                    cell = m.group(1); core = cell.strip()
                    if core and HANGUL.search(core) and core not in skip:
                        a = pos + m.start(1) + (len(cell) - len(cell.lstrip())); spans.append([a, a + len(core), 'md', U.add(core, 'md'), None])
            else:
                pre = MD_PREFIX.match(line).end(); core = line[pre:].rstrip()
                if core and core not in skip: spans.append([pos + pre, pos + pre + len(core), 'md', U.add(core, 'md'), None])
        pos += len(line) + 1
    return spans

def apply_md(text, spans, T):
    out = text
    for s, e, kind, uid, _ in sorted(spans, key=lambda x: -x[0]):
        out = out[:s] + T.get(uid, out[s:e]).replace('\n', ' ') + out[e:]
    return out

def md_links(t, L):
    """이 시리즈의 페이지 링크를 그 언어 파일로 (13-3). 언어 표 안과 다른 시리즈 링크는 그대로."""
    names = [rel(p).replace(os.sep, '/') for p in pages()]; site = CFG.get('siteUrl', '').rstrip('/')
    parts = re.split(r'(<!-- i18n:langtable -->.*?<!-- /i18n:langtable -->)', t, flags=re.S)
    for i in range(0, len(parts), 2):
        x = parts[i]
        for n in sorted(names, key=len, reverse=True):
            ln = out_name(os.path.join(PROJ, n), L).replace(os.sep, '/')
            x = re.sub(r'(\]\((?:\./)?)%s(?=[)#?\s])' % re.escape(n), lambda m: m.group(1) + ln, x)
            if site: x = x.replace(site + '/' + n, site + '/' + ln)
        if site:
            idx = out_name(os.path.join(PROJ, index_page()), L).replace(os.sep, '/')
            x = re.sub(r'%s/?(?=[)\s>]|$)' % re.escape(site), site + '/' + idx, x, flags=re.M)
        parts[i] = x
    return ''.join(parts)

def merge_readme(which='all'):
    if not README_SRC[0]: return
    rt, sp = README_SRC[0]; U = json.load(open(os.path.join(WORK, 'units.json'), encoding='utf-8')); byid = {u['id']: u for u in U}
    order = all_langs(); body = []
    nav = '**' + ' · '.join('[%s](#%s)' % (NATIVE[l], l) for l in order) + '**'
    for L in order:
        if L == 'ko': t = rt; miss = 0
        else:
            tm = load_tm(L); T = {uid: tm[tmkey(byid[uid])] for _, _, _, uid, _ in sp if uid in byid and tmkey(byid[uid]) in tm}
            miss = len({x[3] for x in sp} - set(T)); t = cc_deed(md_links(apply_md(rt, sp, T), L), L)
        body.append('---\n\n<a id="%s"></a>\n\n%s' % (L, t.strip('\n')))
        if L != 'ko': print('merge README', L, '번역 없음', miss)
    os.makedirs(DIST, exist_ok=True)
    open(os.path.join(DIST, 'README.md'), 'w', encoding='utf-8').write(nav + '\n\n' + '\n\n'.join(body) + '\n')
    print('README →', rel(os.path.join(DIST, 'README.md')), '(%d개 언어)' % len(order))

# ---------- 코드 블록 검사 (v1.3) ----------
def code_blocks(html):
    out = []
    for m in re.finditer(r'<script\b([^>]*)>(.*?)</script>', html, re.S):
        if is_code(m.group(1)) and 'data-i18n-skip' not in m.group(1):
            idm = re.search(r'id="([^"]+)"', m.group(1)); out.append((idm.group(1) if idm else '#%d' % len(out), m.group(2)))
    return out

def py_ok(src, run=False, timeout=120):
    """compile, run=True면 임시 폴더에서 실제 실행. (통과 여부, 오류 마지막 줄)."""
    try: compile(src, '<code>', 'exec')
    except SyntaxError as e:
        import html as H
        if '&' in src and H.unescape(src) != src: return py_ok(H.unescape(src), run, timeout)   # HTML 이스케이프해 넣은 코드(&lt;)
        return False, 'SyntaxError: %s (줄 %s)' % (e.msg, e.lineno)
    if not run: return True, ''
    import subprocess, tempfile
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, 'code.py'); open(f, 'w', encoding='utf-8').write(src)
        try: r = subprocess.run([sys.executable, f], cwd=d, capture_output=True, text=True, timeout=timeout, env=dict(os.environ, MPLBACKEND='Agg'))
        except subprocess.TimeoutExpired: return False, '시간 초과 %d초' % timeout
        return r.returncode == 0, (r.stderr.strip().splitlines() or [''])[-1]

def codecheck(run=False, quiet=False):
    """원본(한국어)에서 compile(·실행)되는 코드 블록은 모든 번역판에서도 되어야 한다. 원본에서 안 되는 블록은 건너뛴다."""
    fails = 0; timeout = CFG.get('codeRunTimeout', 120)
    for page in pages():
        ko = dict(code_blocks(load(page)))
        for cid, src in ko.items():
            base, why = py_ok(src, run, timeout)
            if not base:
                if not quiet: print('code', rel(page), cid, '원본도 안 됨 → 건너뜀:', why)
                continue
            for L in LANGS:
                f = os.path.join(DIST, out_name(page, L))
                if not os.path.exists(f): continue
                tr = dict(code_blocks(load(f))).get(cid)
                ok, why = py_ok(tr, run, timeout) if tr is not None else (False, '블록 없음')
                if not ok: fails += 1; print('code FAIL', rel(page), L, cid, why)
                elif not quiet: print('code ok  ', rel(page), L, cid, '실행' if run else 'compile')
    print('codecheck', '실패 %d' % fails if fails else '모두 통과', '(실행 포함)' if run else '(compile만, 실행은 --run)')
    return fails

# ---------- 비용 기록 (v1.2) ----------
COST_COLS = ['lang', 'bundle', 'units', 'src_chars', 'tokens', 'tool_calls', 'model', 'runner', 'date',
             'input_tokens', 'output_tokens', 'cache_write_tokens', 'cache_read_tokens']   # 뒤 4열은 API 실행에서만 채움
def cost_path(): return os.path.join(WORK, 'cost.csv')
def cost_add(L, bundle, tokens, tool_calls, model, runner=None, usage=None, units=None):
    U = units if units is not None else bundle_units(bundle); p = cost_path(); new = not os.path.exists(p)
    row = {'lang': L, 'bundle': os.path.basename(bundle).replace('.json', ''), 'units': len(U), 'src_chars': sum(len(v) for v in U.values()),
           'tokens': int(tokens), 'tool_calls': int(tool_calls), 'model': model, 'runner': runner or RUNNER, 'date': datetime.date.today().isoformat()}
    row.update(usage or {})
    with open(p, 'a', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=COST_COLS)
        if new: w.writeheader()
        w.writerow(row)
    print('cost-add', row['lang'], row['bundle'], row['units'], 'units', row['src_chars'], 'chars', row['tokens'], 'tokens',
          '글자당 %.2f' % (row['tokens'] / max(1, row['src_chars'])))

def cost_summary():
    p = cost_path()
    if not os.path.exists(p): print('비용 기록 없음 (work/cost.csv)'); return
    rows = list(csv.DictReader(open(p, encoding='utf-8')))
    if not rows: print('비용 기록 없음'); return
    agg = {}
    for r in rows:
        a = agg.setdefault(r['lang'], [0, 0, 0, 0]); a[0] += int(r['tokens'] or 0); a[1] += int(r['src_chars'] or 0); a[2] += int(r['tool_calls'] or 0); a[3] += 1
    print('비용 (work/cost.csv)')
    T = [0, 0, 0, 0]
    for L, a in agg.items():
        print('  ', L, '묶음', a[3], '토큰', a[0], '원문', a[1], '자', '글자당 %.2f' % (a[0] / max(1, a[1])), '도구 호출', a[2])
        T = [x + y for x, y in zip(T, a)]
    print('   합계 묶음', T[3], '토큰', T[0], '원문', T[1], '자', '글자당 %.2f' % (T[0] / max(1, T[1])), '도구 호출', T[2])

def stats():
    U = json.load(open(os.path.join(WORK, 'units.json'), encoding='utf-8'))
    from collections import Counter
    print(len(U), 'units', sum(len(u['t']) for u in U), 'chars', dict(Counter(u['ctx'] for u in U)))
    for L in LANGS:
        tm = load_tm(L); sd = load_seeded(L)
        seeded = [u for u in U if tmkey(u) in sd and tmkey(u) in tm]
        print(' ', L, '메모리', len(tm), '남은', sum(1 for u in U if tmkey(u) not in tm),
              '씨앗으로 채움 %d/%d (%.0f%%, %d자)' % (len(seeded), len(U), 100 * len(seeded) / max(1, len(U)), sum(len(u['t']) for u in seeded)))
    cost_summary()

if __name__ == '__main__':
    if len(sys.argv) < 2: print(__doc__); sys.exit(0)
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == 'extract': extract_all()
    elif cmd == 'roundtrip': sys.exit(0 if roundtrip() else 1)
    elif cmd == 'seed': seed()
    elif cmd == 'pending': [pending(L) for L in (LANGS if not args or args[0] == 'all' else args)]
    elif cmd == 'check': check(args[0], args[1], args[2] if len(args) > 2 else None)
    elif cmd == 'retry': retry_all()
    elif cmd == 'check-retry': check_retry(args[0])
    elif cmd == 'merge': merge(args[0] if args else 'all')
    elif cmd == 'cost-add':
        if len(args) < 5: sys.exit('사용: cost-add <L> <묶음> <tokens> <tool_calls> <model>')
        cost_add(*args[:5])
    elif cmd == 'stats': stats()
    elif cmd == 'codecheck': sys.exit(1 if codecheck(run='--run' in args) else 0)
    else: print(__doc__)
