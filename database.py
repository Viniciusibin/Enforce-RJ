from __future__ import annotations

import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "instance", "prj.db")


def get_connection() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS imoveis (
            id                      INTEGER PRIMARY KEY AUTOINCREMENT,

            -- Identificação
            mat_tipo                TEXT,
            tipologia               TEXT,
            cidade                  TEXT,
            estado                  TEXT,

            -- Tombamento
            vf_tombamento           REAL,
            vm_tombamento           REAL,
            resultado_localizacao   TEXT,

            -- Terreno
            area_terreno            REAL,
            unid_area_terreno       TEXT,
            cidade_imovel           TEXT,

            -- Classificação
            classe_imovel           TEXT,
            tipo_imovel             TEXT,

            -- Valores
            valor_avaliacao         REAL,
            valor_venda_forcada     REAL,
            valor_venda_forcada_vp  REAL,

            -- Laudos
            laudo_avaliacao_lideratu TEXT,
            lideratu_arquivo         TEXT,
            laudo_vm_sistema         TEXT,
            laudo_vf_sistema         TEXT,

            -- Enforce
            nivel                   TEXT,
            vm_enforce              REAL,
            vf_enforce              REAL,
            vf_laudo                REAL,
            dt_laudo                TEXT,
            obs                     TEXT,

            -- Tarefa atual
            status_tarefa           TEXT,
            dt_criacao_tarefa       TEXT,
            vf_laudo_att            REAL,

            -- Status geral
            status                  TEXT,
            obs_status              TEXT,

            -- Comercial
            tabela_gi               TEXT,
            proposta                TEXT,
            natureza                TEXT,
            valor_garantia          REAL,
            comprador               TEXT,
            previsao_registro       TEXT,

            -- Geolocalização
            lat                     REAL,
            lng                     REAL
        );
    """)
    conn.commit()
    conn.close()


def get_all_imoveis() -> list[dict]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM imoveis ORDER BY id").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_imovel(imovel_id: int) -> dict | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM imoveis WHERE id = ?", (imovel_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def insert_imovel(data: dict) -> int:
    columns = [c for c in data if c != "id"]
    placeholders = ", ".join("?" for _ in columns)
    sql = f"INSERT INTO imoveis ({', '.join(columns)}) VALUES ({placeholders})"
    conn = get_connection()
    cur = conn.execute(sql, [data[c] for c in columns])
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def update_imovel(imovel_id: int, data: dict) -> bool:
    columns = [c for c in data if c != "id"]
    set_clause = ", ".join(f"{c} = ?" for c in columns)
    sql = f"UPDATE imoveis SET {set_clause} WHERE id = ?"
    conn = get_connection()
    cur = conn.execute(sql, [data[c] for c in columns] + [imovel_id])
    conn.commit()
    updated = cur.rowcount > 0
    conn.close()
    return updated


def delete_imovel(imovel_id: int) -> bool:
    conn = get_connection()
    cur = conn.execute("DELETE FROM imoveis WHERE id = ?", (imovel_id,))
    conn.commit()
    deleted = cur.rowcount > 0
    conn.close()
    return deleted


if __name__ == "__main__":
    init_db()
    print(f"Banco de dados inicializado em: {DB_PATH}")
