from datetime import datetime
import json
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from backend.database.incident_repository import get_incident as db_get_incident
from backend.database.incident_repository import update_rca as db_update_rca
from backend.ml.rca_generator import generate_rca_report
from backend.ml.similar_incidents import get_similar_incidents
from backend.ml.root_cause_agent import analyze_root_cause


def generate_rca(
    incident_id: str,
    actual_root_cause: str,
    resolution_action: str,
    preventive_measure: str,
    additional_notes: str = ""
) -> dict:
    """
    Orchestrate generating an RCA report by collecting all pre-computed
    intelligence (similar incidents, SLA breach, root cause prediction, L3 risk)
    and questionnaire answers, invoking the LLM, and persisting the result in DB.
    """
    # 1. Fetch incident from DB
    inc = db_get_incident(incident_id)
    if not inc:
        raise ValueError(f"Incident {incident_id} not found.")

    # 2. Check if already generated
    if inc.rca_generated and inc.rca_content:
        try:
            return json.loads(inc.rca_content)
        except Exception:
            pass

    # 3. Retrieve similar incidents
    similar_inc_list = []
    similar_inc_text = "None"
    try:
        similar_inc_list = get_similar_incidents(description=inc.description, top_k=5)
        if similar_inc_list:
            similar_inc_text = ", ".join([str(item.get("incident_id")) for item in similar_inc_list if "incident_id" in item])
    except Exception as e:
        print(f"Error fetching similar incidents in generate_rca: {e}")

    # 4. Retrieve Root Cause Agent prediction
    root_cause_prediction = "Unknown"
    root_cause_confidence = 50
    try:
        temp_incident_dict = {
            "incident_id": inc.incident_id,
            "description": inc.description,
            "application": inc.application,
            "category": inc.category,
            "impact_scope": inc.impact_scope,
            "affected_users": inc.affected_users
        }
        rc_analysis = analyze_root_cause(temp_incident_dict, similar_inc_list)
        root_cause_prediction = rc_analysis.get("root_cause", "Unknown")
        root_cause_confidence = rc_analysis.get("confidence", 50)
    except Exception as e:
        print(f"Error predicting root cause in generate_rca: {e}")

    # 5. Get database SLA & L3 values
    sla_breached = bool(inc.sla_breached)
    l3_escalation_risk = inc.l3_escalation_risk if inc.l3_escalation_risk is not None else "Unknown"
    l3_escalation_recommended = bool(inc.l3_escalation_recommended)

    # 6. Gather all data
    incident_data = {
        "incident_id": inc.incident_id,
        "description": inc.description,
        "application": inc.application,
        "category": inc.category,
        "priority": inc.priority,
        "status": inc.status,
        "assigned_team": inc.assigned_team or inc.ai_predicted_team or "N/A",
        "created_at": inc.created_at.strftime("%Y-%m-%d %H:%M:%S") if inc.created_at else "N/A",
        "resolved_at": inc.resolved_at.strftime("%Y-%m-%d %H:%M:%S") if inc.resolved_at else "N/A",
        "resolution_time": inc.actual_resolution_time if inc.actual_resolution_time is not None else "N/A",
        "affected_users": inc.affected_users,
        "impact_scope": inc.impact_scope,
        "sla_breached": sla_breached,
        "l3_escalation_risk": l3_escalation_risk,
        "l3_escalation_recommended": l3_escalation_recommended,
        "root_cause_prediction": root_cause_prediction,
        "root_cause_confidence": root_cause_confidence,
        "similar_incidents": similar_inc_text,
        "actual_root_cause": actual_root_cause,
        "resolution_action": resolution_action,
        "preventive_measure": preventive_measure,
        "additional_notes": additional_notes
    }

    # 7. Generate report via LLM
    rca_json = generate_rca_report(incident_data)
    rca_str = json.dumps(rca_json)

    # 8. Build and upload the PDF to Azure Blob Storage
    from backend.cloud.azure_blob import upload_file
    from datetime import date

    rca_generated_at_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pdf_incident_dict = {
        "incident_id": inc.incident_id,
        "description": inc.description,
        "application": inc.application,
        "category": inc.category,
        "priority": inc.priority,
        "status": inc.status,
        "rca_generated_at": rca_generated_at_str,
        "rca_content": rca_str
    }

    blob_url = None
    try:
        pdf_bytes = build_rca_pdf(pdf_incident_dict)
        filename = f"{inc.incident_id}-RCA-{date.today()}.pdf"
        blob_url = upload_file(pdf_bytes, filename, container_name="rca-files")
    except Exception as e:
        print(f"Error building or uploading RCA PDF to Azure: {e}")

    # 9. Persist to DB
    db_update_rca(
        incident_id=incident_id,
        rca_content=rca_str,
        rca_generated_at=datetime.now(),
        rca_pdf_url=blob_url
    )

    return rca_json


def get_rca_pdf_filename(incident: dict) -> str:
    """Return the filename following pattern <INCIDENT_ID>-RCA-<YYYY-MM-DD>.pdf"""
    incident_id = incident.get("incident_id", "INCIDENT").replace(" ", "-")
    rca_date_str = incident.get("rca_generated_at", "")
    if rca_date_str:
        try:
            rca_date = datetime.strptime(rca_date_str, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
        except Exception:
            rca_date = datetime.now().strftime("%Y-%m-%d")
    else:
        rca_date = datetime.now().strftime("%Y-%m-%d")
    return f"{incident_id}-RCA-{rca_date}.pdf"


def build_rca_pdf(incident: dict) -> bytes:
    """
    Build a professional styled ReportLab PDF containing metadata and the generated RCA details.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=64
    )

    styles = getSampleStyleSheet()

    primary_color = colors.HexColor('#0F172A')
    secondary_color = colors.HexColor('#1E3A8A')
    text_color = colors.HexColor('#334155')
    border_color = colors.HexColor('#E2E8F0')
    bg_light = colors.HexColor('#F8FAFC')

    title_style = ParagraphStyle(
        'RCATitle',
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=primary_color,
        spaceAfter=6
    )

    header_meta_style = ParagraphStyle(
        'RCAHeaderMeta',
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#64748B'),
        spaceAfter=4
    )

    section_heading = ParagraphStyle(
        'RCASectionHeading',
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=secondary_color,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'RCABody',
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=text_color,
        spaceAfter=10
    )

    meta_label = ParagraphStyle(
        'RCAMetaLabel',
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.HexColor('#475569')
    )

    meta_val = ParagraphStyle(
        'RCAMetaValue',
        fontName='Helvetica',
        fontSize=9,
        leading=11,
        textColor=primary_color
    )

    rca_generated_at = incident.get("rca_generated_at", "")
    if rca_generated_at:
        try:
            dt = datetime.strptime(rca_generated_at, "%Y-%m-%d %H:%M:%S")
            formatted_utc_time = dt.strftime("%Y-%m-%d %H:%M UTC")
            formatted_date = dt.strftime("%Y-%m-%d")
        except Exception:
            formatted_utc_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
            formatted_date = datetime.now().strftime("%Y-%m-%d")
    else:
        formatted_utc_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        formatted_date = datetime.now().strftime("%Y-%m-%d")

    story = []

    story.append(Paragraph("Root Cause Analysis Report", title_style))
    story.append(Paragraph(f"Incident ID: {incident.get('incident_id')}", header_meta_style))
    story.append(Paragraph(f"Generated On: {formatted_date}", header_meta_style))
    story.append(Spacer(1, 10))

    divider_table = Table([[""]], colWidths=[504])
    divider_table.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, -1), 1, border_color),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(divider_table)
    story.append(Spacer(1, 12))

    meta_data = [
        [
            Paragraph("Incident ID:", meta_label),
            Paragraph(str(incident.get("incident_id")), meta_val),
            Paragraph("Application:", meta_label),
            Paragraph(str(incident.get("application")), meta_val)
        ],
        [
            Paragraph("Priority:", meta_label),
            Paragraph(str(incident.get("priority")), meta_val),
            Paragraph("Status:", meta_label),
            Paragraph(str(incident.get("status")), meta_val)
        ],
        [
            Paragraph("Generated At:", meta_label),
            Paragraph(str(rca_generated_at), meta_val),
            Paragraph("", meta_label),
            Paragraph("", meta_val)
        ]
    ]

    col_widths = [95, 157, 95, 157]
    meta_table = Table(meta_data, colWidths=col_widths)
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), bg_light),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('BOX', (0, 0), (-1, -1), 0.5, border_color),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, border_color),
    ]))

    story.append(meta_table)
    story.append(Spacer(1, 15))

    rca_content = incident.get("rca_content")
    rca_data = {}
    if rca_content:
        try:
            if isinstance(rca_content, str):
                rca_data = json.loads(rca_content)
            elif isinstance(rca_content, dict):
                rca_data = rca_content
        except Exception:
            pass

    summary_text = rca_data.get("summary", "No summary generated.")
    root_cause_text = rca_data.get("root_cause", "No root cause analysis generated.")
    resolution_text = rca_data.get("resolution", "No resolution action generated.")
    preventive_text = rca_data.get("preventive_action", "No preventive actions generated.")

    sections = [
        ("Summary", summary_text),
        ("Root Cause", root_cause_text),
        ("Resolution", resolution_text),
        ("Preventive Action", preventive_text)
    ]

    for title, content in sections:
        story.append(Paragraph(title, section_heading))
        story.append(Paragraph(content, body_style))
        story.append(Spacer(1, 4))

    def add_footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#64748B'))

        canvas.setStrokeColor(border_color)
        canvas.setLineWidth(0.5)
        canvas.line(54, 45, 612 - 54, 45)

        canvas.drawString(54, 32, "Generated by Incident Intelligence Platform")
        canvas.drawRightString(612 - 54, 32, f"RCA Generated: {formatted_utc_time}")
        canvas.restoreState()

    doc.build(story, onFirstPage=add_footer, onLaterPages=add_footer)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
