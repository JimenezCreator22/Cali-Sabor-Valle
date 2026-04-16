from datetime import date
import json
from pathlib import Path
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel


BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
RESERVAS_FILE = BASE_DIR / "reservas.json"

app = FastAPI(title="Backend Sabor Valle")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def cargar_reservas() -> List[dict]:
    if not RESERVAS_FILE.exists():
        return []

    try:
        with RESERVAS_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def guardar_reservas(reservas: List[dict]) -> None:
    with RESERVAS_FILE.open("w", encoding="utf-8") as file:
        json.dump(reservas, file, ensure_ascii=False, indent=2)


reservas_db: List[dict] = cargar_reservas()


class Reserva(BaseModel):
    nombre: str
    fecha: date
    hora: str
    personas: int


@app.get("/")
async def servir_inicio() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


@app.post("/api/reservas")
async def crear_reserva(reserva: Reserva):
    nueva_reserva = reserva.model_dump(mode="json")
    reservas_db.append(nueva_reserva)
    guardar_reservas(reservas_db)
    return {
        "mensaje": "Reserva confirmada",
        "codigo": f"RES-{len(reservas_db):04d}",
        "detalles": nueva_reserva,
    }


@app.get("/api/reservas")
async def ver_reservas():
    return reservas_db


app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR), name="frontend")
