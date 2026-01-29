"""
PDF Generator module for SOR Automation System
Handles PDF creation and formatting
"""
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from .config import config
import numpy as np
import pandas as pd


def validate_image_path(image_path, image_name):
    """Validate that an image file exists and can be read by ReportLab."""
    print(f"\n[DEBUG] Checking {image_name}...")
    print(f"[DEBUG] Path: {image_path}")
    
    if not image_path:
        print(f"[ERROR] {image_name}: No path provided")
        return None
    
    if not os.path.exists(image_path):
        print(f"[ERROR] {image_name}: File NOT FOUND at {image_path}")
        assets_dir = os.path.dirname(image_path)
        if os.path.exists(assets_dir):
            print(f"[DEBUG] Files in {assets_dir}:")
            for f in os.listdir(assets_dir):
                print(f"        - {f}")
        else:
            print(f"[ERROR] Assets directory does not exist: {assets_dir}")
        return None
    
    file_size = os.path.getsize(image_path)
    print(f"[OK] {image_name}: File exists ({file_size} bytes)")
    
    try:
        reader = ImageReader(image_path)
        width, height = reader.getSize()
        print(f"[OK] {image_name}: Image readable ({width}x{height} pixels)")
        return image_path
    except Exception as e:
        print(f"[ERROR] {image_name}: Cannot read image - {e}")
        return None


def draw_image_safe(canvas_obj, image_path, x, y, width, height, preserve_aspect=True, image_name="image"):
    """Draw an image on canvas safely."""
    print(f"[DEBUG] draw_image_safe called for {image_name} at ({x}, {y}) size ({width}x{height})")
    if not image_path:
        print(f"[DRAW] {image_name}: Skipped - no path")
        return False
    
    if not os.path.exists(image_path):
        print(f"[DRAW] {image_name}: Skipped - file not found: {image_path}")
        return False
    
    try:
        print(f"[DRAW] {image_name}: Drawing at ({x}, {y}) size ({width}x{height})...")
        img_reader = ImageReader(image_path)
        canvas_obj.drawImage(img_reader, x, y, width=width, height=height, preserveAspectRatio=preserve_aspect, anchor='sw')
        print(f"[DRAW] {image_name}: SUCCESS")
        return True
    except Exception as e:
        print(f"[DRAW] {image_name}: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False


def add_stamp(canvas_obj, doc):
    """Draw stamp and date in bottom-right."""
    print("[STAMP] add_stamp called")
    if not config.STAMP_PATH_VALID:
        print("[STAMP] No STAMP_PATH_VALID")
        return
    page_width, page_height = A4
    stamp_size = 25 * mm
    x = page_width - stamp_size - 21 * mm
    y = 25 * mm
    
    if draw_image_safe(canvas_obj, config.STAMP_PATH_VALID, x, y, stamp_size, stamp_size, image_name="STAMP"):
        issue_date = datetime.now().strftime("%Y-%m-%d")
        try:
            canvas_obj.setFont("Helvetica-Bold", 8)
            canvas_obj.setFillColor(colors.black)
            text_width = canvas_obj.stringWidth(issue_date, "Helvetica-Bold", 8)
            canvas_obj.drawString(x + (stamp_size - text_width) / 2, y + stamp_size / 9 - 12, issue_date)
        except Exception as e:
            print(f"[ERROR] Failed to draw stamp date: {e}")


def add_watermark(canvas_obj, doc):
    """Light watermark."""
    print("[WATERMARK] add_watermark called")
    if not config.LOGO_PATH_VALID:
        print("[WATERMARK] No LOGO_PATH_VALID")
        return
    page_width, page_height = A4
    canvas_obj.saveState()
    try:
        canvas_obj.setFillAlpha(0.06)
    except Exception:
        pass
    canvas_obj.translate(page_width / 2, page_height / 2)
    canvas_obj.rotate(45)
    draw_image_safe(canvas_obj, config.LOGO_PATH_VALID, -page_width, -page_height / 2, page_width * 2, page_height, image_name="WATERMARK")
    canvas_obj.restoreState()


def add_cover_page(canvas_obj, doc, learner):
    """Draw cover page."""
    print("\n[COVER PAGE] add_cover_page called")
    print(f"[COVER PAGE] COVER_PATH_VALID: {config.COVER_PATH_VALID}")
    print(f"[COVER PAGE] LOGO_PATH_VALID: {config.LOGO_PATH_VALID}")
    if config.COVER_PATH_VALID:
        draw_image_safe(canvas_obj, config.COVER_PATH_VALID, 0, 0, A4[0], A4[1], preserve_aspect=False, image_name="COVER_BG")
    
    if config.LOGO_PATH_VALID:
        logo_width = 120
        logo_height = 60
        x_position = 38
        y_position = A4[1] - 70  # Moved up from -100 to -70 (30 points higher)
        draw_image_safe(canvas_obj, config.LOGO_PATH_VALID, x_position, y_position, logo_width, logo_height, image_name="COVER_LOGO")


def add_header_footer(canvas_obj, doc):
    """Add header and footer."""
    print("[HEADER] add_header_footer called")
    if config.LOGO_PATH_VALID:
        page_width, page_height = A4
        logo_width = 80
        logo_height = 30
        x = page_width - logo_width - 20
        y = page_height - logo_height - 20
        draw_image_safe(canvas_obj, config.LOGO_PATH_VALID, x, y, logo_width, logo_height, image_name="HEADER_LOGO")

    footer_text = "Final Statement of Results\nSoftware Engineering SAQA Qualification Code 119458"
    footer_lines = footer_text.split('\n')
    canvas_obj.saveState()
    try:
        canvas_obj.setFont("Helvetica", 9)
        x = doc.leftMargin
        y = 30
        for i, line in enumerate(footer_lines):
            canvas_obj.drawString(x, y + (10 * i), line)
        page_num_text = f"Page {doc.page}"
        canvas_obj.drawRightString(A4[0] - doc.rightMargin, y, page_num_text)
    except Exception as e:
        print(f"[ERROR] Failed to draw footer: {e}")
    canvas_obj.restoreState()


def on_first_page(canvas_obj, doc):
    print("[PDF] on_first_page called")
    learner = getattr(doc, 'learner', {})
    add_cover_page(canvas_obj, doc, learner)


def on_later_pages(canvas_obj, doc):
    print("[PDF] on_later_pages called")
    add_header_footer(canvas_obj, doc)
    add_watermark(canvas_obj, doc)
    add_stamp(canvas_obj, doc)


def make_kv_table(kv_list, col_widths=None, styles=None):
    """Make key-value table."""
    if styles is None:
        styles = getSampleStyleSheet()
    normal = styles["Normal"]
    data = [[Paragraph(f"<b>{k}</b>", normal), Paragraph(str(v or ""), normal)] for k, v in kv_list]
    t = Table(data, colWidths=col_widths or [80 * mm, None], hAlign="LEFT")
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    return t


def make_kv_table_bold_header(kv_list, col_widths=None, styles=None):
    """Make key-value table with bold headers."""
    if styles is None:
        styles = getSampleStyleSheet()
    normal = styles["Normal"]
    data = [["Field", "Value"]] + [[k, v] for k, v in kv_list]
    t = Table(data, colWidths=col_widths or [100 * mm, None], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#d9d9d9")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("ALIGN", (1, 0), (1, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def calculate_overall_score(learner_data):
    """Calculate overall score from learner data without processing full dataframe"""
    results = learner_data.get('results', [])
    if not results:
        return 0.0

    raw_weights = config.QUIZ_WEIGHTS
    total_raw_weight = sum(raw_weights.values())

    total_weighted_score = 0.0
    for result in results:
        quiz_id = result.get('quiz_id')
        learner_score = float(result.get('learner_score') or 0)
        total_marks = float(result.get('total_marks') or 1)  # Avoid division by zero

        # Calculate achievement percentage
        achievement_pct = (learner_score / total_marks * 100) if total_marks > 0 else 0

        # Get weight for this quiz
        weight = raw_weights.get(quiz_id, 0)

        # Calculate weighted score
        weighted_score = achievement_pct * weight
        total_weighted_score += weighted_score

    # Calculate overall score
    overall_score = (total_weighted_score / total_raw_weight) if total_raw_weight > 0 else 0.0
    return round(overall_score, 2)


def process_results_data(results_df, quiz_section_map, section_1_name):
    """Process quiz results."""
    if results_df.empty:
        results_df = pd.DataFrame(columns=["learner_name", "quiz_id", "topic_name", "learner_score", "total_marks", "Achievement: Percentage", "Credits", "Weight (%)", "Final EISA Achievement Score", "Section", "Module"])
        overall_score = 0.00
        overall_status = "Not Yet Competent"
        return results_df, overall_score, overall_status

    for col in ["learner_score", "total_marks"]:
        results_df[col] = pd.to_numeric(results_df[col].fillna(0), errors="coerce").fillna(0)

    results_df["Section"] = results_df["quiz_id"].map(lambda x: quiz_section_map.get(x, {}).get('section_name', 'Unknown Module'))
    results_df["Module"] = results_df["Section"]

    raw_weights = config.QUIZ_WEIGHTS
    total_raw_weight = sum(raw_weights.values())

    results_df["module_raw_weight"] = results_df["quiz_id"].map(raw_weights).fillna(0)
    credits_map = config.QUIZ_CREDITS
    results_df["Credits"] = results_df["quiz_id"].map(credits_map).fillna(0).astype(int)

    den = results_df["total_marks"].replace({0: np.nan})
    results_df["Achievement: Percentage"] = ((results_df["learner_score"] / den) * 100).fillna(0).round(2)

    results_df["Final EISA Achievement Score"] = (results_df["Achievement: Percentage"] * results_df["module_raw_weight"]).round(2)

    sum_of_raw_weighted_scores = results_df["Final EISA Achievement Score"].sum()
    overall_score = (sum_of_raw_weighted_scores / total_raw_weight).round(2)

    results_df["Weight (%)"] = (results_df["module_raw_weight"] * 100).round(2)

    overall_status = "Competent" if overall_score >= 70 else "Not Yet Competent"

    print("\n--- Per-quiz results ---")
    print(results_df[["Section", "Module", "topic_name", "learner_score", "total_marks", "Achievement: Percentage", "Weight (%)", "Final EISA Achievement Score"]].head(10).to_string(index=False))
    print(f"\nOverall Score: {overall_score:.2f}% - {overall_status}\n")

    return results_df, overall_score, overall_status


def generate_sor_pdf(learner_name, learner_data, pdf_output_path):
    """Generate the SOR PDF."""
    print(f"\nGenerating SOR PDF for {learner_name}...")

    learner = learner_data['learner']
    profile = learner_data['profile']
    provider_info = learner_data['provider_info']
    section_1_name = learner_data['section_1_name']
    quiz_section_map = learner_data['quiz_section_map']
    results_df = pd.DataFrame(learner_data['results'])
    emp_fields = learner_data['emp_fields']

    results_df, overall_score, overall_status = process_results_data(results_df, quiz_section_map, section_1_name)

    doc = SimpleDocTemplate(pdf_output_path, pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm, topMargin=18 * mm, bottomMargin=18 * mm)
    doc.learner = {"fullname": f"{learner['firstname']} {learner['lastname']}", "id": learner.get("id")}
    elements = []

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="CenterTitle", parent=styles["Heading1"], alignment=1, fontSize=18, spaceAfter=6))
    styles.add(ParagraphStyle(name="SectionTitle", parent=styles["Heading2"], fontSize=12, spaceAfter=6))
    styles.add(ParagraphStyle(name="Small", parent=styles["Normal"], fontSize=9))
    normal = styles["Normal"]

    styles.add(ParagraphStyle(name="CoverTitleGrey", parent=styles["Heading1"], alignment=1, fontSize=16, spaceAfter=12, textColor=colors.HexColor("#555555")))

    # Cover page
    elements.append(Spacer(1, 180))
    elements.append(Paragraph("MINDWORX STATEMENT OF RESULTS", styles["CoverTitleGrey"]))
    elements.append(Spacer(1, 26))

    learner_cover_kv = [
        ("Full Name", f"{learner['firstname']} {learner['lastname']}"),
        ("Registration Number", profile.get("Registration Number", profile.get("registration_number", ""))),
    ]
    elements.append(make_kv_table(learner_cover_kv, col_widths=[65 * mm, None], styles=styles))
    elements.append(Spacer(1, 18))

    qualification_cover_kv = [
        ("Qualification", config.QUAL_TITLE),
        ("SAQA ID", config.SAQA_ID),
        ("NQF Level", config.NQF_LEVEL),
        ("Total Credits", config.TOTAL_CREDITS)
    ]
    elements.append(make_kv_table(qualification_cover_kv, col_widths=[45 * mm, None], styles=styles))
    elements.append(Spacer(1, 155))
    elements.append(PageBreak())

    # Learner Details
    elements.append(Paragraph("Learner Details", styles["SectionTitle"]))
    learner_kv = [
        ("Full Name", f"{learner['firstname']} {learner['lastname']}"),
        ("Email", learner.get("email", "")),
        ("SA ID / DOB", profile.get("Date of Birth", profile.get("ID Number", profile.get("idnumber", "")))),
        ("MindWorx Learner Number", profile.get("Learner Number", profile.get("learner_number", ""))),
        ("Learning Start Date", profile.get("Start Date", profile.get("Learning Start Date", ""))),
        ("Learning End Date", profile.get("Learning End Date", profile.get("enddate", profile.get("learning_end_date", ""))))
    ]
    elements.append(make_kv_table_bold_header(learner_kv, styles=styles))
    elements.append(Spacer(1, 12))

    # Employer Details
    elements.append(Paragraph("Employer Details", styles["SectionTitle"]))
    employer_kv = []
    if emp_fields:
        for f in emp_fields:
            fieldname = f["name"]
            val = profile.get(fieldname, "")
            employer_kv.append((fieldname, val))
    else:
        employer_kv.append(("Employer", "No employer profile fields found (categoryid=5)"))
    elements.append(make_kv_table_bold_header(employer_kv, styles=styles))
    elements.append(PageBreak())

    # Document Version
    elements.append(Paragraph("Document Version", styles["SectionTitle"]))
    doc_version_kv = [
        ("Document Version", "3.0"),
        ("Date Published", "2 Oct 2025"),
        ("Publisher", "MINDWORX ACADEMY"),
        ("Document Change History", "21/7/2025; 22/9/2025; 2/10/2025"),
        ("Document Author", "MvR"),
        ("Review History", "")
    ]
    elements.append(make_kv_table_bold_header(doc_version_kv, styles=styles))
    elements.append(PageBreak())

    # QUALIFICATION STRUCTURE
    elements.append(Paragraph("QUALIFICATION STRUCTURE", styles["SectionTitle"]))
    elements.append(Spacer(1, 6))

    # Knowledge Modules
    elements.append(Paragraph("<b>Knowledge Modules</b>", styles["Small"]))
    knowledge_data = [
        ["KM 01", "Software Engineering", "NQF Level 6", "20"],
        ["KM 02", "Programming", "NQF Level 6", "20"],
        ["KM 03", "Database design and Information Systems", "NQF Level 6", "15"],
        ["KM 04", "Fundamentals of Project Management", "NQF Level 5", "5"],
        ["KM 05", "Digital and Business Mathematics", "NQF Level 5", "15"]
    ]
    knowledge_table = Table([["Code", "Module Name", "NQF Level", "Credits"]] + knowledge_data, colWidths=[30 * mm, 100 * mm, 30 * mm, 20 * mm])
    knowledge_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (2, 1), (3, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold')
    ]))
    elements.append(knowledge_table)
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("Total number of credits for Knowledge Modules: 75", normal))
    elements.append(Spacer(1, 18))

    # Practical Skill Modules
    elements.append(Paragraph("<b>Practical Skill Modules</b>", styles["Small"]))
    practical_data = [
        ["PM 01", "Document system design", "NQF Level 6", "25"],
        ["PM 02", "Design and Manipulate Databases", "NQF Level 5", "5"],
        ["PM 03", "Program and deploy applications", "NQF Level 6", "25"],
        ["PM 04", "Test or debug source code", "NQF Level 5", "15"]
    ]
    practical_table = Table([["Code", "Module Name", "NQF Level", "Credits"]] + practical_data, colWidths=[30 * mm, 100 * mm, 30 * mm, 20 * mm])
    practical_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (2, 1), (3, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold')
    ]))
    elements.append(practical_table)
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("Total number of credits for Practical Skill Modules: 70", normal))
    elements.append(Spacer(1, 18))

    # Work Experience Modules
    elements.append(Paragraph("<b>Work Experience Modules</b>", styles["Small"]))
    work_data = [
        ["WM 01", "Software design", "NQF Level 6", "30"],
        ["WM 02", "Database design and manipulation", "NQF Level 5", "20"],
        ["WM 03", "Software development", "NQF Level 6", "30"],
        ["WM 04", "Software testing", "NQF Level 5", "15"]
    ]
    work_table = Table([["Code", "Module Name", "NQF Level", "Credits"]] + work_data, colWidths=[30 * mm, 100 * mm, 30 * mm, 20 * mm])
    work_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (2, 1), (3, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold')
    ]))
    elements.append(work_table)
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("Total number of credits for Work Experience Modules: 95", normal))
    elements.append(Spacer(1, 18))

    # Exit Level Outcomes
    elements.append(Paragraph("<b>Exit Level Outcome</b>", styles["Small"]))
    exit_outcomes = [
        "Design software to meet clients' needs",
        "Design and manipulate databases",
        "Develop software to add value to the organisation",
        "Test or debug source code"
    ]
    for i, outcome in enumerate(exit_outcomes, 1):
        elements.append(Paragraph(f"{i}. {outcome}", normal))

    elements.append(PageBreak())

    # Results per component
    elements.append(Paragraph("Results per component", styles["SectionTitle"]))
    elements.append(Paragraph("Achievement: Percentage (70% <= Competent)", styles["Small"]))
    elements.append(Spacer(1, 6))

    if not results_df.empty:
        wrap_center_style = ParagraphStyle(name='WrapCenter', fontName='Helvetica', fontSize=9, leading=11, alignment=1)
        wrap_left_style = ParagraphStyle(name='WrapLeft', fontName='Helvetica', fontSize=9, leading=11, alignment=0)

        elements.append(Paragraph(f"<b>{section_1_name}</b>", styles["SectionTitle"]))
        elements.append(Spacer(1, 12))

        unique_sections = results_df["Section"].unique()
        for section_name in unique_sections:
            section_results = results_df[results_df["Section"] == section_name]
            if not section_results.empty:
                elements.append(Paragraph(f"<b>{section_name}</b>", styles["Small"]))
                elements.append(Spacer(1, 6))

                table_columns = ["Topic Title", "Credits", "Weight (%)", "Achievement: Percentage", "Final EISA Achievement Score"]
                data = [[Paragraph(c, wrap_center_style) for c in table_columns]]
                for _, row in section_results.iterrows():
                    data.append([
                        Paragraph(row.get("topic_name", ""), wrap_left_style),
                        str(int(row["Credits"])) if pd.notna(row.get("Credits")) else "",
                        f"{row.get('Weight (%)', 0):.2f}",
                        Paragraph(f"{row.get('Achievement: Percentage', 0):.2f}", wrap_center_style),
                        Paragraph(f"{row.get('Final EISA Achievement Score', 0):.2f}", wrap_center_style)
                    ])

                col_widths = [73 * mm, 20 * mm, 25 * mm, 35 * mm, 35 * mm]
                tbl = Table(data, colWidths=col_widths, hAlign="LEFT", repeatRows=1)
                tbl.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f2f2f2")),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("ALIGN", (1, 1), (2, -1), "CENTER"),
                    ("ALIGN", (3, 1), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                ]))
                elements.append(tbl)
                elements.append(Spacer(1, 12))

        elements.append(Paragraph(f"Overall Module Result: {overall_score:.2f}% - {overall_status}", normal))
    else:
        elements.append(Paragraph("No assessment results found for this learner.", normal))

    elements.append(PageBreak())

    # Provider declaration
    elements.append(Paragraph("Provider declaration and signature (delegated official)", styles["SectionTitle"]))
    declaration_text = """
    I certify that the information recorded above is a true reflection of the learner's internal assessment achievements for this qualification, and that supporting evidence is available for audit.
    """
    elements.append(Paragraph(declaration_text, normal))
    declaration_kv = [
        ("Name of delegated official", "__________________________________________"),
        ("Designation", "Principal / Academic Manager / Quality and Compliance Lead"),
        ("Signature", "__________________________________________"),
        ("Date issued", "________________")
    ]
    elements.append(Spacer(1, 12))
    elements.append(make_kv_table(declaration_kv, styles=styles))

    if os.path.exists(pdf_output_path):
        try:
            os.remove(pdf_output_path)
        except PermissionError:
            print("Please close the PDF if it's open, then re-run.")
            return None

    doc.build(elements, onFirstPage=on_first_page, onLaterPages=on_later_pages)
    print(f"SOR PDF generated: {pdf_output_path}")
    return pdf_output_path