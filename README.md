# Support Ticket AI Triage PoC

Минимальный Proof-of-Concept AI/ML-системы для автоматизации обработки тикетов поддержки крупного онлайн-сервиса.

## Зачем это бизнесу

Система снижает нагрузку на операторов, автоматически обрабатывая типовые FAQ и помогая операторам черновиками ответов. Это сокращает время первого ответа и стоимость обработки тикетов, особенно во время инцидентов и пиковых всплесков. Рисковые категории — платежи, безопасность, персональные данные — остаются под контролем человека, что защищает CSAT, SLA и снижает юридические риски. Экономический эффект создаётся за счёт автоматического закрытия части типовых обращений и ускорения работы операторов.

## Что делает PoC

PoC демонстрирует:

1. приём mock-тикета;
2. обнаружение и маскирование PII;
3. быструю классификацию темы и риска без LLM;
4. поиск похожей статьи базы знаний;
5. маршрутизацию: auto-close, operator review или urgent operator;
6. генерацию черновика ответа через mock LLM;
7. fallback, если LLM недоступен;
8. аудит решения в JSONL-лог.

## Быстрый старт

Требуется Python 3.10+.

Запуск demo:

```bash
python -m poc.demo
```

Запуск smoke-тестов:

```bash
python -m unittest discover -s poc/tests -t . -v
```

Проверка fallback при недоступности LLM:

```bash
SIMULATE_LLM_FAILURE=true python -m poc.demo
```

Для Windows cmd:

```cmd
set SIMULATE_LLM_FAILURE=true && python -m poc.demo
```

После запуска создаётся файл `var/decisions.jsonl` с логом решений.

## Демонстрируемые сценарии

| Ticket | Сценарий | Ожидаемое поведение |
|---|---|---|
| T-001 | Типовой FAQ: отмена подписки | low risk, high confidence, auto-close или safe template fallback |
| T-002 | Платёжная проблема + PII | high risk, PII redaction, urgent operator, без LLM |
| T-003 | Низкая уверенность | unknown topic, low confidence, operator review |
| T-004 | Технический сбой | medium risk, operator review, draft для оператора |

## Что реализовано реально, а что является архитектурным дизайном

### Реально в PoC

- Рабочий end-to-end pipeline.
- Правила классификации темы и риска.
- Простая PII-редукция: email, карта, телефон, CVV/CVC.
- Локальный retrieval по базе знаний на основе TF-IDF-подобного скоринга.
- Mock LLM вместо внешнего LLM API.
- JSONL-аудит решений.
- Fallback при недоступности LLM.
- Smoke-тесты.

### Архитектурный дизайн / целевая система

- Очереди и асинхронная генерация ответов.
- Обученная быстрая ML-модель классификации вместо правил.
- Multilingual embeddings + vector DB вместо локального BoW/TF-IDF.
- Внешний или self-hosted LLM через gateway с timeout, retry, circuit breaker и cost control.
- Prometheus/Grafana, алерты, ML-мониторинг.
- Полноценная разметка исторических тикетов и offline evaluation.
- Production-grade PII detection: NER, regex, DLP-политики.

## Допущения и ограничения

- PoC не является production-ready.
- Внешний LLM API по умолчанию не используется.
- Классификатор основан на правилах и keyword matching.
- Retrieval упрощён: локальная база знаний и лексический скоринг.
- Очередь, auth, rate limiting, persistence и UI оператора не реализованы.
- Автоматически закрываются только low-risk FAQ с высоким уровнем уверенности и совпадением с базой знаний.
- High-risk категории и PII-тикеты не отправляются в LLM и требуют участия оператора.

## Документация

- [docs/architecture.md](docs/architecture.md) — архитектурная диаграмма и описание.
- [docs/ml.md](docs/ml.md) — ML/LLM-задачи, выбор подходов, baseline, валидация.
- [docs/monitoring.md](docs/monitoring.md) — мониторинг, метрики, алерты.
- [docs/risks-and-ops.md](docs/risks-and-ops.md) — риски, highload, privacy, safety.
- [AI_USAGE.md](AI_USAGE.md) — как использовались AI-инструменты.
- [SELF_REVIEW.md](SELF_REVIEW.md) — слабые места, риски и план доработки.
