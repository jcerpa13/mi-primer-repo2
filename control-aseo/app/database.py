import sqlite3
from contextlib import contextmanager
from datetime import datetime

from .config import DB_PATH


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def get_db():
    conn = _connect()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_db() as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS sesiones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                encargado TEXT NOT NULL,
                area TEXT NOT NULL,
                hora_inicio TEXT NOT NULL,
                hora_fin TEXT,
                estado TEXT NOT NULL DEFAULT 'en_progreso',
                nivel_general TEXT
            )
            """
        )
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sesion_id INTEGER NOT NULL REFERENCES sesiones(id) ON DELETE CASCADE,
                nombre_item TEXT NOT NULL,
                foto_path TEXT,
                nivel TEXT,
                retroalimentacion TEXT,
                motor_ia TEXT,
                analizado_en TEXT,
                UNIQUE(sesion_id, nombre_item)
            )
            """
        )


def crear_sesion(encargado: str, area: str, checklist: list[str]) -> int:
    with get_db() as db:
        cur = db.execute(
            "INSERT INTO sesiones (encargado, area, hora_inicio, estado) VALUES (?, ?, ?, 'en_progreso')",
            (encargado, area, datetime.now().isoformat(timespec="seconds")),
        )
        sesion_id = cur.lastrowid
        for item in checklist:
            db.execute(
                "INSERT INTO items (sesion_id, nombre_item) VALUES (?, ?)",
                (sesion_id, item),
            )
        return sesion_id


def obtener_sesion(sesion_id: int):
    with get_db() as db:
        sesion = db.execute("SELECT * FROM sesiones WHERE id = ?", (sesion_id,)).fetchone()
        if not sesion:
            return None, []
        items = db.execute(
            "SELECT * FROM items WHERE sesion_id = ? ORDER BY id", (sesion_id,)
        ).fetchall()
        return sesion, items


def listar_sesiones():
    with get_db() as db:
        return db.execute("SELECT * FROM sesiones ORDER BY id DESC").fetchall()


def guardar_resultado_item(sesion_id: int, nombre_item: str, foto_path: str, nivel: str, retro: str, motor: str):
    with get_db() as db:
        db.execute(
            """
            UPDATE items
            SET foto_path = ?, nivel = ?, retroalimentacion = ?, motor_ia = ?, analizado_en = ?
            WHERE sesion_id = ? AND nombre_item = ?
            """,
            (foto_path, nivel, retro, motor, datetime.now().isoformat(timespec="seconds"), sesion_id, nombre_item),
        )


def finalizar_sesion(sesion_id: int, nivel_general: str):
    with get_db() as db:
        db.execute(
            "UPDATE sesiones SET hora_fin = ?, estado = 'finalizado', nivel_general = ? WHERE id = ?",
            (datetime.now().isoformat(timespec="seconds"), nivel_general, sesion_id),
        )
