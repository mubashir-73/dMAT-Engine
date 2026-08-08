from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "dMAT API is running"}
