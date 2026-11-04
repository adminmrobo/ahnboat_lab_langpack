---
doc: i18n-spec
label: 외국어판 규격 — 언어 전환 UI · README · 외국어판 HTML 규칙 · 제작 절차 · 검사 · 전달
version: 1.1
source: ahnboat_lab_explainer packs/lang/LANG_series_build_instructions.md 8장, 13~17장 (장 번호는 원문 그대로)
---

# 외국어판 규격 (I18N spec)

미션형 시리즈 제작 지시서에서 번역에 관한 장만 옮겨 온 것이다. 장 번호는 원문 그대로 두어, 본 스킬 저장소의 지시서와 같은 번호로 서로 가리킨다. 기획·디자인·페이지 구조(0~7장, 9~12장)는 `ahnboat_lab_explainer`의 지시서에 있다.

이 저장소에서 바꾼 곳:
- 14-8 고정 용어표의 저자 이름을 모든 언어에서 **Ahn Sangsun**으로(한자·가타카나·키릴 문자로 옮기지 않는다).
- 캐릭터 표기 박사 · 조수(하루, 예명 세나) · 초파리 연구원 · 주판봇, 일본어 です・ます체, 우즈베크어 ʼ(U+02BC)는 원문(2026-11-01판)에 이미 반영돼 있다.

## 8. 언어 전환 UI (한국어 원본에도 넣는다)

모든 페이지에 두 가지를 **함께** 넣는다.

1. **최상단 메뉴의 언어 선택 상자** `🌐 [언어 ▾]`
   - 각 편: `nav.top`의 제목(brand) 바로 옆.
   - 첫 화면: 경보 띠의 "미션 보기" 버튼 앞.
2. **오른쪽 아래 🌐 배너**: 화면 오른쪽 아래 고정 둥근 버튼(현재 언어 이름). 누르면 7개 언어 목록, 현재 언어는 앰버. Esc·바깥 클릭으로 닫힘. 인쇄 시 숨김.

언어 순서와 표시 이름: 한국어 · English · 中文 · 日本語 · Oʻzbekcha · Русский · Tiếng Việt

### 전환 동작 (`<head>`의 `<meta charset>` 바로 뒤에 넣는 작은 스크립트)
- 저장 키 하나(예: `motion_ai_lang`)를 `localStorage`에 쓴다. 메뉴·배너에서 고르면 저장하고 같은 페이지의 그 언어 파일로 이동(`#섹션` 유지).
- `?lang=xx`가 있으면 저장하고 그 언어로 연다.
- **한국어 페이지에서만** 자동 전환: 저장된 언어, 없으면 브라우저 언어(`navigator.languages` 앞 두 글자)가 지원 언어면 이동. 지원하지 않는 언어는 한국어 그대로.
- **404 방지**: 이동 전에 `fetch(…, {method:'HEAD'})`로 번역 파일이 있는지 확인하고 없으면 머문다. 확인하는 동안만 화면을 숨기고 2.5초 뒤에는 무조건 보인다. `file://`로 열었을 때는 저장된 선택만 따른다.
- 번역판 주소로 들어온 사람은 자동 전환하지 않는다(공유한 영어 링크는 영어로 열린다).
- 각 파일에 `<link rel="alternate" hreflang="ko|en|zh-CN|ja|uz|ru|vi|x-default">`.

---

## 13. README.md

### 한국어 부분 (원본)
제목 → 한 문단 소개 → **바로 보기** 주소 → 저자 → **언어**(13-2) → 구성(편 표: 편 · 제목 · 다루는 내용 · 난이도) → 막대 인형이 걸어온 길(들어가는 것 · 나오는 것 · 다음 질문) → 각 편의 핵심 숫자 → 각 편에 들어 있는 것 + 주요 실습 표 → Colab 코드 표(코드1 · 코드2 · 라이브러리 · 실행 시간) → 파일(구조 블록 + 크기 표) → 먼저 읽으면 좋은 편 → 데이터와 이미지(설명용 모형 표) → 용어 표기 → 라이선스(출처 표기 예).

### 13-2. 「언어」 절
- 고르는 방법(최상단 메뉴의 🌐 선택 상자, 오른쪽 아래 🌐 배너, 고른 언어 기억), 자동 전환, `?lang=`
- 언어 예외가 있는 편(예: 5-4)
- 표: 언어 · 파일 이름 · 바로 보기 주소(`index.en.html` …)
- 파일 구조 블록에 `*.en.html *.zh.html *.ja.html` / `*.uz.html *.ru.html *.vi.html` 줄 추가

### 13-3. 다국어 README 조립
- 맨 위: `**[한국어](#ko) · [English](#en) · [中文](#zh) · [日本語](#ja) · [Oʻzbekcha](#uz) · [Русский](#ru) · [Tiếng Việt](#vi)**`
- `---` + `<a id="ko"></a>` + 한국어 전체 → 영어 → 중국어 → 일본어 → 우즈베크어 → **러시아어 → 베트남어(러시아어·베트남어는 지정 순서 밖이라 맨 끝)**.
- 각 언어 부분의 이 시리즈 링크는 그 언어 파일로(`5-1_….html` → `5-1_….en.html`, 사이트 주소 → `index.en.html`). 다른 시리즈 링크와 언어 표의 링크는 그대로. CC 링크는 언어별 deed.

---

## 14. 외국어판 HTML 규칙

### 14-1. 언어

| 코드 | 언어 | 표시 이름 | `<html lang>` | 추가 글꼴 | CC deed |
|---|---|---|---|---|---|
| `ko` | 한국어 (원본) | 한국어 | `ko` | — | `deed.ko` |
| `en` | 영어 | English | `en` | IBM Plex Sans | `deed.en` |
| `zh` | 중국어 간체 | 中文 | `zh-CN` | Noto Sans SC | `deed.zh-hans` |
| `ja` | 일본어 | 日本語 | `ja` | Noto Sans JP | `deed.ja` |
| `uz` | 우즈베크어(라틴) | Oʻzbekcha | `uz` | IBM Plex Sans | `deed.en` |
| `ru` | 러시아어 | Русский | `ru` | IBM Plex Sans | `deed.ru` |
| `vi` | 베트남어 | Tiếng Việt | `vi` | IBM Plex Sans (vietnamese 하위 집합 포함) | `deed.vi` |

### 14-2. 번역판을 만들 때 같이 바꾸는 것
- `<html lang>`, 글꼴(`--font`/`--sans` 앞에 추가 글꼴, `--px`도 대체 글꼴 포함), CC 링크.
- **편끼리 링크**(HTML의 href와 JS 문자열 모두): `5-2_….html` → `5-2_….en.html`, `index.html` → `index.en.html`. 절대 주소(앞에 `/`가 있는 것)와 다른 시리즈 링크는 그대로.
- 언어 UI(8장)를 넣은 뒤 링크 변환을 하면 배너의 한국어 링크까지 바뀌므로 **링크 변환 → UI 삽입** 순서를 지킨다.
- **베트남어 글꼴**: 첫 화면의 픽셀 글꼴 Galmuri에는 베트남어 성조 부호가 없을 수 있으므로 vi판의 `--px`는 `"Galmuri11","IBM Plex Sans",monospace`처럼 대체 글꼴을 바로 뒤에 둔다.
- **중국어·일본어 줄바꿈**: 원본의 `word-break:keep-all`을 `*{word-break:normal!important;line-break:strict}`로 덮어쓴다.
- **용어 말풍선**(en·uz·ru·vi): 용어 찾기 정규식에 `'i'` 플래그, 말풍선 조회도 대소문자 무시.

### 14-3. 번역 범위
- 옮긴다: HTML 본문, `<title>`, `meta description/og`, `alt`, `title`, `aria-label`, `placeholder`, 표 머리글 HTML이 든 속성, JS 문자열(버튼, 캔버스 글자, 결과 문구, 퀴즈, 용어 사전, 프롬프트, 말풍선, 토스트), Colab 코드의 **주석·docstring·print 문구**.
- 옮기지 않는다: 코드 식별자·숫자·연산자·f-string 식, 단위, 파일 이름, URL, 고유 명칭(Colab, YOLO, OpenPose, MediaPipe, numpy, CAM-07, MISSION RECEIVED, `[SYSTEM]`), 이모지·화살표·원문자(→ ▶ ❚❚ ①②), 편 번호, CSS·JS 주석, 그림 파일 속 글자.
- 번역판 화면에 한국어가 남으면 안 된다(14-5 예외만 허용).

### 14-4. 코드와 엮인 문자열
- **같은 한국어 문자열 = 사이트 전체에서 같은 번역 하나.** JS 비교(`===`)·객체 키·용어 키가 어긋나지 않는다.
- 숫자와 이어 붙는 조각(`n+'개'`, `'정확도 '+x+'%'`)은 이어 붙인 결과가 자연스럽게, 이음매 띄어쓰기 유지(en·uz·ru·vi는 단위 앞 띄어쓰기, zh·ja는 띄어쓰기 없이).
- 캔버스 라벨은 한국어와 비슷한 길이로 짧게.
- 태그·속성·엔티티(`&nbsp;`)·JS 따옴표 안전(ASCII 따옴표가 문자열을 깨지 않게) 유지.
- 같은 데이터(관절 이름 등)를 Python과 JS가 함께 쓰면 두 곳을 같은 말로.

### 14-5. 언어 자체를 다루는 실습의 예외
한국어 입력이 있어야만 작동하는 실습(예: 5-4 단어 주머니 — 한국어 단어 조각 40개로 학습)은:
- 모델에 넣는 예시 문장·단어 조각·연결어("다가", "고 나서")와 데이터 배열(VOCAB, CAPTIONS 등)을 **한국어로 두고**, 화면에 처음 나올 때 괄호로 뜻을 붙인다: en `"캔을 던진다" (throws a can)`.
- 같은 데이터를 쓰는 Colab 코드의 데이터 문자열도 한국어로 두고 주석만 옮긴다(결과 숫자가 그대로 맞도록).
- 그 밖의 편에서 인용한 프롬프트("춤춰")는 정상 번역(en "Dance!").

### 14-6. 용어 사전(GL)
- 제목은 `번역어 (English term[, 덧붙임])` 형식 유지(괄호로 칸을 나누므로). zh·ja·uz·ru·vi: `边界框 (Bounding box)`, `Khung bao (Bounding box)`.
- en: 괄호가 같은 말 반복이면 빼고(`Bounding box`), 별칭이 있을 때만 남김(`Keypoint (joint)`). 표 머리글 "영어"는 영어판에서만 "Also known as".
- 키는 번역 본문에 그대로 나오는 가장 짧은 형태(en·uz·ru·vi는 소문자).

### 14-7. 언어별 문체
- **en:** 쉬운 교재 영어, 짧은 문장.
- **zh:** 간체자, 평서문.
- **ja:** 본문과 설명은 부드러운 です・ます체, 말풍선은 자연스러운 구어. 판정만 짧게 끊는다.
- **uz:** 라틴 문자 표준 문어, oʻ·gʻ는 U+02BB(ʻ), 끊음 표시는 U+02BC(ʼ, 공개된 번역판과 같음), 독자는 siz. 딱딱한 관청 문체보다 부드러운 설명체.
- **ru:** 중립적 과학 대중서 문체, 독자는 «вы».
- **vi:** 쉽고 친근한 교재체 평서문, 독자는 "bạn". 성조·발음 부호를 빠짐없이 쓰고(유니코드 NFC), 한자어보다 일상어를 먼저 쓴 뒤 괄호에 정식 용어.
- 숫자·소수·단위 그대로. 천 단위 구분은 en·zh·ja `6,220,800`, ru·uz `6 220 800`도 가능. vi는 원본 표기(`6,220,800`, 소수점 `.`)를 그대로 둔다 — 화면 숫자와 코드 출력이 어긋나지 않게.
- 뜻을 옮기고 정보를 더하거나 빼지 않는다. 미션 이야기의 재미는 살린다.

### 14-8. 고정 용어표
저자·등장인물·시리즈 고유 용어는 아래를 따른다(새 시리즈는 이 표에 행을 더한다). 그 밖의 기술 용어는 각 언어의 표준 용어.


| 한국어 | en | zh | ja | uz | ru | vi |
|---|---|---|---|---|---|---|
| AI는 동작을 어떻게 알아보고 만들까? (시리즈 제목) | How Does AI Recognize and Create Motion? | AI 如何识别和生成动作？ | AIは動作をどう見分け、どう作るのか？ | AI harakatni qanday taniydi va yaratadi? | Как ИИ распознаёт и создаёт движения? | AI nhận biết và tạo ra chuyển động như thế nào? |
| 동작 AI (시리즈 약칭) | Motion AI | 动作 AI | 動作AI | Harakat AI | ИИ движений | AI chuyển động |
| 긴급 미션 / 최종 미션 | Emergency mission / Final mission | 紧急任务 / 最终任务 | 緊急ミッション / 最終ミッション | Shoshilinch missiya / Yakuniy missiya | Срочная миссия / Финальная миссия | Nhiệm vụ khẩn cấp / Nhiệm vụ cuối cùng |
| 안상선 ((주)M-Robo 대표) | Ahn Sangsun (CEO, M-Robo Co., Ltd.) | Ahn Sangsun（M-Robo 株式会社代表） | Ahn Sangsun（株式会社M-Robo代表） | Ahn Sangsun (M-Robo kompaniyasi rahbari) | Ahn Sangsun (генеральный директор M-Robo Co., Ltd.) | Ahn Sangsun (Giám đốc điều hành, M-Robo Co., Ltd.) |
| 글 · 안상선 | Written by Ahn Sangsun | 作者 · Ahn Sangsun | 文・Ahn Sangsun | Muallif · Ahn Sangsun | Автор · Ahn Sangsun | Tác giả · Ahn Sangsun |
| 박사 | the Doctor | 博士 | 博士 | Doktor | Доктор | Tiến sĩ |
| 조수 | the Assistant | 助手 | 助手 | Yordamchi | Ассистент | Trợ lý |
| 조수(하루) | the Assistant (Haru) | 助手（Haru） | 助手（ハル） | Yordamchi (Haru) | ассистент (Хару) | Trợ lý (Haru) |
| 세나 (조수의 예명) | Sena | Sena | セナ | Sena | Сена | Sena |
| 초파리 연구원 | the Fruit Fly Researcher | 果蝇研究员 | ショウジョウバエ研究員 | Meva pashshasi tadqiqotchisi | Исследователь-дрозофила | Nhà nghiên cứu Ruồi giấm |
| 주판봇 | AbaBot | 算盘宝 | アバボット | AbaBot | АбаБот | AbaBot |
| 연구실 (식구들) | the lab (crew) | 研究室（成员） | 研究室（の仲間たち） | laboratoriya (jamoasi) | лаборатория (команда) | phòng thí nghiệm (các thành viên) |
| 본부 | HQ | 总部 | 本部 | shtab | штаб | Sở chỉ huy |
| 막대 인형 | stick figure | 火柴人 | 棒人間 | chiziqcha odam | человечек-палочка (стик-фигура) | người que |
| 쓰레기 (무단) 투기 | (illegal) littering / dumping | （乱扔）垃圾 / 乱扔垃圾 | ゴミの（不法）投棄 | chiqindini (noqonuniy) tashlash | (незаконный) выброс мусора | (lén) vứt rác / xả rác bừa bãi |
| 투기 / 정상 (판정 이름) | Littering / Normal | 乱扔 / 正常 | 投棄 / 正常 | Tashlash / Normal | Выброс / Норма | Xả rác / Bình thường |
| 판정보류 | abstain ("no call") | 暂不判定 | 判定保留 | qaror kechiktirildi | воздержание от решения | tạm hoãn phán định |
| 관제실 (라이브 관제실) | control room (live control room) | 监控室（实时监控室） | 管制室（ライブ管制室） | nazorat xonasi (jonli nazorat xonasi) | диспетчерская (живая диспетчерская) | phòng giám sát (phòng giám sát trực tiếp) |
| 관절 | joint (keypoint) | 关节（关键点） | 関節（キーポイント） | boʻgʻim (kalit nuqta) | сустав (ключевая точка) | khớp (điểm mốc) |
| 특징 | feature | 特征 | 特徴 | belgi (xususiyat) | признак | đặc trưng |
| 규칙 대 학습 | rules vs. learning | 规则 vs 学习 | ルール対学習 | qoida va oʻrganish | правила против обучения | quy tắc và học |
| 헛경보 / 놓침 | false alarm / miss | 误报 / 漏报 | 誤報 / 見逃し | soxta signal / oʻtkazib yuborish | ложная тревога / пропуск | báo động giả / bỏ sót |
| 판별 모델 / 생성 모델 | discriminative model / generative model | 判别模型 / 生成模型 | 識別モデル / 生成モデル | diskriminativ model / generativ model | дискриминативная / генеративная модель | mô hình phân biệt / mô hình sinh |
| 생성기 (A~E) | generator (A–E) | 生成器 | 生成器 | generator | генератор | bộ sinh (A–E) |
| 감독관 (채점표) | the Evaluator (score sheet) | 评审员（评分表） | 審査官（採点表） | Nazoratchi (baholash varaqasi) | Эксперт (оценочный лист) | Giám khảo (phiếu chấm điểm) |
| 진짜 같음 · 다양성 · 새로움 | realism · diversity · novelty | 逼真度 · 多样性 · 新颖性 | 本物らしさ・多様性・新しさ | haqqoniylik · xilma-xillik · yangilik | правдоподобие · разнообразие · новизна | độ chân thực · độ đa dạng · độ mới |
| 뼈 길이 오차 | bone-length error | 骨长误差 | 骨の長さの誤差 | suyak uzunligi xatosi | ошибка длины костей | sai số độ dài xương |
| 손잡이(잠재 변수) | knob (latent variable) | 旋钮（潜变量） | つまみ（潜在変数） | dasta (yashirin oʻzgaruvchi) | ручка (латентная переменная) | núm vặn (biến tiềm ẩn) |
| 손잡이 | knob | 旋钮 | つまみ | dasta | ручка | núm vặn |
| 잠재 지도 / 잠재 공간 | latent map / latent space | 潜在地图 / 潜在空间 | 潜在マップ / 潜在空間 | yashirin xarita / yashirin fazo | латентная карта / латентное пространство | bản đồ tiềm ẩn / không gian tiềm ẩn |
| 깔때기 (말 깔때기, 동작 깔때기) | funnel (text funnel, motion funnel) | 漏斗（文字漏斗、动作漏斗） | じょうご（言葉じょうご、動作じょうご） | voronka (soʻz voronkasi, harakat voronkasi) | воронка (текстовая, двигательная) | phễu (phễu chữ, phễu chuyển động) |
| 인코더 · 디코더 | encoder · decoder | 编码器 · 解码器 | エンコーダ・デコーダ | enkoder · dekoder | кодировщик · декодер (энкодер · декодер) | bộ mã hóa · bộ giải mã |
| 병목 | bottleneck | 瓶颈 | ボトルネック | tor boʻgʻiz (bottleneck) | узкое место (бутылочное горлышко) | nút thắt cổ chai |
| 떨림 / 가림 | jitter / occlusion | 抖动 / 遮挡 | 揺れ / 隠れ | titrash / toʻsilish | дрожание / перекрытие | rung / che khuất |
| 단어 주머니 | bag of words | 词袋 | 単語袋（バッグ・オブ・ワーズ） | soʻzlar xaltasi | мешок слов | túi từ |
| 사전 (조각) | dictionary (pieces) | 词典（片段） | 辞書（かけら） | lugʻat (boʻlaklar) | словарь (фрагменты) | từ điển (mảnh từ) |
| 짝 맞추기 | pair matching | 配对 | ペア合わせ | juftlash | подбор пар | ghép cặp |
| 대조 학습 | contrastive learning | 对比学习 | 対照学習 | kontrastiv oʻrganish | контрастивное обучение | học tương phản |
| 공유 지도 / 같은 지도 | shared map / the same map | 共享地图 / 同一张地图 | 共有マップ / 同じ地図 | umumiy xarita / bitta xarita | общая карта / одна карта | bản đồ chung / cùng một bản đồ |
| 찾기 · 만들기 · 이어 붙이기 | find · make · stitch | 查找 · 生成 · 拼接 | 探す・作る・つなぐ | topish · yaratish · ulash | найти · создать · склеить | tìm · tạo · nối |
| 포즈 맵 | pose map | 姿态图 | ポーズマップ | poza xaritasi | карта позы | bản đồ tư thế |
| 참조 이미지 | reference image | 参考图像 | 参照画像 | namuna rasm | референсное изображение | ảnh tham chiếu |
| 동작 일치율 | motion match score | 动作一致率 | 動作一致率 | harakat mosligi | процент совпадения движений | tỉ lệ khớp chuyển động |
| 나란히 보기 | side-by-side view | 并排查看 | 並べて見る | yonma-yon koʻrish | просмотр бок о бок | xem song song |
| 교육자를 위한 TIP / 교육자 TIP | Tips for educators / Educator tips | 教师指南 / 教师 TIP | 教育者向けTIP | Oʻqituvchilar uchun maslahatlar | Советы преподавателям | Mẹo cho người dạy / Mẹo giảng dạy |
| 확인 문제 | check questions | 练习题 | 確認問題 | nazorat savollari | проверочные вопросы | câu hỏi kiểm tra |
| 용어 정리 / 용어 사전 | glossary | 术语表 | 用語集 | atamalar lugʻati | глоссарий | bảng thuật ngữ |
| 비유 / 비유가 틀리는 지점 | analogy / where the analogy breaks | 比喻 / 比喻失效之处 | たとえ / たとえが外れるところ | oʻxshatish / oʻxshatish notoʻgʻri boʻladigan joy | аналогия / где аналогия не работает | phép so sánh / chỗ phép so sánh không đúng |
| 레퍼런스 | references | 参考文献 | 参考文献 | manbalar | источники | tài liệu tham khảo |
| 설명용 모형인 것 | what is an illustrative mock-up | 仅供说明的示意部分 | 説明用の模型であるもの | tushuntirish uchun maket boʻlgan narsalar | что здесь — иллюстративный макет | những gì là mô hình minh họa |
| 코드 1 / 코드 2 | Code 1 / Code 2 | 代码 1 / 代码 2 | コード1 / コード2 | 1-kod / 2-kod | Код 1 / Код 2 | Mã 1 / Mã 2 |
| 복사 · .py 내려받기 · 노트북 내려받기 | Copy · Download .py · Download notebook | 复制 · 下载 .py · 下载笔记本 | コピー・.pyをダウンロード・ノートブックをダウンロード | Nusxalash · .py yuklab olish · Notebook yuklab olish | Копировать · Скачать .py · Скачать ноутбук | Sao chép · Tải .py · Tải notebook |
| 딥러닝 A to Z (3-x 시리즈) | Deep Learning A to Z | 深度学习 A to Z | ディープラーニング A to Z | Chuqur oʻrganish A dan Z gacha | Глубокое обучение от A до Z | Học sâu từ A đến Z |
| AI는 이미지를 어떻게 구분할까? (4-x 시리즈) | How Does AI Tell Images Apart? | AI 如何区分图像？ | AIは画像をどう見分けるのか？ | AI rasmlarni qanday ajratadi? | Как ИИ различает изображения? | AI phân biệt hình ảnh như thế nào? |
| 크리에이티브 커먼즈 저작자표시-비영리 4.0 국제 라이선스(CC BY-NC 4.0) | Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0) | 知识共享 署名-非商业性使用 4.0 国际许可协议（CC BY-NC 4.0） | クリエイティブ・コモンズ 表示-非営利 4.0 国際ライセンス（CC BY-NC 4.0） | Creative Commons Attribution-NonCommercial 4.0 International litsenziyasi (CC BY-NC 4.0) | лицензия Creative Commons «Атрибуция — Некоммерческое использование» 4.0 Международная (CC BY-NC 4.0) | Giấy phép Creative Commons Ghi công – Phi thương mại 4.0 Quốc tế (CC BY-NC 4.0) |

---

## 15. 외국어판 제작 절차 — 언어팩 v1.3으로 실행

손으로 HTML을 고치지 않는다. 외국어판은 **언어팩**(`langpack_v1.3.zip`)으로 만든다. 언어팩이 문장 단위 추출·번역 메모리·번역 검사·조립·언어 전환 UI·README 조립·브라우저 검사를 맡는다. 자세한 사용법은 언어팩의 `README.md`.

1. **준비**: 저장소 루트에 `langpack/`을 두고 `config.example.json`을 `config.json`으로 복사한다. 시리즈마다 정할 것:
   - `pages`, `siteUrl`(공개 주소), `langStorageKey`(예: `motion_ai_lang`), `readme`
   - `switcherHosts`: 각 편은 기본값(`nav.top .brand` 뒤), 첫 화면은 `[".alarm .go","before"]`를 앞에 둔다.
   - `fontVars`: `["--font","--sans"]`
2. **용어표**: 14-8의 시리즈 고유 용어를 `rules/glossary/20_topic_<시리즈>.json`으로 옮긴다. 캐릭터·저자 이름은 `00_series.json`에 이미 있다.
3. **추출과 왕복 검사**: `extract` → `roundtrip`(OK여야 다음으로) → `seed` → `pending all`.
4. **번역**: 언어마다 하위 에이전트 하나(en·zh·ja Haiku급, ru·uz·vi Sonnet급) 또는 `api_translate.py`. 묶음은 에이전트 실행이면 언어당 하나(3만 자).
5. **검사**: `check` → 실패분은 `retry`로 모아 한 번 더.
6. **조립**: `merge`가 HTML 번역판, `dist/README.md`(7개 언어, 「언어」 절 포함), Colab 코드 compile 검사를 한다. `codecheck --run`으로 코드를 실제 실행한다.
7. **브라우저 검사**: `node langpack/browser_check.js --shots` → "모두 통과".

언어팩이 하지 않는 것(작가가 원본에서 처리):
- **편끼리 링크 변환(14-2)**: 번역판의 다른 편 링크는 한국어 파일을 가리킨다. 언어 전환 스크립트가 기억된 언어로 다시 옮겨 준다.
- **용어 말풍선의 `i` 플래그(14-2)**: 페이지 코드에 맞춰 `postReplaceRegex`로 한 번 정해 둔다.
- **언어 자체를 다루는 실습(14-5)**: 한국어로 남길 데이터 배열은 `skipVars`·`data-i18n-skip`으로 빼고, 괄호 뜻풀이는 원본에 쓴다.
- **바깥 파일의 글자**: 화면 글자는 HTML 안에 둔다(1장: 한 파일에 모두 담는다).

## 16. 검사 (전달 전에 모두 통과)

- [ ] 모든 `<script>`가 구문 오류 없이 파싱된다(42개 파일).
- [ ] 7개 언어 × 모든 페이지를 헤드리스 브라우저로 열고 버튼을 모두 눌러 본다: 스크립트 오류 0, 화면·`alt`·`aria-label`에 남은 한국어 0(14-5 예외만).
- [ ] 페이지 안 Colab 코드를 모든 언어에서 `compile()` + 실제 실행(외부 파일이 필요한 코드 제외) → 오류 0.
- [ ] 자동 전환: 브라우저 언어 en/ja/zh/uz/ru/vi → 해당 파일, de/ko → 한국어. 고른 언어 기억, `?lang=`, `#섹션` 유지, 편끼리 링크가 같은 언어로 이어짐.
- [ ] 최상단 메뉴의 언어 선택 상자와 🌐 배너가 데스크톱(1280px)·휴대폰(390px)에서 보이고 작동한다. 가로 넘침 없음.
- [ ] 베트남어 성조 부호가 글꼴 깨짐 없이 보인다(제목·픽셀 글꼴·캔버스 글자).
- [ ] 중국어·일본어 줄바꿈 정상, 용어 밑줄·말풍선 정상, 용어 표 머리글 정상.
- [ ] 스크린샷으로 실습 섹션 몇 곳을 눈으로 확인(캔버스 글자 넘침).

---

## 17. 전달

- 저장소 루트에 그대로 올릴 수 있게 **폴더 없이** HTML(한국어 6 + 번역 36)과 `README.md`를 묶는다.
- 압축 파일 하나가 30MB를 넘으면 나눈다: ① 한국어 + en + zh + README ② ja + uz + ru ③ vi (언어 하나가 압축 후 약 7MB).
- 전달 글에 적을 것: 언어 전환 방식(최상단 메뉴·🌐 배너·자동 전환·기억·`?lang=`), 확인한 것, 언어 예외가 있는 편, 그림 속 글자는 그대로라는 점, 다른 시리즈 링크는 한국어로 연결된다는 점, README 러시아어·베트남어는 순서 밖이라 맨 끝에 붙였다는 점, **원어민 검수 전**(특히 우즈베크어·러시아어·베트남어).
