#!/usr/bin/env python3
"""언어팩 v1.3 — API 직접 번역 (패치 1·5·7). 하위 에이전트 대신 Anthropic API를 부른다.

사용법 (프로젝트 폴더에서, pending 다음에):
  python3 langpack/api_translate.py [<L> ...|all]          work/<L>_00n.json 묶음을 모두 번역 (기본: Message Batches)
  python3 langpack/api_translate.py en --direct            일반 호출(스트리밍)로 바로 번역 (급할 때)
  python3 langpack/api_translate.py en --files en_001.json 특정 묶음만
  python3 langpack/api_translate.py all --fake             API 없이 가짜 응답으로 흐름만 시험
  python3 langpack/api_translate.py retry                  work/retry_00n.json (여러 언어 실패분) 번역 → check-retry

하는 일
  - 시스템 프롬프트 = rules/common.md + rules/lang/<L>.md (규칙 블록에 프롬프트 캐시 지정, 패치 5)
  - 사용자 메시지 = 묶음 JSON (rules 칸은 빼고 보냄)
  - 결과 → work/<L>_00n.out.json, 그다음 langpack.py check를 자동으로 부름
  - usage(입력·출력·캐시 토큰) → work/cost.csv

필요: pip install anthropic, 환경 변수 ANTHROPIC_API_KEY,
      config.json의 apiModels에 실제 모델 문자열 (Anthropic 문서에서 확인해 넣는다. 이 스크립트는 추측해서 채우지 않는다).
상태: 가짜 응답으로만 끝까지 돌려 보았다. 실제 API 실행은 확인 안 됨.
"""
import json, os, re, sys, time, glob, subprocess, signal
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
sys.path.insert(0, PACK)
import langpack as LP   # config.json을 읽고 work 폴더를 정한다

CFG, WORK, LANGS = LP.CFG, LP.WORK, LP.LANGS
TIER_UP = {'haiku': 'sonnet', 'sonnet': 'opus', 'opus': 'opus'}
LANG_NAME = {'en': 'English', 'zh': 'Simplified Chinese', 'ja': 'Japanese', 'ru': 'Russian', 'uz': 'Uzbek (Latin script)', 'vi': 'Vietnamese'}

def model_for(L, retry=False):
    tier = CFG.get('models', {}).get(L, 'sonnet')
    if retry: tier = TIER_UP.get(tier, tier)
    m = CFG.get('apiModels', {}).get(tier, '')
    return tier, m

def system_blocks(L):
    rules = '\n'.join(LP.rules_lines(L, True, True))   # 코드·README 규칙도 늘 넣어 캐시 앞부분을 같게
    tail = ('Translate every unit into %s. Output ONE JSON object {"u0001":"translation", ...} with every id from "units", '
            'and nothing else.' % LANG_NAME.get(L, L))
    # 규칙은 묶음마다 같은 순서로 맨 앞에 → 캐시 지정. 언어마다 다른 꼬리는 캐시 지점 뒤에.
    return [{'type': 'text', 'text': rules, 'cache_control': {'type': 'ephemeral'}}, {'type': 'text', 'text': tail}]

def user_payload(bundle_name):
    objs = [json.load(open(f, encoding='utf-8')) for f in LP.bundle_files(bundle_name)]
    o = {'lang': objs[0].get('lang'), 'glossary': {}, 'hints': {}, 'code': [], 'md': [], 'units': {}}
    for x in objs:
        for k in ('glossary', 'hints', 'units'): o[k].update(x.get(k, {}))
        for k in ('code', 'md'): o[k] += x.get(k, [])
    for k in ('code', 'md'):
        if not o[k]: del o[k]
    return json.dumps(o, ensure_ascii=False, indent=0)

def params(L, bundle_name, retry=False):
    tier, model = model_for(L, retry)
    return {'model': model, 'max_tokens': CFG.get('apiMaxTokens', 32000), 'system': system_blocks(L),
            'messages': [{'role': 'user', 'content': user_payload(bundle_name)}]}, tier

def usage_dict(u):
    g = lambda k: int(getattr(u, k, 0) or 0) if not isinstance(u, dict) else int(u.get(k) or 0)
    d = {'input_tokens': g('input_tokens'), 'output_tokens': g('output_tokens'),
         'cache_write_tokens': g('cache_creation_input_tokens'), 'cache_read_tokens': g('cache_read_input_tokens')}
    d['total'] = sum(d.values()); return d

# ---------- 가짜 클라이언트 (API 없이 흐름 시험) ----------
class FakeMsg:
    def __init__(self, text, usage): self.content = [type('B', (), {'type': 'text', 'text': text})()]; self.usage = usage; self.stop_reason = 'end_turn'
def fake_translate(p):
    units = json.loads(p['messages'][0]['content'])['units']
    out = {k: LP.HANGUL.sub('x', v) for k, v in units.items()}        # 한글 → x (태그·숫자·자리표시 유지)
    txt = json.dumps(out, ensure_ascii=False)
    sys_len = sum(len(b['text']) for b in p['system'])
    usage = {'input_tokens': len(p['messages'][0]['content']), 'output_tokens': len(txt), 'cache_creation_input_tokens': sys_len, 'cache_read_input_tokens': 0}
    return FakeMsg('```json\n' + txt + '\n```', usage)

def text_of(msg):
    return ''.join(getattr(b, 'text', '') for b in msg.content if getattr(b, 'type', '') == 'text')

# ---------- 실행 ----------
def client():
    try: import anthropic
    except ImportError: sys.exit('anthropic 패키지가 없습니다: pip install anthropic')
    if not os.environ.get('ANTHROPIC_API_KEY'): sys.exit('ANTHROPIC_API_KEY 환경 변수가 없습니다.')
    return anthropic.Anthropic()

def run_direct(jobs, fake):
    res = {}
    for cid, (L, name, p, tier) in jobs.items():
        if fake: msg = fake_translate(p)
        else:
            with client().messages.stream(**p) as s: msg = s.get_final_message()   # 긴 출력은 스트리밍 (SDK 시간 제한)
        res[cid] = (text_of(msg), usage_dict(msg.usage), getattr(msg, 'stop_reason', ''))
    return res

def run_batch(jobs, fake):
    if fake: return run_direct(jobs, True)
    c = client()
    b = c.messages.batches.create(requests=[{'custom_id': cid, 'params': p} for cid, (L, name, p, tier) in jobs.items()])
    print('batch', b.id, len(jobs), '건 — 끝날 때까지 기다림 (최대 24시간)')
    json.dump({'id': b.id, 'jobs': {k: [v[0], v[1], v[3]] for k, v in jobs.items()}}, open(os.path.join(WORK, 'api_batch_last.json'), 'w'), ensure_ascii=False)
    while True:
        b = c.messages.batches.retrieve(b.id)
        if b.processing_status == 'ended': break
        print('  ', time.strftime('%H:%M:%S'), b.request_counts); time.sleep(CFG.get('apiPollSeconds', 30))
    res = {}
    for r in c.messages.batches.results(b.id):
        if r.result.type == 'succeeded':
            m = r.result.message; res[r.custom_id] = (text_of(m), usage_dict(m.usage), m.stop_reason)
        else: print('  실패', r.custom_id, r.result.type); res[r.custom_id] = ('', usage_dict({}), r.result.type)
    return res

def collect(argv):
    want = [a for a in argv if not a.startswith('--')]
    files = argv[argv.index('--files') + 1].split(',') if '--files' in argv else None
    if files: want = [w for w in want if w not in files]
    langs = LANGS if not want or want == ['all'] else want
    jobs = {}
    for L in langs:
        names = files or sorted({re.sub(r'\.p\d+\.json$', '.json', os.path.basename(f)) for f in glob.glob(os.path.join(WORK, L + '_*.json'))
                                 if not f.endswith('.out.json')})
        for n in names:
            if not n.startswith(L + '_'): continue
            retry = bool(re.match(r'%s_r\d' % L, n)); p, tier = params(L, n, retry)
            jobs[n[:-5]] = (L, n, p, tier)
    return jobs

def main(argv):
    fake = '--fake' in argv; direct = '--direct' in argv or not CFG.get('apiBatch', True)
    if argv and argv[0] == 'retry': return main_retry(fake, direct)
    jobs = collect(argv)
    if not jobs: print('번역할 묶음이 없습니다 (먼저 langpack.py pending).'); return
    missing = {j[3] for j in jobs.values() if not j[2]['model']}
    if missing and not fake:
        sys.exit('config.json의 apiModels에 %s 모델 문자열을 넣으세요 (Anthropic 문서의 현재 모델 이름 확인).' % ', '.join(sorted(missing)))
    for cid, j in jobs.items():
        if fake and not j[2]['model']: j[2]['model'] = 'fake-' + j[3]
    res = (run_direct if direct else run_batch)(jobs, fake)
    for cid, (txt, u, stop) in res.items():
        L, name, p, tier = jobs[cid]
        out = os.path.join(WORK, cid + '.out.json'); open(out, 'w', encoding='utf-8').write(txt)
        if stop == 'max_tokens': print('  주의', cid, '출력 한도에 걸림 → 빠진 id는 check에서 재시도 묶음이 됨')
        LP.cost_add(L, name, u['total'], 1, p['model'], runner='api' + ('-fake' if fake else '') + ('' if direct else '-batch'), usage={k: u[k] for k in u if k != 'total'})
        LP.check(L, out, name)

def main_retry(fake, direct):
    fs = sorted(f for f in glob.glob(os.path.join(WORK, 'retry_*.json')) if not f.endswith('.out.json'))
    if not fs: print('retry 묶음이 없습니다 (먼저 langpack.py retry).'); return
    f = fs[-1]; tasks = json.load(open(f, encoding='utf-8'))['tasks']; outs = {}
    for L, t in tasks.items():   # 언어별 한 요청 (언어마다 규칙 파일이 다르므로)
        tier, model = model_for(L, retry=True)
        if not model and not fake: sys.exit('apiModels.%s 가 비어 있습니다.' % tier)
        p = {'model': model or 'fake-' + tier, 'max_tokens': CFG.get('apiMaxTokens', 32000), 'system': system_blocks(L),
             'messages': [{'role': 'user', 'content': json.dumps({'lang': L, **t}, ensure_ascii=False, indent=0)}]}
        r = (run_direct if direct else run_batch)({'retry_' + L: (L, f, p, tier)}, fake)['retry_' + L]
        outs[L] = LP.read_out_text(r[0])
        LP.cost_add(L, os.path.basename(f), r[1]['total'], 1, p['model'], runner='api-retry' + ('-fake' if fake else ''),
                    usage={k: r[1][k] for k in r[1] if k != 'total'}, units=t['units'])
        print('retry', L, len(outs[L]), '/', len(t['units']), 'tokens', r[1]['total'])
    out = f[:-5] + '.out.json'; json.dump(outs, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    LP.check_retry(out)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] in ('-h', '--help'): print(__doc__); sys.exit(0)
    main(sys.argv[1:])
