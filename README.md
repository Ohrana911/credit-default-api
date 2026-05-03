<img width="1235" height="90" alt="Снимок экрана 2026-05-03 004055" src="https://github.com/user-attachments/assets/e1aca248-5624-460d-a224-05a29d2ea4df" />
<img width="1960" height="589" alt="Снимок экрана 2026-05-03 002342" src="https://github.com/user-attachments/assets/842bab29-16ba-40e1-ba4c-db47f982e25b" />
<img width="766" height="532" alt="Снимок экрана 2026-05-03 002110" src="https://github.com/user-attachments/assets/a7b0f94c-faca-4b33-af2e-bc160b23a23b" />
<img width="970" height="815" alt="Снимок экрана 2026-05-02 204338" src="https://github.com/user-attachments/assets/075781d0-6a49-4dfb-837e-40ac76fe8af7" />
<img width="2" height="2" alt="Снимок экрана 2026-05-02 204331" src="https://github.com/user-attachments/assets/0d38a58f-9b92-44c0-8c3d-e7ce85c0b905" />
<img width="994" height="675" alt="Снимок экрана 2026-05-02 203012" src="https://github.com/user-attachments/assets/2aa52b46-8b82-49ea-bf64-20124a7d64eb" />
<img width="988" height="839" alt="Снимок экрана 2026-05-02 202806" src="https://github.com/user-attachments/assets/ae4483c1-f68e-408d-82f0-6a66563eb416" />
<img width="983" height="349" alt="Снимок экрана 2026-05-02 202732" src="https://github.com/user-attachments/assets/01565829-3b85-4ad4-b8a8-7596e8d73dba" />
<img width="1259" height="260" alt="Снимок экрана 2026-05-02 202704" src="https://github.com/user-attachments/assets/20976aaa-809b-4519-a692-d380d342c2a5" />
<img width="970" height="395" alt="Снимок экрана 2026-05-02 202423" src="https://github.com/user-attachments/assets/489769ed-731d-40e8-bdc3-956c411a2505" />
<img width="984" height="397" alt="Снимок экрана 2026-05-02 202413" src="https://github.com/user-attachments/assets/3495eda9-931f-45da-bdf0-0bb6b4e3484f" />
<img width="1366" height="342" alt="Снимок экрана 2026-05-02 191507" src="https://github.com/user-attachments/assets/22a5dd9e-6788-46c2-b535-0c0dd7d7fd4e" />
<img width="978" height="781" alt="Снимок экрана 2026-05-02 190805" src="https://github.com/user-attachments/assets/f37de560-9626-40cd-acdd-88acc3650fc5" />
<img width="982" height="433" alt="Снимок экрана 2026-05-02 190729" src="https://github.com/user-attachments/assets/d186b6b8-2c3c-4d46-b3f2-1476aceb181d" />
<img width="970" height="265" alt="Снимок экрана 2026-05-02 190644" src="https://github.com/user-attachments/assets/a8918e91-e4f1-4b0b-b856-193e24935363" />
Финальный проект по дисциплине Внедрение моделей машинного обучения.
Целевая переменная: default.payment.next.month

## Структура проекта
data/ - исходные данные
models/ - сохраненные модели
src/ - исходный код
tests/ - тесты
nginx/ - конфигурация nginx
docs/ - доп. документация (здесь план AB теста)

## Модели, метрики и порог решения
В проекте сравниваются две разные модели:
v1: LogisticRegression + StandardScaler смотреть src/train.py, артефакт models/model_v1.joblib
v2: RandomForestClassifier смотреть src/train_v2.py, артефакт models/model_v2.joblib

### Обучение
Данные делим 80/20 (train_test_split, stratify=y, random_state=42)
Для первой версии v1 используем pipeline: масштабирование и логистическая регрессия
Классы несбалансированы, поэтому для второй v2 добавлен class_weight=balanced

### Метрики
Логистическая регрессия: F1 = 0.3553, Precision = 0.6868, Recall = 0.2396
RandomForestClassifier: F1 = 0.5407, Precision = 0.5248, Recall = 0.5576
Accuracy намеренно не используется как основная метрика, потому что при несбалансированных классах она вводит в заблуждение, такая модель, которая всегда предсказывает "нет дефолта", получила высокий accuracy, но она бесполезна. Поэтому основной метрикой выбран F1-score, гармоническое среднее между Precision и Recall, которое штрафует модель за плохую работу с любым из классов. А вот версия v2 значительно превосходит первую по F1 и Recall, что означает: она находит в 2.3 раза больше реальных должников.

### Порог и почему он такой
В API бинарное решение принимается по стандартному порогу: prediction = 1, если вероятность дефолта P(default) >= 0.5, иначе 0
0.5 самый простой и воспроизводимый бейзлайн без подбора порога по бизнес затратам. В реальном банке порог таким не будет

## Формат API
### GET /health
Ответ:
json
{"status":"ok"}

### POST /predict
Обязательные поля: все признаки клиента из датасета кроме ID и целевой.  
Необязательное поле (без указания будет использоваться лог. регрессия):
model_version: v1 или v2

Ответ:
json
{
  "model_version": "v1",
  "prediction": 0,
  "default_probability": 0.222334
}

Ошибки:
400 если body не JSON
400 если не хватает полей
400 если передан неверный model_version (если вообще передан)

## Обучение моделей
v1:
python src/train.py

v2:
python src/train_v2.py

## Запуск локально
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python src/train.py
python src/train_v2.py
python src/api.py

## Автотесты
Проект включает базовые автотесты через pytest для проверки корректности API. Тесты покрывают эндпоинты /health, /predict а так же отсутствующие поля и неверный model_version

## Примеры API-запросов
Проверка сервиса:
http://127.0.0.1:5000/health

Предикт:
 -X POST http://127.0.0.1:5000/predict ^
  -H "Content-Type: application/json" ^
  -d "{\"LIMIT_BAL\":20000,\"SEX\":2,\"EDUCATION\":2,\"MARRIAGE\":1,\"AGE\":24,\"PAY_0\":2,\"PAY_2\":2,\"PAY_3\":-1,\"PAY_4\":-1,\"PAY_5\":-2,\"PAY_6\":-2,\"BILL_AMT1\":3913,\"BILL_AMT2\":3102,\"BILL_AMT3\":689,\"BILL_AMT4\":0,\"BILL_AMT5\":0,\"BILL_AMT6\":0,\"PAY_AMT1\":0,\"PAY_AMT2\":689,\"PAY_AMT3\":0,\"PAY_AMT4\":0,\"PAY_AMT5\":0,\"PAY_AMT6\":0}"

Предикт для модели v2:
 -X POST http://127.0.0.1:5000/predict ^
  -H "Content-Type: application/json" ^
  -d "{\"model_version\":\"v2\",\"LIMIT_BAL\":20000,\"SEX\":2,\"EDUCATION\":2,\"MARRIAGE\":1,\"AGE\":24,\"PAY_0\":2,\"PAY_2\":2,\"PAY_3\":-1,\"PAY_4\":-1,\"PAY_5\":-2,\"PAY_6\":-2,\"BILL_AMT1\":3913,\"BILL_AMT2\":3102,\"BILL_AMT3\":689,\"BILL_AMT4\":0,\"BILL_AMT5\":0,\"BILL_AMT6\":0,\"PAY_AMT1\":0,\"PAY_AMT2\":689,\"PAY_AMT3\":0,\"PAY_AMT4\":0,\"PAY_AMT5\":0,\"PAY_AMT6\":0}"

## План A/B теста
Cмотреть docs/AB_TEST_PLAN.md

## Архитектурное обоснование
В проекте выбран монолитный подход:
1. один Flask сервис проще разрабатывать и поддерживать, задания можно выполнить спокойно все "в одном месте"
2. меньше инфраструктурной сложности с настройкой межсервисного взаимодействия

Когда стоит переходить к микросервисам:
1. если отдельно масштабируется инференс, логирование, feature-processing или batch-prediction
2. если несколько команд независимо развивают части платформы
3. когда есть деньги

## Брокеры сообщения
В контексте данного проекта например простой (моя субъективная оценка) RabbitMQ мог бы использоваться для асинхронной пакетной обработки заявок на скоринг, для организации очереди на пересчёт рейтинга клиентов при обновлении модели, для асинхронной отправки логов и событий в аналитические системы. API отвечал бы мгновенно, а тяжёлые вычисления уходили в фон и не блокировали юзера.

## Логирование и мониторинг
1. Сейчас API пишет JSON-логи в stdout, так удобно сделать для докера, контейнер сам не знает куда писать логи, это решает инфраструктура снаружи
2. Логируются путь, метод, статус, request/response, время ответа
3. В проде логи из stdout собирались бы централизованно. Стандартный подход через стек ELK (Elasticsearch, Logstash, Kibana) или его аналог OpenSearch. Логи из stdout я бы собирал через filebeat, он умеет читать вывод контейнеров без изменений в коде. Дальше Elasticsearch, Kibana сверху для дашбордов. Главное что нужно видеть что если доля предсказаний дефолта по времени резко меняется, значит что то не так со входными данными, тогда становится видно сразу: сколько запросов, сколько ошибок, как распределились предсказания. Помимо логов, в production важно отслеживать метрики самого сервиса в реальном времени. Для этого используют связку Prometheus и Grafana. Prometheus опрашивает /metrics раз в несколько секунд и пишет временные ряды. Grafana для визуализация и алерты. Конкретно для этого проекта важен один алерт, если доля prediction=1 за час выросла в два раза значит скорее всего что то сломалось во входных данных.

## MLOps-концепты
DVC занимается версионированием датасетов и артефактов модели, чтобы воспроизводить обучение. В контексте проекта DVC позволил бы зафиксировать конкретную версию UCI_Credit_Card.csv и model_v1.joblib, model_v2.joblib так что любой член команды мог бы воспроизвести обучение
MLflow решает другую проблему, когда перебираются алгоритмы, удобно видеть все эксперименты в одном месте.

## ONNX-ML
Текущие модели сохранены в joblib. Для ускорения инференса и переносимости можно конвертировать модель в формат ONNX и запускать через ONNX Runtime.

## uWSGI + nginx
WSGI-сервер запускает Python-приложение в проде. Nginx работает как reverse proxy: балансировка, TLS-терминация, rate limiting.
В этом проекте для простоты в Docker используется gunicorn.
В докерфайле gunicorn запускается с --workers 2, чтобы обрабатывать несколько параллельных запросов.

## Бизнес-метрики
Ожидаемые финансовые потери: Expected Loss = sum(PD_i * EAD_i * LGD_i). PD_i вероятность дефолта клиента i по модели, EAD_i сумма под риском (Exposure at Default), LGD_i доля потерь при дефолте (Loss Given Default). Модель которая лучше предсказывает PD_i позволяет банку резервировать меньше капитала под те же заявки.
Вторая бизнес-метрика доля одобренных заявок при фиксированном уровне риска. При лимите дефолтов 5% банк одобрит больше заявок. 
Обе метрики рассчитываются на основе выходов модели  вероятностей дефолта default_probability и не требуют дополнительных данных помимо тех, что уже есть в ответе API.

## Docker
Сборка образа:
docker build -t credit-default-api:latest .

Запуск контейнера:
docker run --rm -p 5000:5000 credit-default-api:latest

Docker Hub:
https://hub.docker.com/r/tenjotsa/credit-default-api

## Docker Compose
Запуск:
docker compose up -d --build

Проверка:
http://127.0.0.1:5000/health

ML API напрямую: http://127.0.0.1:5000
Через nginx: http://127.0.0.1:8080

Проверка через nginx:
http://127.0.0.1:8080/health

Посмотреть access-логи nginx:
docker logs credit-default-nginx-compose

Остановка:
docker compose down

Выполнено:
Обучена и сохранена модель model_v1.joblib
Реализован Flask API
Добавлено JSON-логирование API
Добавлен requirements.txt
Добавлен и проверен Dockerfile
Добавлен docker-compose.yml
Добавлены model_v2
Добавлен план A/B теста
