export PYTHONPATH=.
# обновляем версию базы до последней
alembic upgrade head 
# запускаем сервер
python main.py