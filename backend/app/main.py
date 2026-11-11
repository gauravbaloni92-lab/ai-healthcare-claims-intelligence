from fastapi import FastAPI

app = FastAPI(
    title="AI Healthcare Claims Intelligence",
    description="Healthcare Benefits and Claims Adjudication Ecosystem",
    version="1.0.0"
)

@app.get("/")
def home():
    return {
        "message": "Welcome to AI Healthcare Claims Intelligence Ecosystem",
        "status": "Running",
        "project": "Healthcare Benefits Automation"
    }

@app.get("/health")
def health_check():
    return {
        "status": "Healthy",
        "service": "Healthcare Claims API"
    }