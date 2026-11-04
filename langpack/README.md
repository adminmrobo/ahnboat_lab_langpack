# 언어팩 v1.3 — 한국어 해설 HTML을 6개 언어판으로

global-i18n v2.0 + 언어팩 패치 VER1.0(`docs/SPEC_langpack_patch_VER1.0.md`)을 실제로 돌아가게 만든 도구 묶음입니다.
첫 적용: 「01 트랜스포머 — 형광펜만으로 번역하기」 (2026-11-01, en·zh·ja·ru·uz·vi).

**원칙:** 번역 AI에게는 번역할 문장만 보여 줍니다. 추출·번역 메모리·검사·조립·언어 전환은 도구가 맡습니다.

## 들어 있는 것

| 파일 | 하는 일 |
|---|---|
| `langpack.py` | extract · roundtrip · seed · pending · check · retry · check-retry · merge · codecheck · cost-add · stats (파이썬 3.8+, 외부 패키지 없음) |
| `api_translate.py` | 하위 에이전트 대신 Anthropic API로 번역 (Message Batches, 프롬프트 캐시, 비용 자동 기록). **실제 API 실행은 확인 안 됨** |
| `browser_check.js` | 로컬 서버로 dist/를 띄워 언어 × 페이지 × 390/1280 폭 검사, 버튼 모두 누르기, 언어 전환 시나리오, 스크린샷 (playwright 필요) |
| `config.example.json` | 설정 예시. `config.json`으로 복사해서 씀 |
| `rules/common.md`, `rules/lang/{L}.md` | 번역 AI에게 주는 규칙 (공통 1개 + 언어별 6개) |
| `rules/code.md`, `rules/readme.md` | 코드 줄·README 줄이 든 묶음에만 더하는 짧은 규칙 |
| `rules/glossary/*.json` | 용어표. 폴더의 모든 파일을 합쳐 씀 (00 시리즈 공통 · 10 ML 일반 · 20 주제별) |
| `tm_seed/{L}.json` | 씨앗 번역 메모리 (01 트랜스포머 페이지에서 검사를 통과한 번역, 언어당 760문장). 같은 문장이 다른 페이지에 나오면 다시 번역하지 않음. 맨 앞 `_source`·`_date`는 출처 표시 |
| `docs/SPEC_langpack_patch_VER1.0.md` | 원래 규격 문서 |

## 다른 HTML에 적용하기

```
내 프로젝트/
├─ 02_overfitting.html      ← 한국어 원본 (그대로 둠)
├─ 03_cnn.html
└─ langpack/                 ← 이 묶음을 그대로 복사
```

1. **설정** — `langpack/config.example.json`을 `langpack/config.json`으로 복사하고 `pages`를 고칩니다.
   - 예: `["*.html"]`, `["chapter1/*.html"]`.
   - 원본 HTML은 고치지 않습니다. 결과는 `dist/`에 생깁니다.
2. **추출과 왕복 검사**
   ```
   python3 langpack/langpack.py extract
   python3 langpack/langpack.py roundtrip     # OK가 나와야 다음으로
   python3 langpack/langpack.py seed          # 씨앗 메모리 합치기 (선택, 권장). 번역마다 검사를 거침
   python3 langpack/langpack.py pending all   # → langpack/work/<L>_001.json …
   ```
   - 에이전트 실행에서 묶음 파일이 Read 한도를 넘으면 `<L>_001.p1.json`, `.p2.json` … 조각으로 나뉩니다. 조각들은 **한 묶음**이고 한 에이전트가 모두 읽습니다.
3. **번역** — 묶음 하나당 번역 AI 한 번 (아래 "번역 AI에게 주는 법").
   - 결과는 `langpack/work/<L>_001.out.json`으로 저장합니다(조각이 있어도 출력은 하나).
   - API로 돌리면 `python3 langpack/api_translate.py all`이 번역·검사·비용 기록까지 합니다.
4. **검사**
   ```
   python3 langpack/langpack.py check en langpack/work/en_001.out.json en_001.json
   ```
   - 통과한 번역만 메모리(`work/<L>/tm.json`)에 들어갑니다.
   - 실패한 id만 `work/en_r001.json` 재시도 묶음이 됩니다.
   - 여러 언어의 실패분은 `retry`로 한 묶음에 모아 한 번만 보냅니다.
   - 묶음마다 비용을 적습니다: `python3 langpack/langpack.py cost-add en en_001 <토큰> <도구 호출 수> haiku` → `work/cost.csv`. `stats`가 합계를 보여 줍니다.
     ```
     python3 langpack/langpack.py retry
     python3 langpack/langpack.py check-retry langpack/work/retry_001.out.json
     ```
5. **조립과 브라우저 검사**
   ```
   python3 langpack/langpack.py merge                 # HTML + dist/README.md(7개 언어) + 코드 compile 검사
   python3 langpack/langpack.py codecheck --run       # Colab 코드 블록을 모든 언어에서 실제 실행 (numpy 등 필요)
   node langpack/browser_check.js --shots             # --shots: 캔버스 구역 스크린샷 → langpack/work/shots/
   ```
   - `merge` 출력의 "번역 없음"과 "마크업에 남은 한글"이 0이어야 합니다. 일부러 남긴 한글(`data-i18n-skip`, 번역 대상이 아닌 속성, `skipStrings`, `allowVisibleHangul`)은 "의도적으로 남김"으로 따로 셉니다.
   - 페이지가 `assets/` 같은 바깥 파일을 쓰면 `dist/`에도 복사해 둬야 브라우저 검사가 돕니다(도구는 HTML만 만듭니다).
   - `browser_check.js`가 "모두 통과"로 끝나야 전달합니다.

원본을 고친 뒤에는 2~5를 다시 돌립니다. 번역 메모리는 한국어 문장을 열쇠로 하므로, 바뀐 문장만 묶음에 들어갑니다.

## 번역 AI에게 주는 법 (패치 1)

**코딩 에이전트의 하위 에이전트로 돌릴 때 (v1.2부터 기본: 읽기 1회 → 쓰기 1회)** — 언어마다 하나씩, 동시에.
`inlineRules: true`(기본)이면 규칙이 묶음 파일 맨 앞 `"rules"` 칸에 들어 있어 규칙 파일을 따로 읽지 않습니다.
조각이 없으면 파일 하나, 조각이 있으면 `p1, p2 …`를 모두 적습니다.
```
You are a translator. Do exactly these steps and nothing else:
1. Read each of these files exactly once, in this order (send the Read calls together in one turn if you can):
   langpack/work/{L}_001.json            (or {L}_001.p1.json, {L}_001.p2.json, … when the bundle is split)
   The first file starts with "rules" (follow them). In every file, "units" is the Korean source,
   "glossary" gives fixed translations, "hints" are context only, "code"/"md" list ids that are code lines / README lines.
2. Translate every unit from all files into {언어 이름} following the rules and the glossary.
3. Write ONE file, langpack/work/{L}_001.out.json, containing only a JSON object {"u0001":"translation", ...}
   with every id from all "units".
Do not run commands or scripts, do not re-read files, do not write any other file. After writing the file, reply with just "done".
```
끝나면 에이전트가 보고한 토큰·도구 호출 수를 `cost-add`로 적습니다.

`inlineRules: false`로 둔 경우의 이전 프롬프트(규칙 파일 2개를 따로 읽음):
```
You are a translator. Do exactly these steps and nothing else:
1. Read langpack/rules/common.md
2. Read langpack/rules/lang/{L}.md
3. Read langpack/work/{L}_001.json ("units": Korean source, "glossary": fixed translations, "hints": context only)
4. Translate every unit into {언어 이름} following both rule files and the glossary. Then write ONE file,
   langpack/work/{L}_001.out.json, containing only a JSON object {"u0001":"translation", ...} with every id from "units".
Do not run commands or scripts, do not re-read files, do not write any other file. After writing the file, reply with just "done".
```

**API로 돌릴 때** — `config.json`에서 `"runner": "api"`로 두고 `bundleChars` 키를 지우거나 12000으로 둡니다. `apiModels`에 실제 모델 문자열을 넣습니다(실행 시점의 Anthropic 문서에서 확인. 비워 두면 스크립트가 멈춥니다).
```
pip install anthropic          # ANTHROPIC_API_KEY 환경 변수 필요
python3 langpack/langpack.py pending all
python3 langpack/api_translate.py all          # Message Batches (최대 24시간). 급하면 --direct
python3 langpack/langpack.py retry && python3 langpack/api_translate.py retry
python3 langpack/api_translate.py all --fake   # API 없이 흐름만 시험
```
- 시스템 프롬프트 = 규칙 두 파일(캐시 지정, 패치 5) + 언어 한 줄. 사용자 메시지 = 묶음 JSON.
- 결과의 `usage`(입력·출력·캐시 쓰기·캐시 읽기)가 `work/cost.csv`에 자동으로 들어갑니다.
- 규칙 부분은 약 1,700자입니다. 모델마다 캐시가 걸리는 최소 길이가 있어서, 짧으면 캐시가 걸리지 않을 수 있습니다. `cost.csv`의 `cache_read_tokens`로 확인합니다.

**채팅 AI로 돌릴 때** — 규칙 두 파일 + 묶음 파일을 함께 주고:
```
rules/common.md 와 rules/lang/{L}.md 를 따른다.
묶음 파일 {L}_001.json의 units를 {언어}로 옮겨 {"id":"번역"} JSON 하나만 출력한다.
glossary의 번역을 그대로 쓰고, 태그·자리표시·엔티티·숫자는 그대로 둔다.
```

**재시도 묶음** `retry_001.json`은 `{"tasks":{"ru":{"units":…,"glossary":…}, …}}` 꼴입니다. 출력은 `{"ru":{"u0123":"…"}, …}`입니다.

**모델 배분 (패치 7):**
- en·zh·ja는 가벼운 모델(Haiku급), ru·uz·vi는 중간 모델(Sonnet급)을 씁니다.
- 재시도는 원래보다 한 단계 위 모델로 보냅니다.

## 조립 때 자동으로 넣는 것 (원본은 그대로)

- **언어 전환 (제작 지시서 8장):** `<head>`의 `<meta charset>` 바로 뒤에 작은 스크립트를 넣습니다.
  - 최상단 메뉴의 🌐 선택 상자: `switcherHosts` 순서대로 찾아 붙입니다. 기본은 `#langSw` 안 → `nav.top .brand` 바로 뒤 → `nav .in` → `nav`. 첫 화면의 경보 띠처럼 "버튼 앞"이면 `[".alarm .go","before"]`를 앞에 넣습니다. 아무 데도 없으면 오른쪽 위에 떠 있습니다.
  - 오른쪽 아래 🌐 배너: 현재 언어 이름이 적힌 둥근 버튼. 누르면 7개 언어 목록(현재 언어는 앰버), Esc·바깥 클릭으로 닫힘, 인쇄 때 숨김. 색은 페이지의 `--panel`·`--text`·`--rule`·`--amber` 변수를 따릅니다.
  - 고른 언어를 `localStorage`(`langStorageKey`)에 기억합니다. `?lang=xx`도 기억합니다. `#섹션`은 유지됩니다.
  - **한국어 페이지에서만** 자동 전환: 저장된 언어 → 없으면 브라우저 언어. 지원하지 않는 언어는 한국어 그대로. 번역판 주소로 들어온 사람은 옮기지 않습니다.
  - 404 방지: 옮기기 전에 `HEAD`로 번역 파일이 있는지 확인하고, 없으면 머뭅니다. 확인하는 동안만 화면을 숨기고 2.5초 뒤에는 무조건 보입니다. `file://`로 열면 저장된 선택만 따릅니다.
- **언어별 처리 (14-1, 14-2):**
  - `<html lang>`(zh는 `zh-CN`, `htmlLang`으로 바꿈)과 `hreflang` 링크 7개 + `x-default`(한국어).
  - 글꼴: en·ru·uz·vi는 IBM Plex Sans, zh는 Noto Sans SC, ja는 Noto Sans JP. `fontVars`(예: `["--font","--sans"]`)에 적은 CSS 변수 맨 앞에도 그 글꼴을 넣습니다.
  - `cssVarFallback`: 변수의 첫 글꼴 바로 뒤에 대체 글꼴. 기본은 vi판 `--px`에 `"IBM Plex Sans"` (Galmuri에 성조 부호가 없을 수 있음).
  - CC 라이선스 링크를 언어별 deed로(`ccDeed`, 기본 en·zh-hans·ja·en(uz)·ru·vi). 한국어 원본과 `legalcode` 링크는 그대로.
  - 중·일 줄바꿈: `*{word-break:normal!important;line-break:strict}`, 일본어 제목은 `auto-phrase`.
  - 페이지마다 다른 코드 고치기는 `postReplace`(문자열)·`postReplaceRegex`(정규식)로 합니다. 예: 용어 말풍선 정규식에 `i` 플래그 (14-2)
    ```json
    "postReplaceRegex": {"en": [["new RegExp\\(([^)]*?),\\s*'g'\\)", "new RegExp($1,'gi')"]]}
    ```
    용어 찾기 코드는 페이지마다 달라서 도구가 자동으로 고치지 않습니다. 한 번 맞춰 두면 시리즈 전체에 씁니다.
- **README 7개 언어 (13장):** `readme`(기본 `README.md`)가 있으면 줄 단위로 뽑아 같이 번역하고 `dist/README.md` 하나로 조립합니다.
  - 맨 위 언어 링크 줄, 언어마다 `---` + `<a id="xx">`, 순서 한국어 → English → 中文 → 日本語 → Oʻzbekcha → Русский → Tiếng Việt.
  - 「언어」 절이 없으면 한국어로 만들어 첫 `## ` 제목 앞에 넣습니다(`readmeLangSection`). 고르는 방법·자동 전환·`?lang=`·언어별 파일 표. 표의 주소는 `siteUrl`로 만듭니다.
  - 각 언어 부분에서 이 시리즈 페이지 링크(`5-1_….html`, `siteUrl`)는 그 언어 파일로 바꿉니다. 언어 표의 링크와 다른 시리즈 링크는 그대로. CC 링크는 언어별 deed.
  - 코드 블록(```)은 옮기지 않습니다.
- **Colab 코드 블록 (14-3, 15장):** `<script type="text/plain">`(`codeTypes`) 안의 파이썬은 한글이 든 **줄 하나**씩 번역합니다. 주석·print 문구·독스트링만 옮기고, 검사기가 코드 골격(주석과 문자열 글 밖)과 f-string의 `{…}` 식이 그대로인지 봅니다. 조립 뒤 원본에서 compile되는 블록은 모든 번역판에서도 compile되어야 합니다(`codecheck --run`은 실제 실행까지).
- **지식 색인 꼬리표 (시리즈 2):**
  - `kg-raw` 노드에 `label.{언어}`·`definition.{언어}`를 더합니다.
  - `page-meta`의 `title`·`series` 등은 번역하고, 원문은 `title_ko`로 남깁니다.
  - `kg-ld`·`refs-csl`은 그대로 둡니다.
  - ai-lab-explainer 페이지라면 화면 스크립트가 `label[LANG] → label.en → label.ko` 순으로 읽어야 이름이 바뀝니다.

## 한국어 페이지를 만들 때 지킬 것 (패치 §8)

1. **한 문장 = 템플릿 하나.**
   - `` `검증 정확도는 ${acc}%예요.` `` ○
   - `'검증 정확도는 '+acc+'%예요.'` ✕ (조각으로 쪼개져 어순을 못 바꿉니다)
2. **같은 한국어, 다른 뜻**이면 문자열 바로 앞에 꼬리표를 답니다. 예: `/*i18n:verdict*/'합격'`. 화면은 그대로이고, 번역 메모리에서 따로 관리됩니다.
3. **번역하면 안 되는 칸**
   - 요소: `data-i18n-skip` 속성을 답니다.
   - 스크립트 블록: `<script data-i18n-skip>`.
   - 결과 조회 문자열: 설정 `skipCallArgs`(함수 이름)와 `skipVars`(변수 이름)에 넣습니다.
   - 화면에 일부러 남기는 한글: 설정 `allowVisibleHangul`(정규식)에 넣습니다.
4. 화면 글자는 CSS `content:"…"`에 넣어도 됩니다. 도구가 추출합니다.
5. 숫자 뒤 조사(`${n}개로`)는 템플릿 안에 그대로 둡니다. 번역 AI가 문장 전체를 다시 씁니다.

## 설정 키

| 키 | 기본값 | 뜻 |
|---|---|---|
| `pages` | `["*.html"]` | 원본 HTML 패턴 (projectDir 기준). 번역판·dist는 자동 제외 |
| `projectDir` / `distDir` | `..` / `dist` | 프로젝트 폴더(langpack 기준) / 결과 폴더 |
| `layout` | `suffix` | `suffix` → `이름.en.html`, `folder` → `en/이름.html`. 한 시리즈 안에서 바꾸지 않음 |
| `langs` | 6개 | 만들 언어 |
| `runner` | `agent` | 번역 실행 방식. `agent`(하위 에이전트) / `api`(api_translate.py) |
| `bundleChars` | runner가 agent면 30000, api면 12000 | 묶음 하나의 원문 글자 수. 에이전트는 호출마다 고정비가 커서 묶음을 크게(언어당 1개), API는 고정비가 작아 작게 나눔. 예시 설정에는 30000이 적혀 있으니 API로 바꾸면 이 키를 지우거나 12000으로 |
| `bundleMaxTokens` | 20000 | 에이전트 실행에서 묶음 **파일** 하나의 토큰 상한(어림). 넘으면 같은 묶음을 조각 파일로 나눔. Read 도구 한도(25,000토큰) 아래로 두기 위함 |
| `tokensPerChar` | 0.9 | 파일 글자 수 → 토큰 어림 비율. 실측: 묶음 JSON 62,555자가 53,973토큰(0.86) |
| `inlineRules` | true | 규칙 두 파일을 묶음 파일 맨 앞 `"rules"` 칸에 넣음(에이전트 실행만). 읽기 3회 → 1회 |
| `apiModels` / `apiMaxTokens` / `apiBatch` | 빈칸 / 32000 / true | api_translate.py: 등급(haiku·sonnet·opus)별 실제 모델 문자열, 출력 한도, Batches 사용 |
| `hintMaxLen` / `hintChars` | 20 / 30 | 이 길이보다 짧은 단위에만 앞뒤 문맥 30자 |
| `metaFields` | title, series, suggestedCitation, todo | page-meta에서 번역할 칸 |
| `skipStrings` / `skipCallArgs` / `skipVars` | `["한국어"]` / [] / [] | 번역하지 않을 문자열·함수 인자·변수 |
| `allowVisibleHangul` | [] | 검사에서 허용할 한글 (정규식) |
| `switcher` / `autoRedirect` / `hreflang` | true | 언어 전환·자동 이동·대체 링크 넣기 |
| `menuSelect` / `banner` | true / true | 최상단 🌐 선택 상자 / 오른쪽 아래 🌐 배너 |
| `switcherHosts` | 위 참고 | 선택 상자를 붙일 곳 `[선택자, append·after·before]` 목록 |
| `langStorageKey` | `i18n_lang` | 고른 언어를 기억하는 키. 시리즈마다 다르게 둘 수 있음(예: `motion_ai_lang`) |
| `htmlLang` | `{"zh":"zh-CN"}` | `<html lang>`·hreflang 코드 |
| `switcherExistsMarkers` | | 이미 전환 장치가 있는 페이지 표시 (있으면 넣지 않음) |
| `fonts` / `fontSelector` / `fontVars` / `cssVarFallback` | | 언어별 글꼴, 글꼴을 앞에 넣을 CSS 변수, 대체 글꼴 |
| `ccDeed` | 위 참고 | 언어별 CC deed |
| `postReplace` / `postReplaceRegex` | {} | 조립 후 문자열·정규식 치환 (`all` 또는 언어별) |
| `codeTypes` / `codeRunTimeout` | `["text/plain"]` / 120 | 코드 블록으로 볼 script type, `codecheck --run` 시간 한도(초) |
| `readme` / `readmeLangSection` / `readmeIndex` / `siteUrl` | `README.md` / true / `index.html` / "" | README 조립. 끄려면 `"readme": ""` |
| `maxClicks` / `shotsPerPage` | 300 / 4 | browser_check: 페이지당 누를 버튼 수, 스크린샷 수 |

## 검사 기준 (`check`)

- 빠진 id가 없어야 합니다.
- 한글이 남으면 안 됩니다(태그 속성 안은 제외 — 조립 때 따로 번역).
- 자리표시 `{n}`, 태그, 엔티티가 원문과 같아야 합니다.
- 앞뒤 공백이 원문과 같아야 합니다(중·일 제외).
- 숫자가 원문과 같아야 합니다. 다음은 오탐을 막으려고 맞춰서 비교합니다.
  - `4만`=40,000, `2만 4천`=24,000.
  - 대상 언어 쪽 `40k`, `4.5 million`, `млн`, `triệu`, `万`도 환산합니다.
  - `1차`·`2등` 같은 서수는 빼고 비교합니다.
  - 1~10을 낱말로 쓴 경우(네 캐릭터 → 4人)는 허용합니다.
- 깨진 JSON은 줄 단위로 복구합니다.

## 실측 (01 트랜스포머, v1.0 실행, 2026-11-01)

| 항목 | 값 |
|---|---|
| 번역량 | 774단위 · 26,237자 × 6개 언어, 언어당 묶음 1개 (bundleChars 30000) |
| 호출 | 하위 에이전트 6회 (en·zh·ja Haiku급, ru·uz·vi Sonnet급), 에이전트마다 도구 호출 5~12회 |
| 토큰 | 합계 1,026,821, 원문 글자당 6.52 |
| 분해 (추정) | 고정비 약 5.1만 × 6회 ≈ 30.6만, 변동 약 72.1만 → 글자당 변동 4.58 |
| 첫 회 검사 | 6개 언어 모두 770/774. 실패 4건은 원본 잔여 태그 탓, 재번역 0 |

묶음 크기 비교 (번역 없이 en 기준)

| | v1.0 | v1.1 (bundleChars 15000) | v1.1 (bundleChars 30000) |
|---|---|---|---|
| 묶음 수 | 1 | 2 | 1 |
| 묶음 파일 글자 합 | 66,667 | 57,926 | 56,702 |
| hints 글자 | 28,502 | 18,101 | 18,101 |

**결론:** 문맥을 줄여도 글자당 변동 비용은 줄지 않았습니다. 에이전트 실행에서는 묶음 하나마다 고정비(약 5만 토큰)가 붙으므로, 묶음 수를 늘리면(v1.1의 1만 5천 자) 언어당 약 5만, 6개 언어 합계 약 30만 토큰이 늘어납니다. 문맥 축소로 줄어드는 몫(입력 약 −15%)보다 큽니다. 그래서 v1.2는 에이전트 실행의 묶음을 다시 3만 자로 둡니다.

**Read 한도 실측 (v1.2, 번역 없음):** 묶음 JSON 62,555자 = 53,973토큰(글자당 0.86). Read 도구는 한 번에 25,000토큰까지 읽으므로, 묶음 파일 하나는 약 2만 9천 자까지 한 번에 읽힙니다. 그래서 원문 약 1만 자보다 큰 묶음은 조각 파일로 나뉘고, 에이전트의 읽기 호출은 조각 수만큼 듭니다(예: 원문 2만 6천 자 → 조각 3개 → 읽기 3 + 쓰기 1). "에이전트당 도구 호출 2회"는 원문 약 1만 자 이하의 묶음에서만 됩니다.

**아직 재 보지 않은 것:** v1.2로 실제 번역했을 때의 토큰·도구 호출 수, 그리고 API 실행(`api_translate.py`)의 글자당 토큰(규격 문서 추정 1.5~2). 다음 번역 때 `cost-add`로 기록하고 `stats`로 비교합니다. 비교 기준은 위 v1.0 수치(글자당 6.52, 변동 4.58)입니다.

**원어민 검수 전**이라는 점을 전달 글에 적습니다. 특히 uz·ru·vi는 문법 일치, ʻ ʼ 표기, 성조를 확인합니다.

## 알려진 한계

- **스크립트 문자열 찾기:** 정규식 리터럴과 나눗셈을 문맥으로 구분합니다. 아주 특이한 코드에서는 `roundtrip`이 FAIL로 알려 줍니다. 그때는 그 부분을 `<script data-i18n-skip>`으로 빼거나 알려 주세요.
- **인라인 이벤트 문자열:** `onclick="alert('…')"` 같은 문자열은 추출하지 않습니다.
- **API 번역:** `api_translate.py`는 가짜 응답(`--fake`)으로만 끝까지 돌려 보았습니다. 실제 API 실행은 확인 안 됨. 기대 효과(호출당 고정비 약 5만 → 약 1천 토큰, 글자당 1.5~2토큰)는 규격 문서의 **추정**입니다.
- **바깥 스크립트의 한글:** 페이지가 `assets/lab.js`처럼 바깥 JS 파일에서 화면 글자를 만들면 그 글자는 번역되지 않습니다(추출 대상은 HTML 파일 하나). 이런 페이지는 브라우저 검사에서 한글이 남습니다.
- **편끼리 링크 변환은 하지 않습니다(HTML).** 번역판의 `5-2_….html` 링크는 한국어판을 가리킵니다. 언어 전환 스크립트가 기억된 언어로 다시 옮겨 주므로 화면에서는 같은 언어로 이어지지만, 한 번 한국어 주소를 거칩니다. README 안의 링크는 바꿉니다.
- **언어 자체를 다루는 실습(14-5):** 한국어로 남겨야 하는 데이터 배열은 `skipVars`·`data-i18n-skip`으로 빼고, 화면에 괄호로 뜻을 붙이는 것은 원본에서 합니다. 코드 블록 안의 그런 데이터 줄은 줄째 `skipStrings`에 넣습니다.
- **코드 실행 검사:** `codecheck --run`은 이 컴퓨터에 설치된 라이브러리로 돌립니다(Colab과 다를 수 있음). 원본에서 실행되지 않는 블록(영상 파일이 필요한 코드 등)은 건너뜁니다.
- **씨앗 메모리 검사:** `seed`는 형식 검사(한글·태그·자리표시·숫자)만 합니다. 같은 문장이 다른 페이지에서 다른 뜻으로 쓰였는지는 알 수 없습니다. 그런 문장은 `/*i18n:문맥*/` 꼬리표로 따로 관리합니다.

## 바뀐 점

**v1.3 (2026-11-01)** — 제작 지시서(인터랙티브 교육 HTML 시리즈) 2~5항 반영
- Colab 코드 블록(`<script type="text/plain">`): 한글이 든 줄 단위로 번역, 코드 골격·f-string 식 검사, `rules/code.md`, `codecheck [--run]`(원본에서 되는 블록만 모든 언어에서 compile·실행). 이전에는 파이썬 주석이 뽑히지 않았음.
- 언어 전환: `<head>`에 넣는 스크립트로 바꿈. 🌐 선택 상자(`switcherHosts`) + 오른쪽 아래 🌐 배너, 고른 언어 기억, `HEAD` 확인 404 방지(2.5초 안전장치), 번역판 주소는 자동 전환 안 함, hreflang `zh-CN`·`x-default`, `<html lang="zh-CN">`.
- 언어별 처리: CC deed, `fontVars`, `cssVarFallback`(vi `--px`), `postReplaceRegex`, 중·일 줄바꿈을 `*` 전체로.
- README 7개 언어 조립: 줄·표 칸 단위 번역(`rules/readme.md`, 링크·코드 조각 검사), 「언어」 절 자동 생성, 시리즈 링크·CC deed 언어별 변환.
- browser_check: 로컬 http 서버, 버튼 모두 누른 뒤 한글 검사, `alt`·`aria-label`·`title`·`placeholder` 한글 검사, 🌐 상자·배너 보임, 전환 시나리오 11가지(선택 상자·#섹션, 기억, 배너·Esc, 브라우저 언어 6개 + de, `?lang=`, 번역판 주소, 404), `--shots`.
- 캐릭터 표기 정리: 박사 · 조수(하루, 예명 세나) · 초파리 연구원 · 주판봇. 규칙 파일 7개를 "조수(하루)"로 바꾸고, 용어표에 `조수(하루)`·`세나`를 더함(기존 용어는 그대로). 우즈베크어 초파리 연구원은 공개판과 같은 Meva pashshasi tadqiqotchisi.
- JS 문자열 속 이스케이프(`\n` 등)가 조립 때 두 겹(`\\n`)이 되던 결함을 바로잡음(v1.1부터 있던 것, 트랜스포머 페이지에는 그런 문자열이 없어 드러나지 않았음). `check`가 이스케이프가 그대로인지도 봄. 코드 블록을 HTML 이스케이프(`&lt;`)해 넣은 페이지도 `codecheck`가 풀어서 검사.
- `| head`로 잘라도 명령이 끝까지 돎. v1.2의 SIGPIPE 처리는 프로세스를 조용히 끝내서 `pending all | head`가 첫 언어 묶음만 쓰고 멈췄음 — 바로잡음.

**v1.2 (2026-11-01)**
- 묶음 크기 기본값을 되돌림: `runner`가 `agent`면 30000자, `api`면 12000자. v1.1의 15000자는 에이전트 실행에서 묶음 수를 2배로 만들어 고정비가 더 늘었음(판단 착오).
- 에이전트 묶음 파일이 Read 한도를 넘으면 같은 묶음을 조각(`.p1`, `.p2` …)으로 나눔(`bundleMaxTokens`, `tokensPerChar`). 한 에이전트가 조각을 모두 읽고 출력은 하나.
- `inlineRules`: 규칙 두 파일을 묶음 파일 맨 앞에 넣어 규칙 읽기 2회를 없앰. README에 "읽기 1회 → 쓰기 1회" 에이전트 프롬프트 추가.
- `api_translate.py` 추가: Message Batches, 규칙 블록 프롬프트 캐시, `check` 자동 호출, `usage`를 `cost.csv`에 기록, `--fake` 시험 모드. 실제 API 실행은 확인 안 됨.
- `cost-add` 명령과 `stats`의 비용 합계(토큰, 글자당 토큰, 도구 호출 수). `cost.csv` 열: `lang,bundle,units,src_chars,tokens,tool_calls,model,runner,date` (+ API 실행 때 입력·출력·캐시 토큰 4열).
- 씨앗 메모리: 출처 표시(`_source`, `_date`) 추가, `seed`가 `_` 열쇠를 건너뛰고 번역마다 검사를 거침, `stats`가 "씨앗으로 채움 n/전체"를 보여 줌. 기존 번역은 그대로.
- `merge`가 일부러 남긴 한글을 "의도적으로 남김 n"으로 따로 셈.
- `browser_check.js`: 언어 전환 시험이 `#top` 대신 페이지의 첫 `[id]` 요소를 씀.
- `| head`로 출력을 잘라도 BrokenPipe 오류가 나지 않게 함(SIGPIPE). → v1.3에서 바로잡음.

**v1.1** — 스크립트 문맥 축소, 씨앗 메모리, folder 배치·`/*i18n:문맥*/` 꼬리표·`skipCallArgs`·`skipVars`·CSS `content` 지원.
