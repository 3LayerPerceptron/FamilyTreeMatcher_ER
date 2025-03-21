# FamilyTreeMatcher Entity Resolution [New version]

Данный репозиторий явялется частью проекта Family Tree Matcher, которая отвечает за Entity Resolution

## How to use [via Docker]?

### Step 0

Необходимо установить Docker

### Step 1: Создание образа

Теперь необходимо скачать Dockerfile к себе на машину и выполнить команду:

```
sudo docker build -t family_matcher <Path to Dockerfile>
```
### Step 2: Запуск контейнера

```
sudo docker run -v <Host Path>:<Container Path> family_matcher <Needles Path (inside container)> <Haystack Path (inside container)> <Matches Path (inside container)>
```

### Step 2 Example:

```
sudo docker run -v <Host Path>:/data family_matcher /data/needles.json /data/haystack.json /data/matches.json
```

### Step 2 Notes:

Во избежание копирования больших объемов данных используется флаг -v. В примере выше, результат появится в папке по адресу <Host Path>.

### Method Notes:
1. From происходи с ubuntu.
2. В образе происходит клонирование репозитория.
3. В pip используется флаг --break-system-packages (Что не критично, т.к. действие происходит в контейнере, альтернативный способ, без подобного флага, привден ниже.)


## How to use [manually]?
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
