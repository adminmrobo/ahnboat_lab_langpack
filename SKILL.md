---
name: ahnboat-lab-translate
description: 한국어 해설 HTML(ai-lab-explainer 페이지·미션형 시리즈)을 언어팩으로 en·zh·ja·uz·ru·vi 외국어판과 7개 언어 README로 만들거나, 번역된 시리즈에 언어 하나를 더할 때 쓴다.
---

# 연구실 해설 페이지 번역 (ahnboat-lab-translate)

한국어 해설 HTML을 **언어팩(langpack)**으로 6개 외국어판으로 옮긴다. 번역 AI에게는 번역할 문장만 보여 주고, 추출·번역 메모리·검사·조립·언어 전환 UI·README 조립·브라우저 검사는 도구가 맡는다. 원본 HTML은 고치지 않는다.

- 도구·규칙 저장소: https://github.com/adminmrobo/ahnboat_lab_langpack (공개)
- 페이지를 만드는 스킬: `ai-lab-explainer` (저장소 `adminmrobo/ahnboat_lab_explainer`)
- 글 · 안상선 ((주)M-Robo 대표) · CC BY-NC 4.0

## 1. 도구 가져오기

작업 폴더(한국어 HTML이 있는 곳)에서:

```
git clone --depth 1 https://github.com/adminmrobo/ahnboat_lab_langpack /tmp/ahnboat_lab_langpack
cp -r /tmp/ahnboat_lab_langpack/langpack ./langpack
```

- 내려받기가 막혀 있으면 사용자에게 저장소 zip(또는 `langpack/` 폴더)을 첨부해 달라고 한다. 도구를 기억으로 다시 쓰지 않는다.
- 필요한 것: python3(외부 패키지 없음), 브라우저 검사에 node + playwright, `codecheck --run`에 페이지 코드가 쓰는 라이브러리(numpy 등).
- 도구 사용법 전체는 `langpack/README.md`, 외국어판 규격(언어 전환 UI·README·번역 범위·용어표·검사)은 저장소 `docs/I18N_spec.md`.

## 2. 시작 전에 확인할 것 (빠진 것만 한 번에 묻는다)

| 항목 | 기본값 |
|---|---|
| 한국어 원본 HTML (+ README.md) | 사용자가 첨부하거나 저장소 주소를 준다 |
| 만들 언어 | en, zh, ja, uz, ru, vi |
| 공개 주소 `siteUrl` | `https://adminmrobo.github.io/<저장소>/` |
| 언어 기억 키 `langStorageKey` | 시리즈 약칭 + `_lang` (예: `motion_ai_lang`) |
| 시리즈 고유 용어표 | 미션형 시리즈면 그 지시서의 14-8 표 → `langpack/rules/glossary/20_topic_<시리즈>.json` |
| 언어 하나만 더하기인가 | 그렇다면 저장소 `tasks/TASK_add_lang.md`를 따른다 (기본 vi) |

## 3. 순서

1. **설정**: `langpack/config.example.json` → `langpack/config.json`. `pages`, `langs`, `siteUrl`, `langStorageKey`, `readme`를 채운다.
   - 미션형 첫 화면은 `switcherHosts` 맨 앞에 `[".alarm .go","before"]`, 각 편은 기본값(`nav.top .brand` 뒤).
   - 글꼴 변수를 쓰는 페이지는 `"fontVars": ["--font","--sans"]`.
2. **추출과 왕복 검사**
   ```
   python3 langpack/langpack.py extract
   python3 langpack/langpack.py roundtrip      # OK가 아니면 멈추고 원인을 알린다
   python3 langpack/langpack.py seed
   python3 langpack/langpack.py pending all
   ```
3. **번역**: 언어마다 하위 에이전트 하나, 동시에. en·zh·ja는 Haiku급, ru·uz·vi는 Sonnet급. 묶음은 언어당 하나(3만 자)이고, 파일이 크면 `.p1 .p2 …` 조각으로 나뉜다. 에이전트 프롬프트(조각이 있으면 파일을 모두 적는다):
   ```
   You are a translator. Do exactly these steps and nothing else:
   1. Read each of these files exactly once, in this order (send the Read calls together in one turn if you can):
      langpack/work/{L}_001.json   (or {L}_001.p1.json, {L}_001.p2.json, … when the bundle is split)
      The first file starts with "rules" (follow them). In every file, "units" is the Korean source,
      "glossary" gives fixed translations, "hints" are context only, "code"/"md" list ids that are code lines / README lines.
   2. Translate every unit from all files into {language} following the rules and the glossary.
   3. Write ONE file, langpack/work/{L}_001.out.json, containing only a JSON object {"u0001":"translation", ...}
      with every id from all "units".
   Do not run commands or scripts, do not re-read files, do not write any other file. After writing the file, reply with just "done".
   ```
   API 키가 있으면 `config.json`의 `runner`를 `api`로 두고 `python3 langpack/api_translate.py all`(모델 문자열은 Anthropic 문서에서 확인해 `apiModels`에 넣는다).
4. **검사와 재시도**
   ```
   python3 langpack/langpack.py check {L} langpack/work/{L}_001.out.json {L}_001
   python3 langpack/langpack.py retry          # 남은 실패분을 모든 언어 한 묶음으로 → 한 단계 위 모델로 한 번
   python3 langpack/langpack.py check-retry langpack/work/retry_001.out.json
   python3 langpack/langpack.py cost-add {L} {L}_001 <토큰> <도구 호출 수> <모델>
   ```
5. **조립과 검사**
   ```
   python3 langpack/langpack.py merge          # HTML 번역판 + dist/README.md(7개 언어) + 코드 compile
   python3 langpack/langpack.py codecheck --run
   node langpack/browser_check.js --shots
   ```
   - `merge`의 "번역 없음"과 "마크업에 남은 한글"은 0이어야 한다("의도적으로 남김"은 괜찮다).
   - 페이지가 `assets/` 같은 바깥 파일을 쓰면 `dist/`에 복사한 뒤 브라우저 검사를 한다.
   - `browser_check.js`가 "모두 통과"로 끝나야 전달한다. 스크린샷(`langpack/work/shots/`)으로 캔버스 글자 넘침을 몇 곳 눈으로 본다.
6. **전달**: `dist/`의 파일을 폴더 없이(저장소 루트에 그대로 올릴 수 있게) 묶는다. 사용자가 시키면 저장소 새 브랜치에 커밋하고 PR을 연다. main에 바로 넣지 않는다.

## 4. 고정 규칙

- **캐릭터 표기**: 박사 · 조수(하루, 예명 세나) · 초파리 연구원 · 주판봇 · 인턴 시아·모아. 주판봇은 언어별 표기(en·uz·vi AbaBot · ja アバボット · zh 算盘宝 · ru АбаБот). 우즈베크어 초파리 연구원은 Meva pashshasi tadqiqotchisi. 연구실 로봇이라고 쓰지 않는다.
- **저자 이름**은 모든 언어에서 **Ahn Sangsun** (한자·가타카나·키릴 문자로 옮기지 않는다).
- **문체는 부드럽게**: 일본어는 です・ます체(である체 아님), 우즈베크어는 부드러운 설명체(siz)와 ʻ(U+02BB)·ʼ(U+02BC), 베트남어는 성조 부호를 빠짐없이.
- 숫자·코드·URL·고유명·태그·자리표시는 그대로. 숫자를 낱말로 풀지 않는다.
- 원어민 검수 전이라는 점을 전달 글에 적는다(특히 uz·ru·vi).
- 용어표·씨앗 메모리의 기존 번역은 사용자가 정한 규칙(위 표기 등)과 맞지 않을 때만 고치고, 고친 곳을 알린다.

## 5. 언어팩이 하지 않는 것 (알리고, 필요하면 원본에서 처리)

- **편끼리 링크 변환(HTML)**: 번역판의 다른 편 링크는 한국어 파일을 가리킨다. 언어 전환 스크립트가 기억된 언어로 다시 옮겨 준다. README 안의 링크는 바꾼다.
- **용어 말풍선의 대소문자 무시(`i` 플래그)**: 페이지 코드에 맞춰 `postReplaceRegex`로 정한다.
- **언어 자체를 다루는 실습(규격 14-5)**: 한국어로 남길 데이터는 `skipVars`·`data-i18n-skip`·`skipStrings`로 뺀다.
- **바깥 스크립트(`assets/*.js`)의 화면 글자**는 번역되지 않는다. 브라우저 검사에서 한글로 드러난다.
- 실제 번역 비용(토큰)은 `cost-add`로 적은 것만 숫자로 말한다. 추정은 "추정"이라고 쓴다.
