# ML / LLM design

## Основные ML-задачи

| Задача | Где используется | Подход в PoC | Целевой подход |
|---|---|---|---|
| Классификация темы | Hot path | Правила и keyword scoring | Лёгкая ML-модель: logistic regression / CatBoost / small transformer |
| Оценка риска | Hot path | Правила | Правила + ML risk score + calibration |
| PII detection | Перед LLM и логом | Regex | Regex + NER + DLP-политики |
| Поиск похожего тикета / KB | Hot path | Локальный TF-IDF-like retrieval | Embeddings + vector DB + BM25 hybrid |
| Генерация ответа | Async | Mock LLM / шаблоны | LLM через gateway с guardrails |
| Дедупликация тикетов | Anti-storm | Не реализовано | Embeddings similarity + incident clustering |
| Контроль качества ответа | Post-processing | Не реализовано | Policy checks, toxicity/PII filter, human sampling |

## Где нужна LLM

LLM полезна для:

- генерации черновиков ответов оператору;
- суммаризации длинных переписок;
- предложения похожих решений;
- помощи оператору в сложных кейсах.

## Где LLM не нужна

LLM не должна:

- принимать финальное решение о закрытии high-risk тикета;
- быть обязательным на hot path;
- видеть сырые PII;
- генерировать ответы по финансовым/юридическим/безопасным кейсам без контроля;
- работать без cost limit и circuit breaker.

## Baseline-модели

Разумные первые baseline:

1. Правила для риска и маршрутизации.
2. TF-IDF + logistic regression для темы.
3. BM25 или простой vector retrieval для базы знаний.
4. Шаблоны для типовых ответов.
5. LLM только как draft assistant.

## Откуда брать модели

Возможные варианты:

- открытые multilingual embeddings: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`;
- лёгкие русскоязычные модели: `cointegrated/rubert-tiny2` или аналогичные;
- классический ML: `scikit-learn`, `CatBoost`;
- LLM: внешний API или self-hosted модель в зависимости от privacy-политики.

В PoC модели не обучаются. Используются mock-компоненты и правила.

## Данные для обучения

Нужны исторические тикеты:

- текст обращения;
- канал;
- категория;
- резолюция;
- время обработки;
- reopen / CSAT;
- инцидентные метки;
- признаки PII;
- решения операторов.

Перед использованием данные нужно:

- обезличить;
- удалить PII;
- разметить по темам и рискам;
- отделить high-risk категории.

## Разметка

Для пилота достаточно:

1. Взять стратифицированную выборку исторических тикетов.
2. Разметить topic и risk.
3. Для high-risk категорий использовать двойную разметку.
4. Расхождения разбирать арбитром.
5. Отдельно разметить выборку для retrieval evaluation.
6. Поддерживать golden set для регрессионных проверок.

## Метрики качества

### Классификация темы

- macro F1;
- accuracy;
- confusion matrix;
- latency p95;
- доля low-confidence решений.

### Оценка риска

Главное — не пропустить high-risk:

- recall для high-risk;
- precision для high-risk;
- false negative rate для high-risk;
- calibration error.

### Retrieval

- recall@k;
- precision@k;
- MRR;
- доля тикетов с релевантным KB hit;
- human relevance rate.

### LLM-ответы

- human approval rate;
- edit distance / edit rate оператором;
- доля ответов, отправленных без изменений;
- reopen rate по auto-close;
- CSAT по auto-close;
- доля небезопасных ответов.

## Обработка низкой уверенности

Если confidence ниже порога:

1. Тикет не закрывается автоматически.
2. Маршрутизируется оператору.
3. Может получить draft, но только как подсказку.
4. Решение логируется.
5. Такие кейсы попадают в active learning sampling.

## Почему выбран такой подход

Подход позволяет:

- быстро стартовать без больших данных;
- контролировать безопасность;
- держать hot path дешёвым;
- постепенно заменять правила на ML;
- измерять эффект до масштабирования.
