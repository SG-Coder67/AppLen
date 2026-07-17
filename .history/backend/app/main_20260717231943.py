from fastapi import FastAPI
app=FastAPI(title="AppLen API");
@app.get("/")
def root():
    return {"message": "Welcome to AppLen API"}