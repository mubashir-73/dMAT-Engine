# dMAT-Engine
An learning and practise platform for dMAT students.


# Instructions:
Build project using docker, it will setup the fastapi server.

# Development Instructions:
install uv and run:
```
uv venv
```
Then perform:
```
uv add -r requirements.txt
```

Run:
```
source .venv/bin/activate.fish
```
finally:
```
uv run uvicorn app.main:app --reload
```

