import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def generate_weekly_wellness_pdf(
    output_path, 
    user_id=1001, 
    user_name="Student User", 
    avg_screen_time=8.4, 
    daily_unlocks=92, 
    sleep_hrs=5.5, 
    top_app="Instagram", 
    risk_level="High Risk",
    ai_recommendations=None
):
    """
    Generates a PDF Digital Wellness Report for Smartphone Addiction Analysis.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom Palette
    COLOR_PRIMARY = colors.HexColor("#1e293b")
    COLOR_ACCENT = colors.HexColor("#3b82f6")
    COLOR_DANGER = colors.HexColor("#ef4444")
    COLOR_SUCCESS = colors.HexColor("#10b981")
    COLOR_BG = colors.HexColor("#f8fafc")
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=22,
        leading=26,
        textColor=COLOR_PRIMARY,
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=15
    )
    
    heading2_style = ParagraphStyle(
        'Heading2',
        parent=styles['Heading2'],
        fontSize=14,
        leading=18,
        textColor=COLOR_PRIMARY,
        spaceBefore=12,
        spaceAfter=8
    )
    
    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['BodyText'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#334155")
    )
    
    # Header
    story.append(Paragraph("📱 Weekly Digital Wellness Report", title_style))
    story.append(Paragraph(f"User ID: USR_{user_id} | Platform: Smartphone Addiction Behavior Intelligence", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=COLOR_ACCENT, spaceBefore=0, spaceAfter=15))
    
    # Risk Level Banner
    risk_color = COLOR_DANGER if risk_level == "High Risk" else (colors.HexColor("#f59e0b") if risk_level == "Medium Risk" else COLOR_SUCCESS)
    risk_banner_data = [
        [Paragraph(f"<b>ADDICTION RISK STATUS:</b> <font color='{risk_color.hexval()}'><b>{risk_level.upper()}</b></font>", ParagraphStyle('RB', parent=body_style, fontSize=12, textColor=COLOR_PRIMARY))]
    ]
    banner_table = Table(risk_banner_data, colWidths=[540])
    banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
        ('BORDER', (0, 0), (-1, -1), 1, risk_color),
        ('PADDING', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER')
    ]))
    story.append(banner_table)
    story.append(Spacer(1, 15))
    
    # Key User Metrics Table
    story.append(Paragraph("📊 Behavioral & Telemetry Metrics", heading2_style))
    
    metrics_data = [
        ["Metric Description", "Recorded Value", "Target Health Threshold"],
        ["Average Daily Screen Time", f"{avg_screen_time} Hours", "< 4.5 Hours / Day"],
        ["Daily Unlock Count", f"{daily_unlocks} Unlocks / Day", "< 50 Unlocks / Day"],
        ["Average Sleep Duration", f"{sleep_hrs} Hours", "7.0 - 8.5 Hours / Night"],
        ["Most Used App", top_app, "Productivity Focus"],
        ["Social Media % of Total Usage", "58%", "< 25% Total Screen Time"]
    ]
    
    metrics_table = Table(metrics_data, colWidths=[200, 170, 170])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, COLOR_BG]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
    ]))
    story.append(metrics_table)
    story.append(Spacer(1, 15))
    
    # AI Personalized Recommendations
    story.append(Paragraph("🧠 AI-Powered Digital Wellbeing Recommendations", heading2_style))
    
    if ai_recommendations is None:
        ai_recommendations = [
            f"Your daily screen time ({avg_screen_time} hrs) is significantly above healthy thresholds. Set strict daily app limits on {top_app}.",
            "Enable 'Bedtime Focus Mode' after 10:00 PM to improve sleep duration and reduce late-night screen pickups.",
            "Batch notifications to arrive every 2 hours rather than instantly to break the impulsive re-checking habit."
        ]
        
    for rec in ai_recommendations:
        bullet_text = f"• {rec}"
        story.append(Paragraph(bullet_text, body_style))
        story.append(Spacer(1, 4))
        
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1"), spaceBefore=10, spaceAfter=10))
    story.append(Paragraph("<font size=8 color='#94a3b8'>Generated by Smartphone Addiction Analytics Platform | AI-Native Behavioral Intelligence Engine</font>", ParagraphStyle('Footer', parent=body_style, alignment=1)))
    
    doc.build(story)
    return output_path

if __name__ == '__main__':
    test_pdf = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'Weekly_Digital_Wellness_Report.pdf')
    generate_weekly_wellness_pdf(test_pdf)
    print("PDF Report generated successfully!")
