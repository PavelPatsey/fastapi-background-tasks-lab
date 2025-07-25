### Основные команды
1. **Создать новую миграцию**
   ```bash
   alembic revision --autogenerate -m "your migration description"
   ```
2. **Применить миграции** к базе данных:
   ```bash
   alembic upgrade head
   ```
3. **Отметить текущее состояние** базы как соответствующее последней ревизии
   ```bash
   alembic stamp head
   ```
