from __future__ import annotations

import os
from datetime import date, datetime
from flask import Flask, jsonify, render_template, request, send_from_directory

import database

app = Flask(__name__)

database.init_db()

STANDARD_DOCS = [
    ("PRC", "Plano de Recuperacao de Credito"),
    ("QGC", "Quadro Geral dos Credores"),
    ("RMA", "Relatorio Mensal de Atividade"),
    ("IDPJ", "Incidente de Desconsideracao da Personalidade Juridica"),
    ("PRECIFICACAO", "Precificacao do Credito"),
    ("PPT", "Apresentacao PowerPoint"),
]


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


CASES = [
    {
        "case_id": "RJ-001",
        "name": "Usina Atlantica S.A.",
        "carteira": "Distressed Energy",
        "valor_credito": 185_000_000,
        "qgc_total_mm": 4100,
        "face_mm": 185,
        "qgc_mm": 4100,
        "cost_mm": 138,
        "mtm_mm": 152,
        "erv_mm": 166,
        "npv_mm": 161,
        "prazo_estimado_anos": 5.2,
        "prazo_remanescente_anos": 3.8,
        "pnl_target": 12.5,
        "pnl_sem_np": 9.4,
        "rj_phase": "Plano homologado",
        "class": "Quirografario",
        "pct_class_i": 0,
        "pct_class_ii": 0,
        "pct_class_iii": 78,
        "valor_extra": 14_500_000,
        "documentos_faltando": ["Ata de AGC", "Balancete 2026"],
        "agc_date": "2026-04-16",
        "status_tag": "Execucao de plano",
        "am_update_tag": "Atrasado",
        "pm": "VBI",
    },
    {
        "case_id": "RJ-002",
        "name": "Varejo Central Ltda.",
        "carteira": "Special Situations",
        "valor_credito": 72_000_000,
        "qgc_total_mm": 860,
        "face_mm": 72,
        "qgc_mm": 860,
        "cost_mm": 54,
        "mtm_mm": 58,
        "erv_mm": 63,
        "npv_mm": 60,
        "prazo_estimado_anos": 3.1,
        "prazo_remanescente_anos": 2.4,
        "pnl_target": 8.1,
        "pnl_sem_np": 6.8,
        "rj_phase": "Assembleia convocada",
        "class": "ME/EPP",
        "pct_class_i": 0,
        "pct_class_ii": 22,
        "pct_class_iii": 58,
        "valor_extra": 2_100_000,
        "documentos_faltando": [],
        "agc_date": "2026-04-30",
        "status_tag": "Aguardando AGC",
        "am_update_tag": "Em dia",
        "pm": "VBI",
    },
    {
        "case_id": "RJ-003",
        "name": "Construtora Horizonte S.A.",
        "carteira": "Real Estate Distressed",
        "valor_credito": 248_000_000,
        "qgc_total_mm": 5300,
        "face_mm": 248,
        "qgc_mm": 5300,
        "cost_mm": 190,
        "mtm_mm": 201,
        "erv_mm": 223,
        "npv_mm": 214,
        "prazo_estimado_anos": 6.0,
        "prazo_remanescente_anos": 5.1,
        "pnl_target": 15.9,
        "pnl_sem_np": 11.1,
        "rj_phase": "Verificacao de creditos",
        "class": "Garantia real",
        "pct_class_i": 0,
        "pct_class_ii": 51,
        "pct_class_iii": 39,
        "valor_extra": 8_800_000,
        "documentos_faltando": ["QGC consolidado", "Parecer juridico"],
        "agc_date": None,
        "status_tag": "Em diligencia",
        "am_update_tag": "Sem atualizacao 15+ dias",
        "pm": "IBI",
    },
    {
        "case_id": "RJ-004",
        "name": "Logistica Sul BR S.A.",
        "carteira": "Infra Credito",
        "valor_credito": 95_000_000,
        "qgc_total_mm": 1420,
        "face_mm": 95,
        "qgc_mm": 1420,
        "cost_mm": 76,
        "mtm_mm": 81,
        "erv_mm": 89,
        "npv_mm": 84,
        "prazo_estimado_anos": 4.4,
        "prazo_remanescente_anos": 2.9,
        "pnl_target": 10.2,
        "pnl_sem_np": 7.6,
        "rj_phase": "Cumprimento de obrigacoes",
        "class": "Quirografario",
        "pct_class_i": 0,
        "pct_class_ii": 0,
        "pct_class_iii": 81,
        "valor_extra": 3_300_000,
        "documentos_faltando": ["Comprovante de pagamento classe III"],
        "agc_date": "2026-05-08",
        "status_tag": "Monitoring",
        "am_update_tag": "Em dia",
        "pm": "IBI",
    },
    {
        "case_id": "RJ-005",
        "name": "Hospital Vida Plena",
        "carteira": "Healthcare",
        "valor_credito": 41_000_000,
        "qgc_total_mm": 980,
        "face_mm": 41,
        "qgc_mm": 980,
        "cost_mm": 31,
        "mtm_mm": 34,
        "erv_mm": 36,
        "npv_mm": 35,
        "prazo_estimado_anos": 2.8,
        "prazo_remanescente_anos": 1.2,
        "pnl_target": 7.4,
        "pnl_sem_np": 5.7,
        "rj_phase": "Encerramento",
        "class": "Trabalhista",
        "pct_class_i": 12,
        "pct_class_ii": 6,
        "pct_class_iii": 22,
        "valor_extra": 900_000,
        "documentos_faltando": [],
        "agc_date": None,
        "status_tag": "Fechamento",
        "am_update_tag": "Em dia",
        "pm": "VBI",
    },
    {
        "case_id": "RJ-006",
        "name": "Agro Norte Cooperativa",
        "carteira": "Agro Distressed",
        "valor_credito": 126_000_000,
        "qgc_total_mm": 3100,
        "face_mm": 126,
        "qgc_mm": 3100,
        "cost_mm": 99,
        "mtm_mm": 108,
        "erv_mm": 117,
        "npv_mm": 112,
        "prazo_estimado_anos": 4.8,
        "prazo_remanescente_anos": 4.0,
        "pnl_target": 11.8,
        "pnl_sem_np": 8.9,
        "rj_phase": "Assembleia convocada",
        "class": "Garantia real",
        "pct_class_i": 0,
        "pct_class_ii": 48,
        "pct_class_iii": 34,
        "valor_extra": 4_200_000,
        "documentos_faltando": ["Plano atualizado"],
        "agc_date": "2026-04-22",
        "status_tag": "Aguardando AGC",
        "am_update_tag": "Em dia",
        "pm": "KPT",
    },
    {
        "case_id": "RJ-007",
        "name": "Tecelagem Aurora S.A.",
        "carteira": "Industrial Turnaround",
        "valor_credito": 58_000_000,
        "qgc_total_mm": 740,
        "face_mm": 58,
        "qgc_mm": 740,
        "cost_mm": 45,
        "mtm_mm": 44,
        "erv_mm": 50,
        "npv_mm": 47,
        "prazo_estimado_anos": 3.7,
        "prazo_remanescente_anos": 2.6,
        "pnl_target": 9.2,
        "pnl_sem_np": 4.3,
        "rj_phase": "Impugnacoes",
        "class": "Quirografario",
        "pct_class_i": 0,
        "pct_class_ii": 0,
        "pct_class_iii": 76,
        "valor_extra": 1_300_000,
        "documentos_faltando": ["Relatorio AM", "Peticao de impugnacao"],
        "agc_date": None,
        "status_tag": "Contencioso",
        "am_update_tag": "Atrasado",
        "pm": "IBI",
    },
    {
        "case_id": "RJ-008",
        "name": "Rede Mercurio de Farmacias",
        "carteira": "Healthcare",
        "valor_credito": 89_000_000,
        "qgc_total_mm": 1650,
        "face_mm": 89,
        "qgc_mm": 1650,
        "cost_mm": 70,
        "mtm_mm": 74,
        "erv_mm": 80,
        "npv_mm": 77,
        "prazo_estimado_anos": 4.2,
        "prazo_remanescente_anos": 3.2,
        "pnl_target": 10.6,
        "pnl_sem_np": 6.1,
        "rj_phase": "Plano homologado",
        "class": "ME/EPP",
        "pct_class_i": 3,
        "pct_class_ii": 19,
        "pct_class_iii": 41,
        "valor_extra": 2_900_000,
        "documentos_faltando": [],
        "agc_date": "2026-05-14",
        "status_tag": "Execucao de plano",
        "am_update_tag": "Em dia",
        "pm": "VBI",
    },
    {
        "case_id": "RJ-009",
        "name": "Metalurgica Delta Ltda.",
        "carteira": "Industrial Turnaround",
        "valor_credito": 134_000_000,
        "qgc_total_mm": 2700,
        "face_mm": 134,
        "qgc_mm": 2700,
        "cost_mm": 101,
        "mtm_mm": 96,
        "erv_mm": 104,
        "npv_mm": 99,
        "prazo_estimado_anos": 5.0,
        "prazo_remanescente_anos": 4.4,
        "pnl_target": 13.4,
        "pnl_sem_np": 3.7,
        "rj_phase": "Verificacao de creditos",
        "class": "Quirografario",
        "pct_class_i": 0,
        "pct_class_ii": 0,
        "pct_class_iii": 84,
        "valor_extra": 5_100_000,
        "documentos_faltando": ["Laudo de avaliacao"],
        "agc_date": "2026-04-10",
        "status_tag": "Em diligencia",
        "am_update_tag": "Sem atualizacao 15+ dias",
        "pm": "KPT",
    },
    {
        "case_id": "RJ-010",
        "name": "Porto Azul Operadora",
        "carteira": "Infra Credito",
        "valor_credito": 210_000_000,
        "qgc_total_mm": 6200,
        "face_mm": 210,
        "qgc_mm": 6200,
        "cost_mm": 171,
        "mtm_mm": 186,
        "erv_mm": 194,
        "npv_mm": 190,
        "prazo_estimado_anos": 6.4,
        "prazo_remanescente_anos": 5.8,
        "pnl_target": 14.7,
        "pnl_sem_np": 10.9,
        "rj_phase": "Cumprimento de obrigacoes",
        "class": "Garantia real",
        "pct_class_i": 0,
        "pct_class_ii": 57,
        "pct_class_iii": 33,
        "valor_extra": 9_600_000,
        "documentos_faltando": [],
        "agc_date": None,
        "status_tag": "Monitoring",
        "am_update_tag": "Em dia",
        "pm": "IBI",
    },
    {
        "case_id": "RJ-011",
        "name": "Educacional Horizonte",
        "carteira": "Special Situations",
        "valor_credito": 67_000_000,
        "qgc_total_mm": 1220,
        "face_mm": 67,
        "qgc_mm": 1220,
        "cost_mm": 52,
        "mtm_mm": 59,
        "erv_mm": 62,
        "npv_mm": 60,
        "prazo_estimado_anos": 3.3,
        "prazo_remanescente_anos": 2.5,
        "pnl_target": 9.9,
        "pnl_sem_np": 7.2,
        "rj_phase": "Assembleia convocada",
        "class": "Trabalhista",
        "pct_class_i": 18,
        "pct_class_ii": 7,
        "pct_class_iii": 26,
        "valor_extra": 1_100_000,
        "documentos_faltando": ["Ata de comite"],
        "agc_date": "2026-04-27",
        "status_tag": "Aguardando AGC",
        "am_update_tag": "Atrasado",
        "pm": "VBI",
    },
    {
        "case_id": "RJ-012",
        "name": "Transporte Rota Certa",
        "carteira": "Infra Credito",
        "valor_credito": 39_000_000,
        "qgc_total_mm": 690,
        "face_mm": 39,
        "qgc_mm": 690,
        "cost_mm": 30,
        "mtm_mm": 33,
        "erv_mm": 36,
        "npv_mm": 34,
        "prazo_estimado_anos": 2.2,
        "prazo_remanescente_anos": 1.6,
        "pnl_target": 6.9,
        "pnl_sem_np": 5.2,
        "rj_phase": "Encerramento",
        "class": "ME/EPP",
        "pct_class_i": 4,
        "pct_class_ii": 12,
        "pct_class_iii": 29,
        "valor_extra": 650_000,
        "documentos_faltando": [],
        "agc_date": "2026-04-06",
        "status_tag": "Fechamento",
        "am_update_tag": "Em dia",
        "pm": "KPT",
    },
]


def dashboard_payload() -> dict:
    today = date.today()
    next_month = 1 if today.month == 12 else today.month + 1
    next_month_year = today.year + 1 if next_month == 1 else today.year

    normalized_cases = []
    for case in CASES:
        c = dict(case)
        c["agc_date_obj"] = parse_date(c["agc_date"])
        c["has_missing_docs"] = len(c["documentos_faltando"]) > 0
        c["missing_agc"] = c["agc_date_obj"] is None
        c["am_delayed"] = "atras" in c["am_update_tag"].lower() or "15+" in c["am_update_tag"]
        c["agc_next_month"] = (
            c["agc_date_obj"] is not None
            and c["agc_date_obj"].month == next_month
            and c["agc_date_obj"].year == next_month_year
        )
        # Mock deterministic document inventory by case id.
        case_number = int(c["case_id"].split("-")[1])
        docs = []
        for idx, (sigla, descricao) in enumerate(STANDARD_DOCS):
            if (case_number + idx) % 4 != 0:
                docs.append(
                    {
                        "id": f"{c['case_id']}-{sigla}",
                        "sigla": sigla,
                        "nome": descricao,
                        "arquivo": f"{c['case_id']}_{sigla}.pdf",
                    }
                )
        c["documentos_presentes"] = docs
        normalized_cases.append(c)

    total_cases = len(normalized_cases)
    missing_docs_cases = sum(1 for c in normalized_cases if c["has_missing_docs"])
    missing_agc_cases = sum(1 for c in normalized_cases if c["missing_agc"])
    delayed_am_cases = sum(1 for c in normalized_cases if c["am_delayed"])
    total_credito = sum(c["valor_credito"] for c in normalized_cases)
    next_month_agc = [c for c in normalized_cases if c["agc_next_month"]]

    return {
        "kpis": {
            "total_cases": total_cases,
            "missing_docs_cases": missing_docs_cases,
            "missing_agc_cases": missing_agc_cases,
            "delayed_am_cases": delayed_am_cases,
            "total_credito": total_credito,
        },
        "cases": normalized_cases,
        "next_month_agc": next_month_agc,
        "reference_date": today.isoformat(),
    }


@app.route("/")
def index():
    return send_from_directory(
        os.path.join(app.root_path, "dashboard_rafa"), "index.html"
    )


@app.route("/<path:filename>")
def serve_dashboard_static(filename):
    return send_from_directory(
        os.path.join(app.root_path, "dashboard_rafa"), filename
    )


@app.route("/casos")
def casos_dashboard():
    return render_template("index.html")


@app.route("/api/imoveis")
def api_imoveis():
    def to_float(v):
        if v is None:
            return None
        try:
            return float(v)
        except (ValueError, TypeError):
            return None

    rows = database.get_all_imoveis()
    properties = [
        {
            "mat":              row.get("mat_tipo"),
            "tipologia":        row.get("tipologia"),
            "cidade":           row.get("cidade"),
            "estado":           row.get("estado"),
            "tipo":             row.get("tipo_imovel"),
            "vm":               to_float(row.get("vm_enforce")),
            "vf":               to_float(row.get("vf_enforce")),
            "area":             to_float(row.get("area_terreno")),
            "unidade":          row.get("unid_area_terreno"),
            "nivel":            row.get("nivel"),
            "localizacao":      row.get("resultado_localizacao"),
            "status":           row.get("status_tarefa"),
            "statusVenda":      row.get("status"),
            "obs":              row.get("obs"),
            "tabelaGI":         row.get("tabela_gi"),
            "proposta":         to_float(row.get("proposta")),
            "comprador":        row.get("comprador"),
            "previsaoRegistro": row.get("previsao_registro"),
            "lat":              to_float(row.get("lat")),
            "lng":              to_float(row.get("lng")),
            "dataVenda":        row.get("data_venda"),
            "valorVendaTotal":  to_float(row.get("valor_venda_total")),
            "fluxoVenda":       row.get("fluxo_venda"),
            "pendenciaVenda":   row.get("pendencia_venda"),
            "quemPendenciaVenda": row.get("quem_pendencia_venda"),
        }
        for row in rows
    ]
    return jsonify(properties)


@app.route("/api/vendas", methods=["POST"])
def api_criar_venda():
    data = request.get_json(force=True)
    if not data or not data.get("matricula"):
        return jsonify({"error": "matricula obrigatória"}), 400

    imovel = database.get_imovel_by_mat(data["matricula"])
    if not imovel:
        return jsonify({"error": "Imóvel não encontrado para esta matrícula"}), 404

    status_atual = (imovel.get("status") or "").strip().lower()
    if status_atual == "vendido":
        return jsonify({"error": "Este imóvel já está com status Vendido"}), 409

    update_data = {
        "status":               "Vendido",
        "comprador":            data.get("comprador"),
        "proposta":             data.get("recebido"),
        "obs":                  data.get("obs"),
        "data_venda":           data.get("data_venda"),
        "valor_venda_total":    data.get("valor_venda_total"),
        "fluxo_venda":          data.get("fluxo_venda"),
        "pendencia_venda":      data.get("pendencia_venda"),
        "quem_pendencia_venda": data.get("quem_pendencia_venda"),
    }
    update_data = {k: v for k, v in update_data.items() if v is not None}
    database.update_imovel(imovel["id"], update_data)
    return jsonify({"ok": True}), 200


@app.route("/api/propostas", methods=["GET"])
def api_get_propostas():
    rows = database.get_all_propostas()
    imoveis = database.get_all_imoveis()
    imovel_by_mat = {str(r.get("mat_tipo", "")).strip(): r for r in imoveis}

    result = []
    for p in rows:
        mat = str(p.get("matricula", "")).strip()
        imovel = imovel_by_mat.get(mat, {})
        result.append({
            "id":             p["id"],
            "matricula":      p["matricula"],
            "valor_venda":    p["valor_venda"],
            "fluxo":          p["fluxo"],
            "quem_fez":       p["quem_fez"],
            "pendencia":      p["pendencia"],
            "quem_pendencia": p["quem_pendencia"],
            "obs":            p["obs"],
            "tipologia":      imovel.get("tipologia"),
            "cidade":         imovel.get("cidade"),
            "estado":         imovel.get("estado"),
            "tipo":           imovel.get("tipo_imovel"),
        })
    return jsonify(result)


@app.route("/api/propostas", methods=["POST"])
def api_create_proposta():
    data = request.get_json(force=True)
    if not data or not data.get("matricula"):
        return jsonify({"error": "matricula obrigatória"}), 400
    new_id = database.insert_proposta(data)
    return jsonify({"id": new_id}), 201


@app.route("/api/propostas/<int:proposta_id>", methods=["PUT"])
def api_update_proposta(proposta_id):
    data = request.get_json(force=True)
    if not data:
        return jsonify({"error": "body vazio"}), 400
    updated = database.update_proposta(proposta_id, data)
    if not updated:
        return jsonify({"error": "proposta não encontrada"}), 404
    return jsonify({"ok": True})


@app.route("/api/dashboard")
def dashboard():
    return jsonify(dashboard_payload())


if __name__ == "__main__":
    app.run(debug=True)
