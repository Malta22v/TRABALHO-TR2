import csv
import os
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "output" / "pdf"
PDF_FILE = OUTPUT_DIR / "relatorio_politicas_abr.pdf"
TEX_FILE = OUTPUT_DIR / "relatorio_politicas_abr.tex"

RUNS = {
    "RATE": {
        "label": "Politica 1 - RATE",
        "summary": ROOT / "graphs" / "1_RATE_20260624_150800" / "summary.csv",
        "dashboard": ROOT / "graphs" / "1_RATE_20260624_150800" / "dashboard.png",
        "csv": ROOT / "logs" / "metrics_1_RATE_20260624_150800.csv",
        "graphs": ROOT / "graphs" / "1_RATE_20260624_150800",
    },
    "BUFFER": {
        "label": "Politica 2 - BUFFER",
        "summary": ROOT / "graphs" / "2_BUFFER_20260624_150847" / "summary.csv",
        "dashboard": ROOT / "graphs" / "2_BUFFER_20260624_150847" / "dashboard.png",
        "csv": ROOT / "logs" / "metrics_2_BUFFER_20260624_150847.csv",
        "graphs": ROOT / "graphs" / "2_BUFFER_20260624_150847",
    },
    "HYBRID": {
        "label": "Politica 3 - HYBRID",
        "summary": ROOT / "graphs" / "3_HYBRID_20260624_150940" / "summary.csv",
        "dashboard": ROOT / "graphs" / "3_HYBRID_20260624_150940" / "dashboard.png",
        "csv": ROOT / "logs" / "metrics_3_HYBRID_20260624_150940.csv",
        "graphs": ROOT / "graphs" / "3_HYBRID_20260624_150940",
    },
}

COMPARISON_IMAGE = ROOT / "graphs" / "comparison_20260624_151027" / "comparison.png"
COMPARISON_CSV = ROOT / "graphs" / "comparison_20260624_151027" / "comparison_summary.csv"


def read_one_row(path):
    with path.open(newline="", encoding="utf-8") as file:
        return next(csv.DictReader(file))


def fmt_number(value, suffix="", decimals=2):
    number = float(value)
    formatted = f"{number:.{decimals}f}".replace(".", ",")
    return f"{formatted} {suffix}".strip()


def flow_table(rows, styles):
    data = [[Paragraph(step, styles["Flow"]) for step in rows]]
    table = Table(data, colWidths=[16.2 * cm])
    table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#6B7280")),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return table


def image(path, width_cm):
    img = Image(str(path))
    ratio = img.imageHeight / img.imageWidth
    img.drawWidth = width_cm * cm
    img.drawHeight = img.drawWidth * ratio
    return img


def build_pdf():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    summaries = {name: read_one_row(info["summary"]) for name, info in RUNS.items()}

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="TitleCenter",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=20,
        leading=25,
        spaceAfter=18,
    ))
    styles.add(ParagraphStyle(
        name="SubtitleCenter",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#334155"),
        spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        name="BodyJustify",
        parent=styles["BodyText"],
        alignment=TA_JUSTIFY,
        fontSize=10.5,
        leading=15,
        spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        name="Flow",
        parent=styles["BodyText"],
        fontSize=9,
        leading=12,
    ))

    doc = SimpleDocTemplate(
        str(PDF_FILE),
        pagesize=A4,
        rightMargin=1.8 * cm,
        leftMargin=1.8 * cm,
        topMargin=1.7 * cm,
        bottomMargin=1.7 * cm,
        title="Relatorio de Comparacao das Politicas ABR",
    )

    story = []
    story.append(Spacer(1, 3.2 * cm))
    story.append(Paragraph("Relatorio de Comparacao das Politicas ABR", styles["TitleCenter"]))
    story.append(Paragraph("Adaptive Bitrate Streaming - Projeto Final TR2", styles["SubtitleCenter"]))
    story.append(Paragraph("Execucao realizada em 24/06/2026 com 30 segmentos por politica.", styles["SubtitleCenter"]))
    story.append(Spacer(1, 1.0 * cm))
    story.append(Paragraph(
        "O objetivo deste relatorio e comparar tres politicas de selecao adaptativa de bitrate, "
        "avaliando throughput, estabilidade do buffer, eventos de rebuffer, failover e qualidade final.",
        styles["BodyJustify"],
    ))
    story.append(PageBreak())

    story.append(Paragraph("1. Artefatos gerados", styles["Heading1"]))
    artifact_data = [["Politica", "CSV", "Graficos"]]
    for name, info in RUNS.items():
        artifact_data.append([
            RUNS[name]["label"],
            str(info["csv"].relative_to(ROOT)),
            str(info["graphs"].relative_to(ROOT)),
        ])
    artifact_data.append(["Comparacao", str(COMPARISON_CSV.relative_to(ROOT)), str(COMPARISON_IMAGE.relative_to(ROOT))])
    artifact_table = Table(artifact_data, colWidths=[4.0 * cm, 6.2 * cm, 6.0 * cm], repeatRows=1)
    artifact_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F2937")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(artifact_table)
    story.append(Spacer(1, 0.5 * cm))

    story.append(Paragraph("2. Descricao das politicas e fluxogramas", styles["Heading1"]))

    story.append(Paragraph("2.1 Politica 1 - RATE", styles["Heading2"]))
    story.append(Paragraph(
        "A politica RATE escolhe a proxima qualidade a partir da mediana recente de throughput. "
        "Ela aplica um fator de seguranca conforme o estado do buffer: quando o buffer esta critico, "
        "forca a menor representacao; com buffer baixo, reduz a banda considerada; com buffer bom, "
        "usa a mediana de forma menos conservadora.",
        styles["BodyJustify"],
    ))
    story.append(flow_table([
        "1. Baixa segmento atual.",
        "2. Mede throughput.",
        "3. Atualiza historico e calcula a mediana da janela.",
        "4. Le a confianca do buffer.",
        "5. Se buffer critico: escolhe menor qualidade.",
        "6. Caso contrario: aplica fator de seguranca.",
        "7. Escolhe o maior bitrate menor ou igual a banda segura.",
    ], styles))

    story.append(Paragraph("2.2 Politica 2 - BUFFER", styles["Heading2"]))
    story.append(Paragraph(
        "A politica BUFFER ignora a estimativa de banda e usa apenas o nivel do buffer para selecionar "
        "a qualidade. Quanto maior o buffer acumulado, maior a representacao escolhida.",
        styles["BodyJustify"],
    ))
    story.append(flow_table([
        "1. Baixa segmento atual.",
        "2. Atualiza nivel do buffer.",
        "3. Buffer < 4s: escolhe 240p.",
        "4. Buffer entre 4s e 8s: escolhe 360p.",
        "5. Buffer entre 8s e 12s: escolhe 480p.",
        "6. Buffer entre 12s e 16s: escolhe 720p.",
        "7. Buffer >= 16s: escolhe 1080p.",
    ], styles))

    story.append(Paragraph("2.3 Politica 3 - HYBRID", styles["Heading2"]))
    story.append(Paragraph(
        "A politica HYBRID combina mediana de throughput, nivel do buffer e jitter EWMA. Com buffer alto, "
        "filtra quedas isoladas de throughput e permite ser mais agressiva. Com buffer baixo ou rede instavel, "
        "penaliza a banda estimada de acordo com o jitter.",
        styles["BodyJustify"],
    ))
    story.append(flow_table([
        "1. Baixa segmento atual.",
        "2. Mede throughput e jitter.",
        "3. Atualiza historico de throughput.",
        "4. Le nivel do buffer.",
        "5. Buffer > 14s: filtra outliers baixos e aumenta banda estimada.",
        "6. Buffer entre 12s e 14s: aplica ganho leve de transicao.",
        "7. Buffer entre 8s e 12s: penaliza por jitter.",
        "8. Buffer entre 4s e 8s: penaliza mais por jitter.",
        "9. Buffer < 4s: reduz agressivamente a banda estimada.",
    ], styles))

    story.append(PageBreak())
    story.append(Paragraph("3. Comparacao dos resultados", styles["Heading1"]))
    comparison_data = [[
        "Politica", "Throughput medio", "Buffer medio", "Rebuffer",
        "Failover", "Trocas", "Bitrate medio", "Qual. final"
    ]]
    for name in ["RATE", "BUFFER", "HYBRID"]:
        row = summaries[name]
        comparison_data.append([
            RUNS[name]["label"].replace("Politica ", ""),
            fmt_number(row["avg_throughput_kbps"], "kbps"),
            fmt_number(row["avg_buffer_s"], "s"),
            row["total_rebuffer_events"],
            row["failover_events"],
            row["quality_switches"],
            fmt_number(row["avg_bitrate_kbps"], "kbps"),
            row["final_quality"],
        ])
    comparison_table = Table(
        comparison_data,
        colWidths=[2.3 * cm, 2.3 * cm, 1.9 * cm, 1.5 * cm, 1.5 * cm, 1.4 * cm, 2.1 * cm, 1.8 * cm],
        repeatRows=1,
    )
    comparison_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F2937")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.6),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
    ]))
    story.append(comparison_table)
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph(
        "A politica RATE e um bom baseline porque reage ao throughput, mas apresentou oscilacao: "
        "foram 6 trocas de qualidade e termino em 480p, mesmo com buffer estabilizado. A politica BUFFER "
        "teve o pior comportamento geral nesta execucao, com menor throughput medio, menor buffer medio, "
        "1 rebuffer e 1 failover. A politica HYBRID apresentou o melhor resultado: maior throughput medio, "
        "maior bitrate medio, menos trocas de qualidade, zero rebuffer e qualidade final 1080p.",
        styles["BodyJustify"],
    ))
    story.append(Paragraph("4. Decisoes de mudanca embasadas por dados", styles["Heading1"]))
    story.append(Paragraph(
        "A evolucao RATE -> BUFFER -> HYBRID foi motivada por problemas mensuraveis nas execucoes. "
        "A tabela abaixo liga cada mudanca de politica aos dados observados nos CSVs gerados.",
        styles["BodyJustify"],
    ))
    evidence_data = [["Decisao", "Evidencia numerica", "Interpretacao"]]
    evidence_data.extend([
        [
            "RATE precisa de criterio alem do throughput",
            "Segmento 15: RATE baixou 720p, mas o throughput instantaneo foi 300,43 kbps, abaixo do bitrate de 900 kbps; jitter EWMA = 440,76 kbps.",
            "O historico de throughput pode atrasar a reacao a quedas bruscas.",
        ],
        [
            "RATE oscila qualidade",
            "6 trocas: 240p -> 360p -> 480p -> 720p -> 480p -> 360p -> 480p; terminou em 480p mesmo com buffer bom em 18/30 segmentos.",
            "Evita rebuffer, mas nao estabiliza bem a qualidade visual.",
        ],
        [
            "BUFFER sozinha nao basta",
            "Segmento 4: failover e rebuffer com throughput de 81,04 kbps, buffer de 1,11 s e failover de 1,148 s.",
            "Ignorar throughput e jitter faz a degradacao ser percebida tarde demais.",
        ],
        [
            "BUFFER escolhe acima da rede",
            "Segmento 16: BUFFER em 720p (900 kbps), mas throughput de 336,40 kbps; no segmento 17 caiu para 480p.",
            "Buffer isolado nao representa a capacidade real de download.",
        ],
        [
            "HYBRID justifica a politica final",
            "0 rebuffer, 0 failover, 3 trocas, throughput medio 1200,33 kbps, bitrate medio 1066,67 kbps e jitter EWMA medio 39,48 kbps.",
            "Throughput, buffer e jitter juntos reduzem travamento e oscilacao.",
        ],
    ])
    evidence_table = Table(evidence_data, colWidths=[4.0 * cm, 7.0 * cm, 5.2 * cm], repeatRows=1)
    evidence_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F2937")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.2),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(evidence_table)
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        "Assim, a RATE serviu como linha de base orientada por rede, mas apresentou atraso de resposta e oscilacao. "
        "A BUFFER tentou proteger a reproducao pelo armazenamento local, mas falhou quando a rede degradou. "
        "A HYBRID foi adotada porque os dados mostraram que a decisao precisava considerar simultaneamente "
        "capacidade de rede, folga de buffer e instabilidade.",
        styles["BodyJustify"],
    ))

    story.append(Spacer(1, 0.3 * cm))
    story.append(image(COMPARISON_IMAGE, 16.2))

    story.append(PageBreak())
    story.append(Paragraph("5. Analise por politica", styles["Heading1"]))
    analysis = {
        "RATE": (
            "A RATE manteve 0 eventos de rebuffer e 0 failovers, mas terminou conservadora em 480p. "
            "O uso de throughput com janela curta ajuda a reagir a variacoes, porem tambem gera oscilacao "
            "quando a rede alterna entre picos e quedas."
        ),
        "BUFFER": (
            "A BUFFER terminou em 720p, mas sofreu 1 rebuffer e 1 failover. O problema e que a politica "
            "nao observa a banda real nem o jitter; assim, uma decisao baseada apenas no buffer pode manter "
            "ou subir qualidade mesmo quando a rede nao sustenta a representacao."
        ),
        "HYBRID": (
            "A HYBRID estabilizou em 1080p a partir do segmento 10 e se manteve nessa qualidade ate o final. "
            "A combinacao de buffer, throughput e jitter reduziu trocas desnecessarias e preservou a reproducao."
        ),
    }
    for name in ["RATE", "BUFFER", "HYBRID"]:
        story.append(KeepTogether([
            Paragraph(RUNS[name]["label"], styles["Heading2"]),
            Paragraph(analysis[name], styles["BodyJustify"]),
            image(RUNS[name]["dashboard"], 16.2),
        ]))

    story.append(PageBreak())
    story.append(Paragraph("6. Failover", styles["Heading1"]))
    story.append(Paragraph(
        "O failover fica encapsulado em core/server_manager.py. O cliente inicia no servidor de maior "
        "prioridade. Quando download_segment falha, o ServerManager.failover() percorre os demais servidores, "
        "executa health check em /health e troca para o primeiro servidor saudavel. O CSV registra server_id, "
        "failover e failover_time_s. Na execucao comparativa, o failover real ocorreu na politica BUFFER, "
        "no segmento 4, indo para srv-B e levando 1,148 s.",
        styles["BodyJustify"],
    ))
    story.append(Paragraph("7. Mocks utilizados", styles["Heading1"]))
    story.append(Paragraph(
        "O arquivo mock_failover_policy.py contem testes sem depender dos servidores reais. O MockHealth "
        "simula quais servidores estao saudaveis e valida o failover bidirecional, a filtragem de throughput "
        "baixo isolado na HYBRID e o comportamento conservador da HYBRID com buffer baixo e jitter alto.",
        styles["BodyJustify"],
    ))

    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)


def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#64748B"))
    canvas.drawRightString(19.2 * cm, 1.0 * cm, f"Pagina {doc.page}")
    canvas.restoreState()


def build_tex():
    tex = r"""\documentclass[12pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[brazil]{babel}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{geometry}
\geometry{margin=2cm}
\title{Relatorio de Comparacao das Politicas ABR}
\author{Projeto Final TR2}
\date{24/06/2026}
\begin{document}
\maketitle

\section{Resumo}
Este relatorio compara tres politicas ABR: RATE, BUFFER e HYBRID. A execucao foi realizada com 30 segmentos por politica.

\section{Resultados}
\begin{tabular}{lrrrrrrl}
\toprule
Politica & Throughput & Buffer & Rebuffer & Failover & Trocas & Bitrate & Final\\
\midrule
RATE & 771,52 kbps & 12,58 s & 0 & 0 & 6 & 580,00 kbps & 480p\\
BUFFER & 564,89 kbps & 9,86 s & 1 & 1 & 7 & 590,00 kbps & 720p\\
HYBRID & 1200,33 kbps & 12,88 s & 0 & 0 & 3 & 1066,67 kbps & 1080p\\
\bottomrule
\end{tabular}

\section{Analise}
A politica RATE reage ao throughput, mas oscilou e terminou conservadora em 480p. A politica BUFFER decide apenas pelo nivel do buffer, o que causou rebuffer e failover nesta execucao. A politica HYBRID combinou throughput, buffer e jitter, sustentando 1080p com zero rebuffer.

\section{Decisoes embasadas por dados}
A mudanca de RATE para BUFFER e, depois, para HYBRID foi motivada por evidencias numericas. Na RATE, o segmento 15 baixou 720p com throughput instantaneo de apenas 300,43 kbps, abaixo do bitrate de 900 kbps, e jitter EWMA de 440,76 kbps. Isso mostra atraso de reacao a quedas bruscas. Na BUFFER, o segmento 4 registrou rebuffer e failover com throughput de 81,04 kbps, buffer de 1,11 s e failover de 1,148 s. No segmento 16, a BUFFER estava em 720p, mas a rede entregou 336,40 kbps, levando a queda para 480p no segmento seguinte. A HYBRID foi escolhida como politica final porque teve 0 rebuffer, 0 failover, apenas 3 trocas, throughput medio de 1200,33 kbps, bitrate medio de 1066,67 kbps e jitter EWMA medio de 39,48 kbps.

\section{Failover e mocks}
O failover e implementado pelo ServerManager, que troca para um servidor saudavel quando o download falha. O arquivo mock_failover_policy.py usa MockHealth para validar failover bidirecional e cenarios da politica HYBRID sem depender da rede real.

\end{document}
"""
    TEX_FILE.write_text(tex, encoding="utf-8")


if __name__ == "__main__":
    build_pdf()
    build_tex()
    print(PDF_FILE)
    print(TEX_FILE)


