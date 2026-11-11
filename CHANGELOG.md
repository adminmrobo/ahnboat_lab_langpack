# 변경 기록

## 2026-11-11 · 언어팩 v1.5 — 새 식구 시아·모아

- 용어표 `00_series.json`에 캐릭터 팩 1.4의 새 식구를 더함: `인턴 시아`·`시아`(en Intern Sia / Sia · zh 实习生西娅 / 西娅 · ja インターンのシア / シア · uz Stajyor Sia / Sia · ru Стажёрка Сия / Сия · vi Thực tập sinh Sia / Sia), `인턴 모아`·`모아`(en Intern Moa / Moa · zh 实习生茉雅 / 茉雅 · ja インターンのモア / モア · uz Stajyor Moa / Moa · ru Стажёрка Моа / Моа · vi Thực tập sinh Moa / Moa), 미공개 X1~X3용 `미공개`(en Secret · zh 未公开 · ja 未公開 · uz Sir · ru Секрет · vi Bí mật). 표기는 ahnboat_lab_explainer `packs/lang/langpack` 사본과 같음.
- 외국어판 규격 14-8 표·언어 추가 작업 문서 고정 용어표에 같은 행을 더하고, 캐릭터 표기 줄(SKILL·README·규격)에 인턴 시아·모아를 넣음.

## 2026-11-04 · 언어팩 v1.4 — 연구실 로봇 이름 교체

- Money-Robo((주)M-Robo 회사 캐릭터) → **주판봇**. 외국어판 표기 en·uz·vi AbaBot · ja アバボット · zh 算盘宝 · ru АбаБот. "모든 언어에서 그대로" 규칙을 언어별 표기로 바꿈.
- 용어표 `00_series.json`에 `주판봇` 행을 더하고 `주판봇 승` 행을 고침. 씨앗 메모리 6개 언어, 언어 규칙 7개, 외국어판 규격·언어 추가 작업 문서의 이름을 함께 고침.

## 2026-11-03 · 저장소 첫 판 (ahnboat_lab_explainer에서 분리)

- **번역 스킬 1.0** (`SKILL.md`, 스킬 이름 `ahnboat-lab-translate`): 도구 가져오기, 시작 전 확인, 실행 순서, 에이전트 프롬프트, 고정 규칙, 언어팩이 하지 않는 것.
- **언어팩 v1.3** (`langpack/`): `ahnboat_lab_explainer`의 `packs/lang/langpack/`을 옮김. 저자 이름을 모든 언어에서 Ahn Sangsun으로 — 러시아어 용어표 `안상선`과 러시아어 씨앗 메모리 3문장의 "Ан Сансон (Ahn Sangsun)"을 "Ahn Sangsun"으로 고침.
- **외국어판 규격 1.1** (`docs/I18N_spec.md`): 미션형 시리즈 제작 지시서의 8장·13~17장을 옮김(장 번호 유지). 14-8 표의 저자 이름 ja·ru를 Ahn Sangsun으로.
- **작업 팩 · 언어 추가 1.1** (`tasks/TASK_add_lang.md`): `packs/task/`에서 옮기고 경로만 고침.
- `docs/SPEC_langpack_patch_VER1.0.md`: 언어팩 원 규격을 옮김.

언어팩 자체의 판별 변경(v1.1~v1.3)은 `langpack/README.md` 끝의 "바뀐 점".
