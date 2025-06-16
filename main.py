# Fazendo o parser dos argumentos passados na execução do script
from endpoints.services import app
import os
import uvicorn
from dotenv import load_dotenv

cwd = os.getcwd()
load_dotenv(dotenv_path=f"{cwd}/.env")

if __name__ == "__main__":
    uvicorn.run("endpoints.services:app", host="0.0.0.0", port=8000, reload=True)
