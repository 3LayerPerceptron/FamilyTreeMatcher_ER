# FamilyTreeMatcher Entity Resolution [New version]

Данный репозиторий явялется частью проекта Family Tree Matcher, которая отвечает за Entity Resolution

## How to use?
Все шаги происходят в основной директории репозитория

### Step 0

Необходимо установить python 3.12

### Step 1: Создание виртуальной среды (можно пропустить, если у вас есть виртуальное окружение)
```
python3 -m venv FTMER
```
```
source ~/FTMER/bin/activate
```
### Step 2: Установка зависимостей
```
python3 -m pip install -r requirements.txt
```

### Step 3: Получение мэтчей
После шага 2 запустите основной скрипт, который в формате json выдаст полученные мэтчи.
```
python3 FTM_ER.py ./genotek_tree_1.json ./genotek_tree_2.json ./matches.json
```
