"""Script to generate the Mandi Saathi Startup & Commands Manual as a beautifully styled PDF."""

import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_pdf():
    script_dir = Path(__file__).resolve().parent.parent
    pdf_path = script_dir / "Mandi_Saathi_Startup_Commands_Guide.pdf"

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Theme Colors
    primary_color = colors.HexColor('#1B5E20')    # Deep Forest Green
    secondary_color = colors.HexColor('#2E7D32')  # Medium Forest Green
    accent_blue = colors.HexColor('#0277BD')      # Ocean Blue
    dark_text = colors.HexColor('#212121')
    code_bg = colors.HexColor('#F4F6F8')
    code_border = colors.HexColor('#CFD8DC')
    header_bg = colors.HexColor('#E8F5E9')

    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=primary_color,
        fontName='Helvetica-Bold',
        spaceAfter=3
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#555555'),
        fontName='Helvetica',
        spaceAfter=8
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Heading2'],
        fontSize=12,
        leading=15,
        textColor=secondary_color,
        fontName='Helvetica-Bold',
        spaceBefore=8,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=8.5,
        leading=11.5,
        textColor=dark_text,
        fontName='Helvetica',
        spaceAfter=3
    )

    bold_body = ParagraphStyle(
        'BoldBody',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor('#1B5E20'),
        fontName='Courier-Bold'
    )

    code_desc = ParagraphStyle(
        'CodeDesc',
        parent=styles['Normal'],
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor('#37474F'),
        fontName='Helvetica'
    )

    story = []

    # Title & Subtitle Header
    story.append(Paragraph('Mandi Saathi — Startup & Execution Manual', title_style))
    story.append(Paragraph('AI Price & Sell-Timing Advisor for Indian Farmers • Official Developer & Operator Guide', subtitle_style))
    story.append(HRFlowable(width='100%', thickness=1.5, color=primary_color, spaceAfter=8))

    # 1. Quick Start Commands
    story.append(Paragraph('1. Quick All-In-One Copy-Paste Commands', h1_style))
    story.append(Paragraph('For instant execution, copy and paste either of the following single-line commands into your Windows PowerShell or CMD terminal:', body_style))

    quick_table_data = [
        [
            Paragraph('<b>Option A: Daily Instant Start</b><br/><font color="#555">Navigates to project directory and boots Uvicorn with auto-reload</font>', body_style),
            Paragraph('<code>cd c:\\Users\\ajink\\OneDrive\\Desktop\\project\\mandisathi\\mandiSaaathi; python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload</code>', code_style)
        ],
        [
            Paragraph('<b>Option B: Full Setup & Start</b><br/><font color="#555">Installs/verifies all dependencies first, then boots the server</font>', body_style),
            Paragraph('<code>cd c:\\Users\\ajink\\OneDrive\\Desktop\\project\\mandisathi\\mandiSaaathi; pip install -r requirements.txt; python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload</code>', code_style)
        ]
    ]

    t1 = Table(quick_table_data, colWidths=[180, 360])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), code_bg),
        ('BOX', (0,0), (-1,-1), 1, code_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, code_border),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t1)
    story.append(Spacer(1, 6))

    # 2. Detailed Command Breakdown
    story.append(Paragraph('2. Detailed Command Breakdown & What Each Command Does', h1_style))
    story.append(Paragraph('Below is an in-depth breakdown of what happens behind the scenes for every individual command:', body_style))

    cmd_data = [
        [
            Paragraph('<b>Step & Command</b>', ParagraphStyle('TH1', parent=bold_body, textColor=colors.white)),
            Paragraph('<b>What It Does & Why It Is Needed</b>', ParagraphStyle('TH2', parent=bold_body, textColor=colors.white))
        ],
        [
            Paragraph('<b>1. Change Directory</b><br/><code>cd ...\\mandiSaaathi</code>', code_style),
            Paragraph('Switches your active terminal session to the project directory root. This ensures all relative directory references like <code>backend/</code>, <code>frontend/</code>, and <code>data/</code> resolve accurately.', code_desc)
        ],
        [
            Paragraph('<b>2. Create Virtual Env</b><br/><code>python -m venv .venv</code>', code_style),
            Paragraph('Initializes a dedicated, isolated Python virtual environment inside <code>.venv/</code>. Prevents system package conflicts and isolates versions from other projects on your machine.', code_desc)
        ],
        [
            Paragraph('<b>3. Activate Virtual Env</b><br/><code>.\\.venv\\Scripts\\Activate.ps1</code><br/><i>(or activate.bat in CMD)</i>', code_style),
            Paragraph('Sets your shell PATH to prioritize the virtual environment. Any subsequent <code>pip install</code> or <code>python</code> command operates strictly within this isolated sandbox.', code_desc)
        ],
        [
            Paragraph('<b>4. Install Packages</b><br/><code>pip install -r requirements.txt</code>', code_style),
            Paragraph('Reads <code>requirements.txt</code> and installs core runtime dependencies: <b>FastAPI</b> (API framework), <b>Uvicorn</b> (ASGI web server), <b>Pandas & NumPy</b> (data engines), <b>Pydantic</b> (schema validation), and <b>HTTPX</b> (Gemini client).', code_desc)
        ],
        [
            Paragraph('<b>5. Environment Config</b><br/><code>cp .env.example .env</code>', code_style),
            Paragraph('Creates your local configuration file from the sample template. You can optionally set <code>GEMINI_API_KEY</code> for AI natural language chat parsing, or custom <code>PORT</code> and <code>HOST</code> values.', code_desc)
        ],
        [
            Paragraph('<b>6. Launch Web Server</b><br/><code>python -m uvicorn backend.main:app<br/>--host 127.0.0.1 --port 8000 --reload</code>', code_style),
            Paragraph('Boots the ASGI application on port 8000. <b>Crucial feature:</b> FastAPI automatically serves <b>both</b> the backend API and the static frontend UI simultaneously at <code>http://localhost:8000</code> via Starlette static file mounting!', code_desc)
        ]
    ]

    t2 = Table(cmd_data, colWidths=[200, 340])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, code_bg]),
        ('BOX', (0,0), (-1,-1), 1, code_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, code_border),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t2)
    story.append(Spacer(1, 6))

    # 3. Uvicorn Flags Breakdown
    story.append(Paragraph('3. Understanding the Uvicorn Command Arguments', h1_style))
    flags_data = [
        [Paragraph('<b>Argument / Flag</b>', bold_body), Paragraph('<b>Technical Purpose & Function</b>', bold_body)],
        [Paragraph('<code>backend.main:app</code>', code_style), Paragraph('Tells Uvicorn to import module <code>backend.main</code> and locate the ASGI instance named <code>app</code>.', body_style)],
        [Paragraph('<code>--host 127.0.0.1</code>', code_style), Paragraph('Binds locally to localhost. Use <code>--host 0.0.0.0</code> when deploying inside Docker or cloud containers (Render/Railway).', body_style)],
        [Paragraph('<code>--port 8000</code>', code_style), Paragraph('Sets the TCP port listener. If port 8000 is occupied, you can change this to 8080 or any free port.', body_style)],
        [Paragraph('<code>--reload</code>', code_style), Paragraph('Enables hot-reload mode for development. The server monitors Python files and reloads instantly when files change.', body_style)]
    ]
    t_flags = Table(flags_data, colWidths=[160, 380])
    t_flags.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#ECEFF1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, code_bg]),
        ('BOX', (0,0), (-1,-1), 1, code_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, code_border),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_flags)
    story.append(Spacer(1, 10))
    story.append(PageBreak())

    # 4. URLs
    story.append(Paragraph('4. Application Access URLs', h1_style))
    urls_data = [
        [Paragraph('<b>View / Resource</b>', bold_body), Paragraph('<b>URL</b>', bold_body), Paragraph('<b>Description</b>', bold_body)],
        [Paragraph('<b>Main App UI</b>', body_style), Paragraph('http://localhost:8000', code_style), Paragraph('Interactive Single Page App (Advisor, Chat, Alerts, Proof, About)', body_style)],
        [Paragraph('<b>Health Check</b>', body_style), Paragraph('http://localhost:8000/api/health', code_style), Paragraph('Returns <code>{"status":"ok"}</code> confirming backend is healthy', body_style)],
        [Paragraph('<b>Data Status</b>', body_style), Paragraph('http://localhost:8000/api/data-status', code_style), Paragraph('Displays status of 6,630 verified Agmarknet historical records', body_style)],
        [Paragraph('<b>Swagger Docs</b>', body_style), Paragraph('http://localhost:8000/docs', code_style), Paragraph('Interactive OpenAPI/Swagger documentation for testing all routes', body_style)]
    ]
    t_urls = Table(urls_data, colWidths=[110, 180, 250])
    t_urls.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), header_bg),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, code_bg]),
        ('BOX', (0,0), (-1,-1), 1, code_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, code_border),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_urls)
    story.append(Spacer(1, 6))

    # 5. Maintenance & Useful Commands
    story.append(Paragraph('5. Utility & Testing Commands', h1_style))
    utils_data = [
        [Paragraph('<b>Action</b>', bold_body), Paragraph('<b>Command</b>', bold_body), Paragraph('<b>Description</b>', bold_body)],
        [Paragraph('<b>Run Tests</b>', body_style), Paragraph('python -m pytest', code_style), Paragraph('Executes all 51 automated test cases across the entire suite', body_style)],
        [Paragraph('<b>Backfill Data</b>', body_style), Paragraph('python scripts/backfill.py', code_style), Paragraph('Ingests 90 days of Agmarknet historical records into SQLite', body_style)],
        [Paragraph('<b>Load CSV</b>', body_style), Paragraph('python scripts/load_manual_csv.py &lt;file&gt;', code_style), Paragraph('Loads downloaded Agmarknet CSV into the SQLite database', body_style)],
        [Paragraph('<b>Stop Server</b>', body_style), Paragraph('Press Ctrl + C', code_style), Paragraph('Sends SIGINT to safely terminate the running Uvicorn server', body_style)]
    ]
    t_utils = Table(utils_data, colWidths=[110, 200, 230])
    t_utils.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#ECEFF1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, code_bg]),
        ('BOX', (0,0), (-1,-1), 1, code_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, code_border),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_utils)
    story.append(Spacer(1, 6))

    # 6. Troubleshooting
    story.append(Paragraph('6. Common Troubleshooting Scenarios', h1_style))
    faq_data = [
        [Paragraph('<b>Issue / Error Message</b>', bold_body), Paragraph('<b>Root Cause & Instant Resolution</b>', bold_body)],
        [
            Paragraph('<b>Unable to Connect to Mandi Engine</b>', code_style),
            Paragraph('The backend Uvicorn process is not running. Launch the server using <code>python -m uvicorn backend.main:app --port 8000</code> and refresh the page.', body_style)
        ],
        [
            Paragraph('<b>Port 8000 Already in Use (WinError 10048)</b>', code_style),
            Paragraph('Another background process is holding port 8000. Run <code>netstat -ano | findstr :8000</code> to find the PID and kill it, or launch on <code>--port 8080</code>.', body_style)
        ],
        [
            Paragraph('<b>PowerShell ExecutionPolicy Error</b>', code_style),
            Paragraph('Run <code>Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass</code> before activating the virtual environment.', body_style)
        ]
    ]
    t_faq = Table(faq_data, colWidths=[180, 360])
    t_faq.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#FFEBEE')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, code_bg]),
        ('BOX', (0,0), (-1,-1), 1, code_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, code_border),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_faq)
    story.append(Spacer(1, 14))
    story.append(HRFlowable(width='100%', thickness=1, color=colors.HexColor('#B0BEC5'), spaceAfter=6))
    footer_style = ParagraphStyle(
        'FooterNote',
        parent=styles['Normal'],
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#78909C'),
        alignment=1
    )
    story.append(Paragraph('Mandi Saathi Engineering Manual • Hackathon VORTEX 2K26 • Data Source: Agmarknet (agmarknet.gov.in)', footer_style))

    doc.build(story)
    print(f"SUCCESS: PDF generated at: {pdf_path}")
    print(f"File size: {os.path.getsize(pdf_path):,} bytes")

if __name__ == "__main__":
    generate_pdf()
