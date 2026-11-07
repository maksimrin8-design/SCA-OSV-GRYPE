# SCA-OSV-GRYPE

Бенчмарк для сравнения **OSV-Scanner** и **Grype** на зависимостях реальных GitHub-проектов.

## Область исследования

В этой работе реализуется только **SCA (Software Composition Analysis)**: сравнение обнаружения известных уязвимостей в сторонних зависимостях. SAST, SBOM как отдельный эксперимент и Secret Scanning в текущий объём не входят.

## Что находится в репозитории

- `projects/manifest.json` — 30 уникальных upstream GitHub-репозиториев с закреплёнными commit SHA.
- `.github/workflows/scan.yml` — GitHub Actions workflow, запускающий OSV-Scanner и Grype для каждого проекта.
- `ground-truth/expected-vulnerabilities.csv` — независимо проверяемый эталон; в сравнительную таблицу попадают только строки со статусом `verified`.
- `scripts/build_sca_table.py` — формирует одну качественную сравнительную таблицу SCA в Markdown и CSV.

## Структура результата для каждого приложения

Workflow формирует каталог приложения и сохраняет его в отдельный GitHub Actions artifact:

```text
application-name/
├── project.json
├── upstream-commit.txt
├── upstream.txt
├── dependency-files.txt
├── osv/
│   ├── result.json
│   ├── version.txt
│   └── exit-code.txt
├── grype/
│   ├── result.json
│   ├── version.txt
│   └── exit-code.txt
└── default/
    └── reference.json
```

- `osv/` — исходный JSON-отчёт OSV-Scanner, версия инструмента и код завершения.
- `grype/` — исходный JSON-отчёт Grype, версия инструмента и код завершения.
- `default/` — эталонные записи для приложения. Если проверенных записей пока нет, это явно помечается как `not_yet_adjudicated`; пустой список не означает, что приложение не содержит уязвимых зависимостей.

## Запуск

1. Откройте **Actions → SCA benchmark (OSV-Scanner vs Grype)**.
2. Нажмите **Run workflow**.
3. После завершения скачайте артефакты `scan-Pxxx-...` — внутри каждого находится структура приложения.
4. Скачайте `sca-benchmark-comparison`: в нём находятся `sca-comparison.md` (единая таблица), `sca-comparison.csv` и `evidence-index.json`.

Результаты сохраняются как workflow artifacts, а не автоматически коммитятся обратно в ветку. Это сохраняет историю запусков и не создаёт коммиты от имени Actions при каждом сканировании.

## Ground Truth и корректная интерпретация

**30 репозиториев — корпус для сканирования, а не утверждение, что все 30 содержат уязвимые зависимости.** Уязвимости бизнес-логики приложения (например, XSS/SQLi) не являются эталоном для SCA.

Сейчас подтверждён один тестовый случай:

- `coder/osv-test`, `minimist@0.0.8`, npm.
- `GHSA-xvch-5gv4-984h` / `CVE-2021-44906` — идентификаторы одной уязвимости.
- Lockfile: https://github.com/coder/osv-test/blob/18c46d1b2a0119ff94e910e0b305819b763a4e79/fixtures/vulnerable/package-lock.json
- Advisory: https://github.com/advisories/GHSA-xvch-5gv4-984h

Остальные проекты остаются кандидатами на сканирование, пока их lockfiles и версии зависимостей не сверены с диапазонами затронутых версий в advisories. Неизвестные находки не объявляются ложноположительными, а приложения без подтверждённых эталонных записей не оцениваются по recall.

## Ограничения воспроизводимости

Workflow фиксирует фактический upstream commit и версии сканеров в артефактах. Установка сканеров через `latest` означает, что версии инструментов могут меняться между запусками; для финального эксперимента следует закрепить конкретные версии OSV-Scanner и Grype, а также зафиксировать дату/состояние баз уязвимостей.
