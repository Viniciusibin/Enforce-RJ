from __future__ import annotations

import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "instance", "prj.db")


def get_connection() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _add_column_if_missing(conn: sqlite3.Connection, table: str, column: str, col_type: str) -> None:
    existing = {row[1] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}
    if column not in existing:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")


def init_db() -> None:
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS propostas (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            matricula       TEXT NOT NULL,
            valor_venda     REAL,
            fluxo           TEXT,
            quem_fez        TEXT,
            pendencia       TEXT,
            quem_pendencia  TEXT,
            obs             TEXT,
            created_at      TEXT DEFAULT (datetime('now'))
        );

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
    # Migrate existing databases with new columns
    for col, typ in [
        ("data_venda",         "TEXT"),
        ("valor_venda_total",  "REAL"),
        ("fluxo_venda",        "TEXT"),
        ("pendencia_venda",    "TEXT"),
        ("quem_pendencia_venda", "TEXT"),
    ]:
        _add_column_if_missing(conn, "imoveis", col, typ)
    conn.commit()
    conn.close()


def get_imovel_by_mat(mat: str) -> dict | None:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM imoveis WHERE TRIM(mat_tipo) = TRIM(?)", (mat,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


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


def get_all_propostas() -> list[dict]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM propostas ORDER BY id").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_proposta(proposta_id: int) -> dict | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM propostas WHERE id = ?", (proposta_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def insert_proposta(data: dict) -> int:
    allowed = {"matricula", "valor_venda", "fluxo", "quem_fez", "pendencia", "quem_pendencia", "obs"}
    columns = [c for c in data if c in allowed]
    placeholders = ", ".join("?" for _ in columns)
    sql = f"INSERT INTO propostas ({', '.join(columns)}) VALUES ({placeholders})"
    conn = get_connection()
    cur = conn.execute(sql, [data[c] for c in columns])
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def update_proposta(proposta_id: int, data: dict) -> bool:
    allowed = {"matricula", "valor_venda", "fluxo", "quem_fez", "pendencia", "quem_pendencia", "obs"}
    columns = [c for c in data if c in allowed]
    if not columns:
        return False
    set_clause = ", ".join(f"{c} = ?" for c in columns)
    sql = f"UPDATE propostas SET {set_clause} WHERE id = ?"
    conn = get_connection()
    cur = conn.execute(sql, [data[c] for c in columns] + [proposta_id])
    conn.commit()
    updated = cur.rowcount > 0
    conn.close()
    return updated


if __name__ == "__main__":
    init_db()
    print(f"Banco de dados inicializado em: {DB_PATH}")
