# ahnboat_lab_langpack — 연구실 해설 페이지 번역 스킬과 언어팩

한국어 해설 HTML(`ai-lab-explainer` 페이지, 미션형 시리즈)을 **en · zh · ja · uz · ru · vi** 외국어판과 7개 언어 README로 만드는 번역 스킬과 도구 모음이다. 페이지를 만드는 스킬은 별도 저장소 [`ahnboat_lab_explainer`](https://github.com/adminmrobo/ahnboat_lab_explainer)에 있다.

글 · 안상선 ((주)M-Robo 대표)

**원칙:** 번역 AI에게는 번역할 문장만 보여 준다. 추출·번역 메모리·검사·조립·언어 전환 UI·README 조립·브라우저 검사는 도구가 맡는다. 원본 HTML은 고치지 않는다.

## 하려는 일 → 필요한 파일

| 하려는 일 | 함께 줄 파일 |
|---|---|
| 한국어 페이지의 외국어판 6개 | `SKILL.md` + `langpack/` (+ 미션형이면 `docs/I18N_spec.md`) |
| 번역된 시리즈에 언어 하나만 추가 (예: 베트남어) | 위 + `tasks/TASK_add_lang.md` |
| 도구 사용법만 | `langpack/README.md` |

## 폴더

```
ahnboat_lab_langpack/
├─ SKILL.md                    번역 스킬 본문 (ahnboat-lab-translate)
├─ manifest.json   CHANGELOG.md   LICENSE.md
├─ langpack/                   언어팩 v1.3
│  ├─ langpack.py              extract · roundtrip · seed · pending · check · retry · merge · codecheck · cost-add · stats
│  ├─ api_translate.py         API 직접 번역 (Message Batches · 프롬프트 캐시) — 실제 API 실행은 확인 안 됨
│  ├─ browser_check.js         로컬 서버 · 버튼 모두 누르기 · 언어 전환 11가지 · 스크린샷
│  ├─ config.example.json
│  ├─ rules/                   공통 규칙 · 언어별 규칙 6개 · 코드/README 규칙 · glossary/ 용어표
│  ├─ tm_seed/                 씨앗 번역 메모리 (언어당 760문장, 01 트랜스포머)
│  └─ README.md                도구 사용법 · 설정 키 · 실측 · 알려진 한계
├─ docs/
│  ├─ I18N_spec.md             외국어판 규격 (제작 지시서 8장 · 13~17장)
│  └─ SPEC_langpack_patch_VER1.0.md   언어팩 원 규격
└─ tasks/
   └─ TASK_add_lang.md         언어 하나 추가 (기본값 vi)
```

## 설치

**Claude 스킬** — 저장소를 `ahnboat-lab-translate/` 폴더 이름으로 받으면 맨 위 `SKILL.md`가 스킬 본문이 된다. `SKILL.md`만 스킬로 저장한 경우에는 번역할 때 스킬이 이 저장소를 내려받아 `langpack/`을 쓴다.

**ChatGPT · Gemini · Genspark** — `SKILL.md`, `langpack/` 전체, `docs/I18N_spec.md`를 지식 파일(또는 대화 첨부)로 올린다. 도구를 실행할 수 있는 환경이어야 한다.

## 고정 규칙 요약

- 캐릭터: 박사 · 조수(하루, 예명 세나) · 초파리 연구원 · 주판봇 (주판봇은 언어별 표기(en·uz·vi AbaBot · ja アバボット · zh 算盘宝 · ru АбаБот))
- 저자 이름은 모든 언어에서 **Ahn Sangsun**
- 문체는 부드럽게: 일본어 です・ます체, 우즈베크어 부드러운 설명체와 ʻ(U+02BB)·ʼ(U+02BC)
- 결과는 원어민 검수 전이라고 전달 글에 적는다

## 라이선스

CC BY-NC 4.0 — `LICENSE.md`. 출처 표기 예: `ahnboat_lab_langpack, 안상선 ((주)M-Robo), CC BY-NC 4.0`
