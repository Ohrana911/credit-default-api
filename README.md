Целевая переменная: default.payment.next.month<br>

## Структура проекта
data/ - исходные данные<br>
models/ - сохраненные модели<br>
src/ - исходный код<br>
tests/ - тесты<br>
nginx/ - конфигурация nginx<br>
docs/ - доп. документация (здесь план AB теста)<br>

## Модели, метрики и порог решения
В проекте сравниваются две разные модели:<br>
v1: LogisticRegression + StandardScaler смотреть src/train.py, артефакт models/model_v1.joblib<br>
v2: RandomForestClassifier смотреть src/train_v2.py, артефакт models/model_v2.joblib<br>

### Обучение
Данные делим 80/20 (train_test_split, stratify=y, random_state=42)<br>
Для первой версии v1 используем pipeline: масштабирование и логистическая регрессия<br>
Классы несбалансированы, поэтому для второй v2 добавлен class_weight=balanced<br>

### Метрики
Логистическая регрессия: F1 = 0.3553, Precision = 0.6868, Recall = 0.2396<br>
RandomForestClassifier: F1 = 0.5407, Precision = 0.5248, Recall = 0.5576<br>
Accuracy намеренно не используется как основная метрика, потому что при несбалансированных классах она вводит в заблуждение, такая модель, которая всегда предсказывает "нет дефолта", получила высокий accuracy, но она бесполезна. Поэтому основной метрикой выбран F1-score, гармоническое среднее между Precision и <br>Recall, которое штрафует модель за плохую работу с любым из классов. А вот версия v2 значительно превосходит первую по F1 и Recall, что означает: она находит в 2.3 раза больше реальных должников.<br>

### Порог и почему он такой
В API бинарное решение принимается по стандартному порогу: prediction = 1, если вероятность дефолта P(default) >= 0.5, иначе 0<br>
0.5 самый простой и воспроизводимый бейзлайн без подбора порога по бизнес затратам. В реальном банке порог таким не будет<br>

## Формат API
### GET /health
Ответ:<br>
json<br>
{"status":"ok"}<br>

### POST /predict
Обязательные поля: все признаки клиента из датасета кроме ID и целевой.<br>
Необязательное поле (без указания будет использоваться лог. регрессия):<br>
model_version: v1 или v2<br>

Ответ:<br>
json<br>
{<br>
  "model_version": "v1",<br>
  "prediction": 0,<br>
  "default_probability": 0.222334<br>
}<br>

Ошибки:<br>
400 если body не JSON<br>
400 если не хватает полей<br>
400 если передан неверный model_version (если вообще передан)<br>

## Обучение моделей<br>
v1:<br>
python src/train.py<br>
<br>
v2:<br>
python src/train_v2.py<br>
<br>
## Запуск локально<br>
python -m venv .venv<br>
.venv\Scripts\activate<br>
pip install -r requirements.txt<br>
python src/train.py<br>
python src/train_v2.py<br>
python src/api.py<br>
<br>
<img width="566" height="123" alt="Снимок экрана 2026-05-03 045753" src="https://github.com/user-attachments/assets/70cca961-f96a-4c17-ac81-6389d50f2131" />

<br>
## Автотесты<br>
Проект включает базовые автотесты через pytest для проверки корректности API. Тесты покрывают эндпоинты /health, /predict а так же отсутствующие поля и неверный model_version<br>

<img width="457" height="248" alt="Снимок экрана 2026-05-03 045805" src="https://github.com/user-attachments/assets/544be62b-402c-4b14-93dc-be59a4fd6d99" /><br>

## Примеры API-запросов
Проверка сервиса:<br>
http://127.0.0.1:5000/health<br>
<br>
Предикт:<br>
 -X POST http://127.0.0.1:5000/predict ^<br>
  -H "Content-Type: application/json" ^<br>
  -d "<br>{\"LIMIT_BAL\":20000,\"SEX\":2,\"EDUCATION\":2,\"MARRIAGE\":1,\"AGE\":24,\"PAY_0\":2,\"PAY_2\":2,\"PAY_3\":-1,\"PAY_4\":-1,\"PAY_5\":-2,\"PAY_6\":-2,\"BILL_AMT1\":3913,\"BILL_AMT2\":3102,\"BILL_AMT3\":689,\"BILL_AMT4\":0,\"BILL_AMT5\":0,\"BILL_AMT6\":0,\"PAY_AMT1\":0,\"PAY_AMT2\":689,\"PAY_AMT3\":0,\"PAY_AMT4\":0,\"PAY_AMT5\":0,\"PAY_AMT6\":0}"<br>

Предикт для модели v2:<br>
 -X POST http://127.0.0.1:5000/predict ^<br>
  -H "Content-Type: application/json" ^<br>
  -d "<br>{\"model_version\":\"v2\",\"LIMIT_BAL\":20000,\"SEX\":2,\"EDUCATION\":2,\"MARRIAGE\":1,\"AGE\":24,\"PAY_0\":2,\"PAY_2\":2,\"PAY_3\":-1,\"PAY_4\":-1,\"PAY_5\":-2,\"PAY_6\":-2,\"BILL_AMT1\":3913,\"BILL_AMT2\":3102,\"BILL_AMT3\":689,\"BILL_AMT4\":0,\"BILL_AMT5\":0,\"BILL_AMT6\":0,\"PAY_AMT1\":0,\"PAY_AMT2\":689,\"PAY_AMT3\":0,\"PAY_AMT4\":0,\"PAY_AMT5\":0,\"PAY_AMT6\":0}"<br>

## A/B
### Демонстрация тестовой модели v2 и явного выбора версии
<img width="984" height="397" alt="Снимок экрана 2026-05-02 202413" src="https://github.com/user-attachments/assets/a4a1505c-1da8-40fd-926b-be70ee2b25d4" />
<br>

### Демонстрация контрольной модели v1 и явного выбора версии
<img width="970" height="395" alt="Снимок экрана 2026-05-02 202423" src="https://github.com/user-attachments/assets/2257f437-ab7c-4084-aed9-ce0b059095f8" />
<br>

### Дефолтная модель. Ответ API без явной версии
<img width="970" height="265" alt="Снимок экрана 2026-05-02 190644" src="https://github.com/user-attachments/assets/849691fd-74b3-422e-b74c-5ffa51419d16" />
<br>

### Базовая проверка, что сервис запущен и отвечает
<img width="982" height="433" alt="Снимок экрана 2026-05-02 190729" src="https://github.com/user-attachments/assets/3de17aea-441b-4928-9059-209a8eea9cbb" />
<br>

### Негативный тест валидации входных данных
<img width="978" height="781" alt="Снимок экрана 2026-05-02 190805" src="https://github.com/user-attachments/assets/5dc87c8c-9735-496b-bddd-eccb4f6fe0a9" />
<br>

## План A/B теста
Cмотреть docs/AB_TEST_PLAN.md<br>

## Архитектурное обоснование
В проекте выбран монолитный подход:<br>
1. один Flask сервис проще разрабатывать и поддерживать, задания можно выполнить спокойно все "в одном месте"<br>
2. меньше инфраструктурной сложности с настройкой межсервисного взаимодействия<br>

Когда стоит переходить к микросервисам:<br>
1. если отдельно масштабируется инференс, логирование, feature-processing или batch-prediction<br>
2. если несколько команд независимо развивают части платформы<br>
3. когда есть деньги<br>

## Брокеры сообщения
В контексте данного проекта например простой (моя субъективная оценка) RabbitMQ мог бы использоваться для асинхронной пакетной обработки заявок на скоринг, для организации очереди на пересчёт рейтинга клиентов при обновлении модели, для асинхронной отправки логов и событий в аналитические системы. API отвечал бы мгновенно, а тяжёлые вычисления уходили в фон и не блокировали юзера.<br>

## Логирование и мониторинг
1. Сейчас API пишет JSON-логи в stdout, так удобно сделать для докера, контейнер сам не знает куда писать логи, это решает инфраструктура снаружи<br>
2. Логируются путь, метод, статус, request/response, время ответа<br>
3. В проде логи из stdout собирались бы централизованно. Стандартный подход через стек ELK (Elasticsearch, Logstash, Kibana) или его аналог OpenSearch. Логи из stdout я бы собирал через filebeat, он умеет читать вывод контейнеров без изменений в коде. Дальше Elasticsearch, Kibana сверху для дашбордов. Главное что нужно видеть что если доля предсказаний дефолта по времени резко меняется, значит что то не так со входными данными, тогда становится видно сразу: сколько запросов, сколько ошибок, как распределились предсказания. Помимо логов, в production важно отслеживать метрики самого сервиса в реальном времени. Для этого используют связку Prometheus и Grafana. Prometheus опрашивает /metrics раз в несколько секунд и пишет временные ряды. Grafana для визуализация и алерты. Конкретно для этого проекта важен один алерт, если доля prediction=1 за час выросла в два раза значит скорее всего что то сломалось во входных данных.

## MLOps-концепты
DVC занимается версионированием датасетов и артефактов модели, чтобы воспроизводить обучение. В контексте проекта DVC позволил бы зафиксировать конкретную версию UCI_Credit_Card.csv и model_v1.joblib, model_v2.joblib так что любой член команды мог бы воспроизвести обучение<br>
MLflow решает другую проблему, когда перебираются алгоритмы, удобно видеть все эксперименты в одном месте.<br>

## ONNX-ML
Текущие модели сохранены в joblib. Для ускорения инференса и переносимости можно конвертировать модель в формат ONNX и запускать через ONNX Runtime.<br>

## uWSGI + nginx
WSGI-сервер запускает Python-приложение в проде. Nginx работает как reverse proxy: балансировка, TLS-терминация, rate limiting.<br>
В этом проекте для простоты в Docker используется gunicorn.<br>
В докерфайле gunicorn запускается с --workers 2, чтобы обрабатывать несколько параллельных запросов.<br>

## Бизнес-метрики
Ожидаемые финансовые потери: Expected Loss = sum(PD_i * EAD_i * LGD_i). PD_i вероятность дефолта клиента i по модели, EAD_i сумма под риском (Exposure at Default), LGD_i доля потерь при дефолте (Loss Given Default). Модель которая лучше предсказывает PD_i позволяет банку резервировать меньше капитала под те же заявки.<br>
Вторая бизнес-метрика доля одобренных заявок при фиксированном уровне риска. При лимите дефолтов 5% банк одобрит больше заявок. <br>
Обе метрики рассчитываются на основе выходов модели  вероятностей дефолта default_probability и не требуют дополнительных данных помимо тех, что уже есть в ответе API.<br>

## Docker
Скачивание образа:<br>
docker pull tenjotsa/credit-default-api:latest<br>
<img width="783" height="173" alt="Снимок экрана 2026-05-03 050205" src="https://github.com/user-attachments/assets/6ef5d07b-a68d-44d7-8c28-79b7622675bb" />

Сборка образа:<br>
docker build -t credit-default-api:latest .<br>
<img width="841" height="429" alt="Снимок экрана 2026-05-03 050745" src="https://github.com/user-attachments/assets/5fb7edc0-bc73-4360-8e90-bdabc673fca3" />

Запуск контейнера:<br>
docker run --rm -p 5000:5000 credit-default-api:latest<br>
<img width="797" height="191" alt="Снимок экрана 2026-05-03 050735" src="https://github.com/user-attachments/assets/560b3473-39ae-4ca4-9721-ed43d3301e9b" />

Docker Hub:<br>
https://hub.docker.com/r/tenjotsa/credit-default-api<br>

## Docker Compose
Запуск:<br>
docker compose up -d --build<br>
<img width="840" height="721" alt="Снимок экрана 2026-05-03 050812" src="https://github.com/user-attachments/assets/17bfce8a-dde3-4e84-9b1f-07fd4a9d0380" />

Проверка:<br>
http://127.0.0.1:5000/health<br>
<img width="970" height="265" alt="Снимок экрана 2026-05-02 190644" src="https://github.com/user-attachments/assets/70fa4235-7399-4f72-8834-306e6a5ed460" />

ML API напрямую: http://127.0.0.1:5000<br>
Через nginx: http://127.0.0.1:8080<br>

Проверка через nginx:<br>
http://127.0.0.1:8080/health<br>

<img width="1960" height="589" alt="Снимок экрана 2026-05-03 002342" src="https://github.com/user-attachments/assets/9f04c06b-6d20-40b5-82c2-c3b406d084d2" />

<br>
Посмотреть access-логи nginx:<br>
docker logs credit-default-nginx-compose<br>

Остановка:<br>
docker compose down<br>

## Скриншоты из Docker Desktop и Docker Hub

### образ опубликован и доступен для скачивания по docker pull
<img width="970" height="815" alt="Снимок экрана 2026-05-02 204338" src="https://github.com/user-attachments/assets/2dad7f78-d8d0-4eee-bd5c-cbe092f21c8d" />

### продакшн запуск, gunicorn, демонстрация двух версий модели через API
<img width="988" height="839" alt="Снимок экрана 2026-05-02 202806" src="https://github.com/user-attachments/assets/44f00c07-29f6-4379-a82f-f0aa51b88107" />

### контейнер реально запущен на хосте, API доступен локально на порту 5000
<img width="983" height="349" alt="Снимок экрана 2026-05-02 202732" src="https://github.com/user-attachments/assets/7ff14194-8ec2-4d2d-93c4-81aa53977d67" />

### запросы идут через reverse‑proxy на 8080, на edge фиксируются access‑логи, upstream отвечает 200
<img width="1960" height="589" alt="Снимок экрана 2026-05-03 002342" src="https://github.com/user-attachments/assets/59ead112-cc27-45f6-98f0-68bf4b9a2357" />


# Выполнено:
- Обучена и сохранена модель model_v1.joblib
- Реализован Flask API
- Добавлено JSON-логирование API
- Добавлен requirements.txt
- Добавлен и проверен Dockerfile
- Добавлен docker-compose.yml
- Добавлены model_v2
- Добавлен план A/B теста
