# dMAT-Engine
An learning and practise platform for dMAT students.


### Instructions:
Build project using docker, it will setup the fastapi server.

### Development Instructions:
install uv and run:
```fish
uv venv
```
Then perform:
```fish
uv add -r requirements.txt
```

Run:
```fish
source .venv/bin/activate.fish
```
finally:
```fish
uv run uvicorn app.main:app --reload
```
Make sure to run the database container before running backend locally:
```fish
docker compose -f docker-compose.dev.yaml up --build 
```
### Updating Package list:
```
 uv export --format requirements.txt > requirements.txt
```
### Updating DB Schema to date:
```
alembic upgrade head
```
