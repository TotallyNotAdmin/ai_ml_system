# Monitoring

## Технические метрики

| Метрика | Зачем |
|---|---|
| hot path latency p50/p95/p99 | Контроль SLA 500 ms |
| classifier error rate | Доступность и стабильность классификации |
| retrieval latency | Деградация поиска |
| LLM error rate | Доступность внешнего LLM API |
| LLM timeout rate | Проблемы сети или provider |
| queue lag | Задержка async-генерации |
| fallback rate | Как часто система деградирует |
| JSONL audit write errors | Потеря аудита |
| CPU / memory | Инфраструктурные ограничения |

## ML-метрики

| Метрика | Зачем |
|---|---|
| распределение confidence | Поиск деградации модели |
| распределение topic/risk | Изменение входящего потока |
| доля unknown topic | Качество классификатора |
| доля low-confidence | Корректность порогов |
| retrieval hit rate | Качество базы знаний и retrieval |
| human override rate | Насколько модель ошибается |
| auto-close reopen rate | Качество автоматических ответов |
| CSAT по auto-close | Продуктовое качество |

## Бизнес-метрики

- cost per ticket;
- operator workload;
- auto-deflection rate;
- first response time;
- SLA compliance;
- CSAT;
- reopen rate;
- escalation rate;
- LLM cost per day;
- savings estimate.

## Стартовые алерты

| Алерт | Условие |
|---|---|
| Hot path SLO breach | p95 latency > 500 ms за 5 минут |
| LLM unavailable | error rate > 5% за 5 минут |
| LLM budget | дневной бюджет использован на 80% |
| Low confidence spike | доля low-confidence > baseline на 20% |
| High-risk spike | резкий рост high-risk тикетов |
| Retrieval degradation | retrieval hit rate упал заметно |
| Auto-close quality | reopen rate auto-close выше общего |
| PII leak | обнаружение PII в отправленных черновиках |
| Audit failure | ошибки записи audit log |

## Как отличить деградацию модели от изменения потока

Нужно сравнивать:

1. Распределение входных текстов.
2. Распределение каналов.
3. Распределение времени и инцидентов.
4. Долю новых слов и новых тем.
5. Показания на стабильном golden set.

Если golden set качество стабильно, но входное распределение изменилось — вероятно, изменился поток.
Если качество падает и на golden set — вероятно, деградирует модель.

## Мониторинг стоимости LLM

Нужно отслеживать:

- tokens per request;
- cost per ticket;
- cost per day;
- cost by topic;
- cost by route;
- доля запросов, попавших в budget limit;
- эффективность черновиков: cost / approved draft.

В PoC стоимость считается условно: `tokens / 1000 × LLM_COST_PER_1K_TOKENS_RUB`.

## Как понять, что исходная задача решается

Главный критерий — не точность модели, а бизнес-эффект:

- операторы тратят меньше времени;
- первый ответ приходит быстрее;
- CSAT не падает;
- reopen rate не растёт;
- high-risk кейсы не автоматизируются ошибочно;
- стоимость LLM меньше экономии.
