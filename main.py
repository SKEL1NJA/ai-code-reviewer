from fastapi import FastAPI

app = FastAPI(title="AI Code Reviewer")

@app.get("/")
def read_root():
    return {"status": "AI Code Reviewer is running"}