# Django + restapi

## Установка проекта
### Создать виртуальное окружение
```
virtualenv -p python3 .venv
```
### активация виртального окружения:
```
source .venv/bin/activate

```
### Устанавливаем зависимости
```
pip install -r requirements.txt
```
### Создать базу postgresql
```
Название базы: djangoproject
Далее применяем миграции: python manage.py migrate
```

### Запуск проекта
```
python manage.py runserver
```

### В проекте
```
Список пользователей /api/users/ (для примера)
Настройки:
Serializers - core.serializers
Views - core.views
Models - core.views
Routers - _project_.routers
```
