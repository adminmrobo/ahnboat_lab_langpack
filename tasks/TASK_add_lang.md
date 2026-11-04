---
pack: task
id: add-lang
label: 번역된 시리즈에 언어 하나만 더하기 (기본값 vi)
version: 1.1
core_min: 1.9
needs: docs/I18N_spec.md, langpack/ (v1.3) — 이 저장소(ahnboat_lab_langpack)
---

# 작업 팩 · 언어 하나 추가 (`TASK_add_lang`)

이미 몇 개 언어로 번역해 공개한 시리즈에 **언어 하나만** 더한다. 0부는 어떤 언어·시리즈에도 쓰는 일반 절차이고, 1부는 저자가 쓴 **베트남어 추가 보완 지시서**(동작 AI 5-x 시리즈 기준)를 그대로 실은 실행 예다. 1부의 "5-x", "36개", "6개" 같은 값은 그 시리즈의 값이므로 다른 시리즈에서는 0부 입력표의 값으로 바꿔 읽는다.

> 이 저장소에서 "지시서 N장"은 8장·13~17장이면 `docs/I18N_spec.md`의 같은 장, 그 밖의 장은 `ahnboat_lab_explainer`의 `packs/lang/LANG_series_build_instructions.md`를 가리킨다.

## 0-1. 입력

| 항목 | 기본값 | 예 (동작 AI) |
|---|---|---|
| 새 언어 코드 | `vi` | `vi` |
| 이미 있는 언어 | 저장소 파일 이름에서 읽는다 (`*.xx.html`) | en, zh, ja, uz, ru |
| 한국어 원본 파일 목록 | 저장소의 `*.html` 중 언어 코드가 없는 것 | index + 5-1~5-5 (6개) |
| 시리즈 고유 용어표 | `langpack/rules/glossary/20_topic_<시리즈>.json` | 지시서 14-8 |
| 공개 주소 | 언어팩 `config.json`의 `siteUrl` | `https://adminmrobo.github.io/<저장소>/` |
| 언어 순서 | 새 언어는 **맨 끝** | 한국어 · English · 中文 · 日本語 · Oʻzbekcha · Русский · Tiếng Việt |

## 0-2. 원칙 (언어와 상관없이)

1. **원문은 한국어 원본**이다. 다른 번역판을 다시 옮기지 않는다(중역 금지). 다른 번역판은 같은 문자열을 어떻게 처리했는지 참고만 한다.
2. **기존 번역판은 본문을 한 글자도 바꾸지 않는다.** 바뀌는 것은 언어 메뉴, 🌐 배너, 전환 스크립트의 언어 목록, `hreflang` 네 곳뿐이다(1부 4장 표).
3. 바꾸는 방법은 **문자열 치환 또는 같은 번역으로 다시 빌드** 둘 중 하나. 손으로 고치지 않는다. 끝나면 원래 파일과 diff해서 네 곳 밖 차이가 0인지 확인한다.
4. 캐릭터·저자 이름은 언어팩 `00_series.json`을 따른다. **주판봇은 언어별 표기(en·uz·vi AbaBot · ja アバボット · zh 算盘宝 · ru АбаБот)로** 쓴다(ahnboat_lab_explainer 캐릭터 팩 C1).
5. 결과는 **원어민 검수 전**이라고 전달 글에 적는다.

## 0-3. 언어팩 설정에 새 언어 더하기

언어팩 v1.3은 en·zh·ja·ru·uz·vi를 이미 지원한다. 이 여섯 중 하나를 더할 때는 `config.json`의 `langs`에 코드만 더하면 된다. **그 밖의 언어**(예: th, id)는 아래를 모두 채운다.

| 설정·파일 | 할 일 |
|---|---|
| `config.json` `langs` | 코드 추가 (맨 끝) |
| `fonts`, `postReplace` | 그 언어 글자가 있는 글꼴 (Google Fonts) |
| `cssVarFallback` | 픽셀 글꼴 등 글자가 빠질 수 있는 변수에 대체 글꼴 |
| `ccDeed`, `htmlLang` | CC 링크의 언어별 deed, `<html lang>` 값 |
| `models` | 번역 모델 등급 |
| `rules/lang/{코드}.md` | 문체 규칙 (다른 언어 파일과 같은 형식) |
| `rules/glossary/*.json` | 모든 항목에 새 언어 값 |
| `tm_seed/{코드}.json` | 없으면 빈 번역 메모리로 시작 |

## 0-4. 절차

1. 원본에서 언어 UI 블록을 떼고 번역 단위를 뽑는다 → 왕복 검사 → 새 언어만 번역 → 검사 → 조립 (지시서 15장, 1부 2·3장).
2. 기존 번역판의 언어 UI 네 곳에 새 언어를 더한다 (1부 4장).
3. README에 새 언어 절을 맨 끝에 붙이고, 모든 언어 절의 언어 목록·표에 한 줄을 더한다 (1부 5장).
4. 검사 (1부 6장) → 전달 (1부 7장).

---

# 1부 · 실행 예: 베트남어 추가 보완 지시서 (원문)

> v1.0에서 고친 곳: 8장 고정 용어표의 "연구실 로봇"을 주판봇으로 바꾸고(ahnboat_lab_explainer 캐릭터 팩 C1), 언어팩 `00_series.json`에 있는 조수(하루)·세나 행을 더했다. 나머지는 원문 그대로다.

# 보완 지시서 — 기존 6개 언어판에 베트남어(vi)만 추가

이미 공개된 시리즈(한국어 원본 + 영어·중국어·일본어·우즈베크어·러시아어판)에 **베트남어판만 더한다.** 다른 언어의 번역은 다시 하지 않고 한 글자도 바꾸지 않는다. 기존 파일에서 바뀌는 것은 **언어 메뉴·배너·전환 스크립트에 베트남어 항목이 추가되는 것뿐**이다.

기준 문서: 「제작 지시서 — 인터랙티브 교육 HTML 시리즈」(베트남어 반영판). 이 보완서와 다른 내용이 없으며, 세부 규칙은 그 문서의 해당 장을 따른다.

> AI에게 줄 때: 현재 저장소 파일 전체(또는 압축 파일)와 이 보완서를 주고 "이 보완서대로 베트남어만 추가해 줘"라고 요청한다.

---

## 1. 입력과 산출물

**입력**
- 현재 저장소의 HTML 전체: 한국어 6개 + 번역판 30개(`*.en|zh|ja|uz|ru.html`)
- 현재 `README.md`

**산출물**
| 구분 | 파일 | 바뀌는 것 |
|---|---|---|
| 새 파일 | `index.vi.html`, `5-1_….vi.html` … (6개) | 한국어 원본에서 새로 번역 |
| 갱신 | 기존 36개 HTML | 언어 UI에 Tiếng Việt 추가 (본문 변경 없음) |
| 갱신 | `README.md` | 언어 목록·표에 베트남어 추가, 맨 끝에 베트남어 절 추가 |

언어 순서는 어디서나 **한국어 · English · 中文 · 日本語 · Oʻzbekcha · Русский · Tiếng Việt** (베트남어는 맨 끝).

---

## 2. 베트남어 번역

- **원문은 한국어 원본**이다. 영어판을 다시 옮기는 중역은 하지 않는다(영어판은 같은 문자열을 어떻게 처리했는지 참고용으로만 본다).
- 한국어 원본에는 이미 언어 UI(`<style id="i18n-css">`, `<script id="i18n-js">`, `<link rel="alternate">`, `.lang-top`, `#langPick` 배너와 그 스크립트)가 들어 있다. **번역 단위를 뽑기 전에 이 블록들을 떼어 낸다**("한국어", "언어" 같은 UI 글자가 번역 대상에 섞이지 않게).
- 절차는 제작 지시서 15장과 같다: 데이터 가리기 → 번역 단위 뽑기(html·attr·js·code, 태그 자리표시 `<1>…</1>`, 템플릿 식 `${0}`) → 왕복 검사 → 묶음별 번역 → 검사기 → 조립.
- 규칙은 제작 지시서 14장을 따른다. 베트남어에 해당하는 요점:
  - **문체:** 쉽고 친근한 교재체 평서문, 독자는 "bạn". 성조·발음 부호를 빠짐없이(유니코드 NFC). 일상어로 먼저 풀고 괄호에 정식 용어.
  - **같은 한국어 문자열 = 하나의 번역**(JS 비교·객체 키·용어 키가 어긋나지 않게).
  - **이음매:** 숫자 뒤 단위 조각은 앞에 띄어쓰기(`n+' mục'`).
  - **숫자:** 원본 표기 그대로(`6,220,800`, 소수점 `.`) — 화면 숫자와 코드 출력이 어긋나지 않게.
  - **5-4 예외:** 한국어 모델에 넣는 예시 문장·단어 조각·VOCAB/CAPTIONS는 한국어로 두고 처음 나올 때 괄호로 뜻: `"캔을 던진다" (ném lon)`.
  - **용어 사전(GL):** 제목은 `번역어 (English term)` 형식 유지(`Khung bao (Bounding box)`), 키는 본문에 그대로 나오는 가장 짧은 소문자 형태.
  - **Colab 코드:** 주석·docstring·print 문구만 옮긴다.
  - 고정 용어는 아래 8장 표의 vi 열.

## 3. 베트남어 페이지 조립

제작 지시서 14-2와 8장대로:
- `<html lang="vi">`, CC 링크 `deed.ko` → `deed.vi`.
- 글꼴: Google Fonts의 IBM Plex Sans(베트남어 글자 포함)를 `--font`/`--sans` 앞에 추가. 첫 화면의 픽셀 글꼴은 `--px:"Galmuri11","IBM Plex Sans",monospace`처럼 대체 글꼴을 바로 뒤에 둔다(Galmuri에 성조 부호가 없을 수 있음).
- 편끼리 링크(HTML·JS): `5-2_….html` → `5-2_….vi.html`, `index.html` → `index.vi.html`. 다른 시리즈 링크와 절대 주소는 그대로.
- 용어 말풍선: 찾기 정규식에 `'i'` 플래그, 조회도 대소문자 무시.
- 언어 UI(최상단 메뉴 선택 상자 + 🌐 배너 + 전환 스크립트 + hreflang)는 7개 언어로 넣는다. **링크 변환을 먼저, UI 삽입은 나중에.**

## 4. 기존 36개 파일 갱신 (UI만)

본문·번역은 건드리지 않고 아래 다섯 곳만 바꾼다.

| 위치 | 바꾸는 것 |
|---|---|
| `<script id="i18n-js">` | 언어 배열 `L=["ko","en","zh","ja","uz","ru"]`에 `"vi"` 추가 / 파일 이름에서 언어 코드를 떼는 정규식 `(ko\|en\|zh\|ja\|uz\|ru)`에 `vi` 추가 |
| 최상단 메뉴 `.lang-top select` | 맨 끝에 `<option value="vi" lang="vi">Tiếng Việt</option>` |
| 🌐 배너 `#langPick ul` | 맨 끝에 `<li><a href="<파일이름>.vi.html" hreflang="vi" lang="vi" data-l="vi">Tiếng Việt</a></li>` |
| `<head>`의 hreflang | `x-default` 앞에 `<link rel="alternate" hreflang="vi" href="<파일이름>.vi.html">` |
| `<style id="i18n-css">` | 바꾸지 않음 |

- 기존 번역 결과(언어별 번역 JSON)와 빌드 도구가 남아 있으면 언어 목록에 vi를 더해 **전체를 다시 빌드**해도 된다. 같은 번역으로 다시 만들므로 본문은 똑같이 나온다.
- 남아 있지 않으면 위 다섯 곳만 **문자열 치환으로 고친다.** 손으로 고치지 않는다.
- 고친 뒤 원래 파일과 비교(diff)해서 **위 다섯 곳 말고 달라진 줄이 없는지** 확인한다.

## 5. README 갱신

- 맨 위 언어 이동 줄 끝에 ` · [Tiếng Việt](#vi)`.
- **모든 언어 절**의 「언어」 부분에서 언어 나열에 베트남어를 더하고(예: "영어·중국어·일본어·우즈베크어·러시아어·베트남어"), 언어 표에 한 줄 추가:
  `| Tiếng Việt | *.vi.html | https://adminmrobo.github.io/<저장소>/index.vi.html |`
  파일 구조 블록의 `*.uz.html *.ru.html` 줄에 `*.vi.html`을 더한다. 이 밖의 문장은 다시 번역하지 않는다.
- 러시아어 절 뒤에 `---` + `<a id="vi"></a>` + **베트남어 절 전체**를 붙인다(한국어 절을 원문으로 번역). 이 시리즈 링크는 `.vi.html`로, 사이트 주소는 `index.vi.html`로, CC 링크는 `deed.vi`로.

## 6. 검사

**베트남어 페이지 6개**
- [ ] 모든 `<script>`가 구문 오류 없이 파싱된다.
- [ ] 헤드리스 브라우저로 열고 버튼을 모두 눌러 본다: 스크립트 오류 0, 화면·`alt`·`aria-label`에 남은 한국어 0(5-4 예외만).
- [ ] 페이지 안 Colab 코드가 `compile()`과 실제 실행 모두 통과한다(외부 파일이 필요한 코드 제외).
- [ ] 성조 부호가 깨지지 않는다(제목, 첫 화면 픽셀 글꼴, 캔버스 글자). 캔버스 라벨이 넘치지 않는다.
- [ ] 용어 밑줄·말풍선, 용어 표의 "용어/영어" 칸이 정상이다.

**기존 36개 + 전체**
- [ ] diff 결과 바뀐 곳은 4장의 다섯 곳뿐이다.
- [ ] 모든 페이지의 최상단 메뉴와 🌐 배너에 Tiếng Việt가 7번째로 보이고, 누르면 같은 편의 `.vi.html`로 간다.
- [ ] 브라우저 언어가 vi이면 한국어 페이지에서 `.vi.html`로 자동 전환되고, en/zh/ja/uz/ru는 지금처럼 동작한다. `?lang=vi`, 고른 언어 기억, `#섹션` 유지.
- [ ] 휴대폰 폭(390px)에서 가로 넘침이 없다(선택 상자가 한 칸 길어졌으므로 확인).

## 7. 전달

- 기존 36개 파일도 바뀌었으므로 **42개 HTML + README.md를 모두** 저장소 루트에 다시 올린다(폴더 없이).
- 30MB 한도에 맞춰 나눈다: ① 한국어 + en + zh + README ② ja + uz + ru ③ vi.
- 전달 글에 적을 것: 베트남어만 새로 번역했고 다른 언어 본문은 그대로라는 점, 기존 파일은 언어 메뉴만 바뀌었다는 점, 5-4 예외, README 베트남어 절은 맨 끝이라는 점, **원어민 검수 전**.

---

## 8. 고정 용어표 (베트남어)

저자·등장인물·시리즈 고유 용어는 아래 vi 열을 따른다. 그 밖의 기술 용어는 베트남어 표준 용어.

| 한국어 | en | vi |
|---|---|---|
| AI는 동작을 어떻게 알아보고 만들까? (시리즈 제목) | How Does AI Recognize and Create Motion? | AI nhận biết và tạo ra chuyển động như thế nào? |
| 동작 AI (시리즈 약칭) | Motion AI | AI chuyển động |
| 긴급 미션 / 최종 미션 | Emergency mission / Final mission | Nhiệm vụ khẩn cấp / Nhiệm vụ cuối cùng |
| 안상선 ((주)M-Robo 대표) | Ahn Sangsun (CEO, M-Robo Co., Ltd.) | Ahn Sangsun (Giám đốc điều hành, M-Robo Co., Ltd.) |
| 글 · 안상선 | Written by Ahn Sangsun | Tác giả · Ahn Sangsun |
| 박사 | the Doctor | Tiến sĩ |
| 조수 | the Assistant | Trợ lý |
| 조수(하루) | the Assistant (Haru) | Trợ lý (Haru) |
| 세나 (조수의 예명) | Sena | Sena |
| 초파리 연구원 | the Fruit Fly Researcher | Nhà nghiên cứu Ruồi giấm |
| 주판봇 | AbaBot | AbaBot |
| 연구실 (식구들) | the lab (crew) | phòng thí nghiệm (các thành viên) |
| 본부 | HQ | Sở chỉ huy |
| 막대 인형 | stick figure | người que |
| 쓰레기 (무단) 투기 | (illegal) littering / dumping | (lén) vứt rác / xả rác bừa bãi |
| 투기 / 정상 (판정 이름) | Littering / Normal | Xả rác / Bình thường |
| 판정보류 | abstain ("no call") | tạm hoãn phán định |
| 관제실 (라이브 관제실) | control room (live control room) | phòng giám sát (phòng giám sát trực tiếp) |
| 관절 | joint (keypoint) | khớp (điểm mốc) |
| 특징 | feature | đặc trưng |
| 규칙 대 학습 | rules vs. learning | quy tắc và học |
| 헛경보 / 놓침 | false alarm / miss | báo động giả / bỏ sót |
| 판별 모델 / 생성 모델 | discriminative model / generative model | mô hình phân biệt / mô hình sinh |
| 생성기 (A~E) | generator (A–E) | bộ sinh (A–E) |
| 감독관 (채점표) | the Evaluator (score sheet) | Giám khảo (phiếu chấm điểm) |
| 진짜 같음 · 다양성 · 새로움 | realism · diversity · novelty | độ chân thực · độ đa dạng · độ mới |
| 뼈 길이 오차 | bone-length error | sai số độ dài xương |
| 손잡이(잠재 변수) | knob (latent variable) | núm vặn (biến tiềm ẩn) |
| 손잡이 | knob | núm vặn |
| 잠재 지도 / 잠재 공간 | latent map / latent space | bản đồ tiềm ẩn / không gian tiềm ẩn |
| 깔때기 (말 깔때기, 동작 깔때기) | funnel (text funnel, motion funnel) | phễu (phễu chữ, phễu chuyển động) |
| 인코더 · 디코더 | encoder · decoder | bộ mã hóa · bộ giải mã |
| 병목 | bottleneck | nút thắt cổ chai |
| 떨림 / 가림 | jitter / occlusion | rung / che khuất |
| 단어 주머니 | bag of words | túi từ |
| 사전 (조각) | dictionary (pieces) | từ điển (mảnh từ) |
| 짝 맞추기 | pair matching | ghép cặp |
| 대조 학습 | contrastive learning | học tương phản |
| 공유 지도 / 같은 지도 | shared map / the same map | bản đồ chung / cùng một bản đồ |
| 찾기 · 만들기 · 이어 붙이기 | find · make · stitch | tìm · tạo · nối |
| 포즈 맵 | pose map | bản đồ tư thế |
| 참조 이미지 | reference image | ảnh tham chiếu |
| 동작 일치율 | motion match score | tỉ lệ khớp chuyển động |
| 나란히 보기 | side-by-side view | xem song song |
| 교육자를 위한 TIP / 교육자 TIP | Tips for educators / Educator tips | Mẹo cho người dạy / Mẹo giảng dạy |
| 확인 문제 | check questions | câu hỏi kiểm tra |
| 용어 정리 / 용어 사전 | glossary | bảng thuật ngữ |
| 비유 / 비유가 틀리는 지점 | analogy / where the analogy breaks | phép so sánh / chỗ phép so sánh không đúng |
| 레퍼런스 | references | tài liệu tham khảo |
| 설명용 모형인 것 | what is an illustrative mock-up | những gì là mô hình minh họa |
| 코드 1 / 코드 2 | Code 1 / Code 2 | Mã 1 / Mã 2 |
| 복사 · .py 내려받기 · 노트북 내려받기 | Copy · Download .py · Download notebook | Sao chép · Tải .py · Tải notebook |
| 딥러닝 A to Z (3-x 시리즈) | Deep Learning A to Z | Học sâu từ A đến Z |
| AI는 이미지를 어떻게 구분할까? (4-x 시리즈) | How Does AI Tell Images Apart? | AI phân biệt hình ảnh như thế nào? |
| 크리에이티브 커먼즈 저작자표시-비영리 4.0 국제 라이선스(CC BY-NC 4.0) | Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0) | Giấy phép Creative Commons Ghi công – Phi thương mại 4.0 Quốc tế (CC BY-NC 4.0) |
