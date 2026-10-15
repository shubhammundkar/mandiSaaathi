"""Mandi Saathi - Pitch & Product Demo Deck Generator.

Generates a professional 16:9 widescreen presentation deck (PPTX) blending
Hackathon Pitch Deck (VORTEX 2K26) with Real Product Demo & Farmer Impact.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# -----------------------------------------------------------------------------
# Color Palette Constants
# -----------------------------------------------------------------------------
BG_DARK = RGBColor(16, 40, 24)          # Deep Forest Green
BG_LIGHT = RGBColor(246, 248, 246)      # Off-white / light slate
PRIMARY_GREEN = RGBColor(27, 94, 32)    # Dark Green
ACCENT_GREEN = RGBColor(46, 125, 50)    # Forest Leaf Green
LIGHT_GREEN = RGBColor(232, 245, 233)   # Card Green Fill
CARD_BG = RGBColor(255, 255, 255)       # Pure White
CARD_BORDER = RGBColor(215, 226, 218)   # Crisp card border
GOLD_ACCENT = RGBColor(230, 124, 11)    # Warm Amber/Gold
RED_ACCENT = RGBColor(198, 40, 40)      # Danger/Trap Red
BLUE_ACCENT = RGBColor(21, 101, 192)    # Tech Blue
TEXT_DARK = RGBColor(28, 37, 30)        # Main body text
TEXT_MUTED = RGBColor(95, 110, 100)     # Subtitle & caption text
TEXT_WHITE = RGBColor(255, 255, 255)    # White text

FONT_TITLE = "Calibri"
FONT_BODY = "Calibri"


def create_deck(output_path: str):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    def set_slide_background(slide, color: RGBColor):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = color
        bg.line.fill.background()
        return bg

    def add_header(slide, category: str, title: str, subtitle: str = ""):
        # Category Pill Badge
        badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.45), Inches(3.2), Inches(0.35))
        badge.fill.solid()
        badge.fill.fore_color.rgb = LIGHT_GREEN
        badge.line.color.rgb = PRIMARY_GREEN
        badge.line.width = Pt(1)
        tf = badge.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = category.upper()
        p.font.name = FONT_BODY
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = PRIMARY_GREEN
        p.alignment = PP_ALIGN.CENTER

        # Slide Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.82), Inches(11.7), Inches(0.7))
        tf_t = title_box.text_frame
        tf_t.word_wrap = True
        p_t = tf_t.paragraphs[0]
        p_t.text = title
        p_t.font.name = FONT_TITLE
        p_t.font.size = Pt(24)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_DARK

        # Subtitle
        if subtitle:
            p_sub = tf_t.add_paragraph()
            p_sub.text = subtitle
            p_sub.font.name = FONT_BODY
            p_sub.font.size = Pt(12)
            p_sub.font.color.rgb = TEXT_MUTED

    def add_card(slide, left, top, width, height, fill_color=CARD_BG, border_color=CARD_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = fill_color
        if border_color:
            card.line.color.rgb = border_color
            card.line.width = Pt(1.2)
        else:
            card.line.fill.background()
        return card

    # =========================================================================
    # SLIDE 1: Title & Hero Slide (Pitch & Demo)
    # =========================================================================
    slide1 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide1, BG_DARK)

    # Accent Top Banner
    top_bar = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), prs.slide_width, Inches(0.12))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = GOLD_ACCENT
    top_bar.line.fill.background()

    # Event / Hackathon Badge
    h_badge = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(1.0), Inches(4.2), Inches(0.42))
    h_badge.fill.solid()
    h_badge.fill.fore_color.rgb = RGBColor(30, 70, 42)
    h_badge.line.color.rgb = GOLD_ACCENT
    h_badge.line.width = Pt(1)
    tf = h_badge.text_frame
    p = tf.paragraphs[0]
    p.text = "🏆 VORTEX 2K26 HACKATHON PITCH & DEMO"
    p.font.name = FONT_BODY
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = GOLD_ACCENT
    p.alignment = PP_ALIGN.CENTER

    # Hero Main Title
    tbox = slide1.shapes.add_textbox(Inches(1.0), Inches(1.6), Inches(11.3), Inches(2.2))
    tf1 = tbox.text_frame
    tf1.word_wrap = True
    p1 = tf1.paragraphs[0]
    p1.text = "Mandi Saathi (मंडी साथी)"
    p1.font.name = FONT_TITLE
    p1.font.size = Pt(44)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_WHITE

    p2 = tf1.add_paragraph()
    p2.text = "AI-Powered Net-Profit & Smart Selling Advisor for Farmers"
    p2.font.name = FONT_TITLE
    p2.font.size = Pt(22)
    p2.font.color.rgb = RGBColor(165, 214, 167)
    p2.font.bold = True

    p3 = tf1.add_paragraph()
    p3.text = "Protecting Indian farmers from the 'Headline Price Trap' with real economic calculations and native voice AI in Marathi, Hindi & English."
    p3.font.name = FONT_BODY
    p3.font.size = Pt(14)
    p3.font.color.rgb = RGBColor(200, 225, 205)

    # 3 Stat / Impact Cards on Hero
    c_specs = [
        ("₹15k – ₹50k", "Extra Net Profit", "Per harvest saved by avoiding the headline price trap", GOLD_ACCENT),
        ("100% Devanagari", "Voice-First AI", "Native Marathi & Hindi voice interaction for low-literacy farmers", RGBColor(129, 199, 132)),
        ("57/57 Verified", "Deterministic Math", "Real Agmarknet APMC rates, freight models & spoilage metrics", RGBColor(100, 181, 246))
    ]
    for i, (metric, label, desc, color) in enumerate(c_specs):
        left = Inches(1.0 + i * 3.85)
        c = add_card(slide1, left, Inches(4.3), Inches(3.6), Inches(2.3), fill_color=RGBColor(24, 55, 33), border_color=RGBColor(45, 95, 58))
        tf_c = c.text_frame
        tf_c.word_wrap = True
        tf_c.vertical_anchor = MSO_ANCHOR.TOP

        p_m = tf_c.paragraphs[0]
        p_m.text = metric
        p_m.font.name = FONT_TITLE
        p_m.font.size = Pt(26)
        p_m.font.bold = True
        p_m.font.color.rgb = color

        p_l = tf_c.add_paragraph()
        p_l.text = label
        p_l.font.name = FONT_BODY
        p_l.font.size = Pt(13)
        p_l.font.bold = True
        p_l.font.color.rgb = TEXT_WHITE

        p_d = tf_c.add_paragraph()
        p_d.text = desc
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(10.5)
        p_d.font.color.rgb = RGBColor(180, 205, 185)

    # =========================================================================
    # SLIDE 2: The Core Problem — The "Headline Price Trap"
    # =========================================================================
    slide2 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide2, BG_LIGHT)
    add_header(slide2, "The Critical Problem", "The 'Headline Price Trap' in Indian Agriculture",
               "Why farmers lose thousands of rupees chasing distant high prices they see on paper.")

    # 3 Problem Breakdown Cards
    probs = [
        ("1. The Headline Illusion", RED_ACCENT, [
            "Farmers see a high quote on news or WhatsApp (e.g., Vashi ₹2,100/q vs Local Pune ₹1,800/q).",
            "They assume traveling to the big city will automatically yield ₹300/q extra income.",
            "Headline prices completely ignore transport costs, labor, and transit spoilage."
        ]),
        ("2. Hidden Friction Costs", GOLD_ACCENT, [
            "Transport Freight: ₹800–₹2,500 tempo rental per trip eats into margins.",
            "Loading/Unloading & Market Cess: ₹50–₹75/q deducted at distant APMCs.",
            "Perishable Transit Degradation: 2–5% tomato/vegetable loss in non-AC tempos."
        ]),
        ("3. The Auction Cutoff Hazard", PRIMARY_GREEN, [
            "Most APMCs hold morning auctions with cutoffs at 11:00 AM or 12:00 PM.",
            "Long travel delays mean arriving late: forced to sell at 30% distress discount or pay overnight warehouse rent.",
            "Result: Farmer actually pockets LESS cash than selling at their local mandi!"
        ])
    ]

    for i, (title, color, bullets) in enumerate(probs):
        left = Inches(0.8 + i * 3.95)
        card = add_card(slide2, left, Inches(1.75), Inches(3.75), Inches(5.1), fill_color=CARD_BG, border_color=CARD_BORDER)
        
        # Header stripe on card
        stripe = slide2.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, Inches(1.75), Inches(3.75), Inches(0.1))
        stripe.fill.solid()
        stripe.fill.fore_color.rgb = color
        stripe.line.fill.background()

        tf_c = card.text_frame
        tf_c.word_wrap = True
        tf_c.vertical_anchor = MSO_ANCHOR.TOP

        p_t = tf_c.paragraphs[0]
        p_t.text = title
        p_t.font.name = FONT_TITLE
        p_t.font.size = Pt(16)
        p_t.font.bold = True
        p_t.font.color.rgb = color

        for b in bullets:
            p_b = tf_c.add_paragraph()
            p_b.text = "• " + b
            p_b.font.name = FONT_BODY
            p_b.font.size = Pt(11.5)
            p_b.font.color.rgb = TEXT_DARK
            p_b.space_before = Pt(8)

    # =========================================================================
    # SLIDE 3: The Solution — Mandi Saathi
    # =========================================================================
    slide3 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide3, BG_LIGHT)
    add_header(slide3, "The Solution", "Mandi Saathi: India's 1st AI Net-Return Engine",
               "Transforming agricultural selling from speculative guesswork to data-driven net profit.")

    sol_cards = [
        ("💰 Real Net Profit Math", "Calculates Real Cash-in-Pocket", [
            "Deducts vehicle transport costs (diesel + tempo rates).",
            "Deducts mandi cess, loading/unloading labor charges.",
            "Accounts for crop spoilage curve during transit.",
            "Formula: Net Return = Gross Modal - (Freight + Labor + APMC Fee + Spoilage)"
        ], PRIMARY_GREEN),
        ("🎙️ Multilingual Voice AI", "Zero Literacy Barrier", [
            "Voice-first interface in pure Marathi Devanagari, Hindi & English.",
            "Conversational multi-turn context (understands follow-ups).",
            "Auto-translates colloquial speech: '२० क्विंटल', 'दोन गाडी', '५० पोती'.",
            "Text-to-speech audio playback directly speaks the advice to the farmer."
        ], BLUE_ACCENT),
        ("⚖️ Actionable Decision Rules", "Timing & Safety Guardrails", [
            "Multi-Mandi Arbitrage: Ranks all mandis within 300 km by net in-pocket return.",
            "Store vs. Sell: Recommends whether to hold crop for price surges or sell immediately.",
            "Break-Even Threshold: Tells farmer the exact minimum price needed to travel.",
            "Cutoff Alert: Warns when departure time risks missing the auction."
        ], GOLD_ACCENT)
    ]

    for i, (title, subtitle, points, color) in enumerate(sol_cards):
        left = Inches(0.8 + i * 3.95)
        card = add_card(slide3, left, Inches(1.75), Inches(3.75), Inches(5.1), fill_color=CARD_BG, border_color=CARD_BORDER)

        stripe = slide3.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, Inches(1.75), Inches(3.75), Inches(0.1))
        stripe.fill.solid()
        stripe.fill.fore_color.rgb = color
        stripe.line.fill.background()

        tf_c = card.text_frame
        tf_c.word_wrap = True
        tf_c.vertical_anchor = MSO_ANCHOR.TOP

        p_t = tf_c.paragraphs[0]
        p_t.text = title
        p_t.font.name = FONT_TITLE
        p_t.font.size = Pt(16)
        p_t.font.bold = True
        p_t.font.color.rgb = color

        p_sub = tf_c.add_paragraph()
        p_sub.text = subtitle
        p_sub.font.name = FONT_BODY
        p_sub.font.size = Pt(11)
        p_sub.font.bold = True
        p_sub.font.color.rgb = TEXT_MUTED

        for pt in points:
            p_pt = tf_c.add_paragraph()
            p_pt.text = "✓ " + pt
            p_pt.font.name = FONT_BODY
            p_pt.font.size = Pt(11)
            p_pt.font.color.rgb = TEXT_DARK
            p_pt.space_before = Pt(6)

    # =========================================================================
    # SLIDE 4: Core Feature — Multi-Mandi Net Profit Ranker
    # =========================================================================
    slide4 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide4, BG_LIGHT)
    add_header(slide4, "Core Feature 1", "Multi-Mandi Net Profit Ranker",
               "Ranks all reachable APMCs by real net earnings rather than deceptive headline prices.")

    # Left Column: Explanation
    card_left = add_card(slide4, Inches(0.8), Inches(1.75), Inches(4.2), Inches(5.1), fill_color=CARD_BG)
    tf_l = card_left.text_frame
    tf_l.word_wrap = True
    p = tf_l.paragraphs[0]
    p.text = "How the Ranker Works"
    p.font.name = FONT_TITLE
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_GREEN

    pts = [
        "Farmer inputs crop, quantity & home district (e.g., 20 quintals Tomato from Pune).",
        "Engine pulls active daily APMC prices from surrounding districts (Pune, Ahilyanagar, Nashik, Mumbai).",
        "Computes exact road distance (km) and estimated tempo travel time.",
        "Deducts vehicle freight, loading/unloading, market cess, and transit spoilage.",
        "Ranks markets by net return (₹/q) and total earnings in pocket.",
        "Highlights the #1 Winner with auction cutoff verification."
    ]
    for pt in pts:
        p_pt = tf_l.add_paragraph()
        p_pt.text = "• " + pt
        p_pt.font.name = FONT_BODY
        p_pt.font.size = Pt(11.5)
        p_pt.font.color.rgb = TEXT_DARK
        p_pt.space_before = Pt(6)

    # Right Column: UI Simulation Card (Real Example)
    card_right = add_card(slide4, Inches(5.3), Inches(1.75), Inches(7.2), Inches(5.1), fill_color=LIGHT_GREEN, border_color=PRIMARY_GREEN)
    tf_r = card_right.text_frame
    tf_r.word_wrap = True

    p_r1 = tf_r.paragraphs[0]
    p_r1.text = "🏆 WINNER: Sangamner APMC (Ahilyanagar District)"
    p_r1.font.name = FONT_TITLE
    p_r1.font.size = Pt(17)
    p_r1.font.bold = True
    p_r1.font.color.rgb = PRIMARY_GREEN

    sub_r = [
        ("Gross Modal Price:", "₹2,139.00 / quintal"),
        ("Distance & Transit:", "154.0 km (~3.4 hrs by tempo)"),
        ("Transport Deduction:", "-₹5.44 / quintal (tempo freight)"),
        ("Handling & Market Fee:", "-₹53.58 / quintal"),
        ("Transit Spoilage:", "-₹2.00 / quintal (perishable adjustment)"),
        ("Total Net In-Pocket:", "₹1,933.98 / quintal"),
        ("Total Earnings (1020 Q):", "₹1,972,660 net cash"),
        ("Extra Gain vs Local Pune:", "+₹233.83 / quintal (+₹238,506 total gain!)")
    ]
    for lbl, val in sub_r:
        p_s = tf_r.add_paragraph()
        p_s.text = f"{lbl}  {val}"
        p_s.font.name = FONT_BODY
        p_s.font.size = Pt(12)
        p_s.font.color.rgb = TEXT_DARK
        p_s.space_before = Pt(4)

    p_verdict = tf_r.add_paragraph()
    p_verdict.text = "💡 Verdict: Sangamner market offers significantly higher prices that comfortably overcome the transport cost, delivering maximum take-home profit before the 12:00 PM auction."
    p_verdict.font.name = FONT_BODY
    p_verdict.font.size = Pt(11)
    p_verdict.font.bold = True
    p_verdict.font.color.rgb = PRIMARY_GREEN
    p_verdict.space_before = Pt(10)

    # =========================================================================
    # SLIDE 5: Core Feature — "Sell Now vs. Store" Timing Advisor
    # =========================================================================
    slide5 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide5, BG_LIGHT)
    add_header(slide5, "Core Feature 2", "'Sell Now vs. Store' Timing Advisor",
               "Prevents distress selling while protecting farmers against perishable storage decay.")

    cards_s5 = [
        ("Perishable Crop Protection", [
            "Crops like Tomato & Green Vegetables spoil rapidly in standard farm storage.",
            "Degradation rate exceeds 1.5% - 3.0% per day without controlled atmosphere.",
            "Decision Engine Rule: Flags Tomato as strictly non-storable without active cold chain.",
            "Recommendation: 'Sell Today' — Avoids catastrophic weight loss and rotting."
        ], RED_ACCENT),
        ("Durable Commodity Holding", [
            "Crops like Onion, Soybean, Cotton & Wheat can be stored safely.",
            "Forecasts 7-14 day price trends using historical Agmarknet seasonal patterns.",
            "Calculates Net Holding Gain = Expected Price Increase - (Warehouse Rent + 0.5% Shrinkage).",
            "Recommendation: 'Hold for 5 Days' if projected gain exceeds +₹75/q hurdle rate."
        ], PRIMARY_GREEN),
        ("Clear Action Badges", [
            "🟢 'आजच तातडीने विक्री करा' (Sell Immediately Today)",
            "🟡 '५ दिवस साठवून ठेवा' (Store for 5 Days for ₹120/q extra gain)",
            "🔴 'बाजार घसरणीची शक्यता' (Impending Supply Glut - Sell Now)",
            "All recommendations accompanied by a plain-language explanation of costs vs benefits."
        ], GOLD_ACCENT)
    ]

    for i, (title, pts, col) in enumerate(cards_s5):
        left = Inches(0.8 + i * 3.95)
        c = add_card(slide5, left, Inches(1.75), Inches(3.75), Inches(5.1))
        
        stripe = slide5.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, Inches(1.75), Inches(3.75), Inches(0.1))
        stripe.fill.solid()
        stripe.fill.fore_color.rgb = col
        stripe.line.fill.background()

        tf = c.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = FONT_TITLE
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = col

        for pt in pts:
            p_pt = tf.add_paragraph()
            p_pt.text = "• " + pt
            p_pt.font.name = FONT_BODY
            p_pt.font.size = Pt(11.5)
            p_pt.font.color.rgb = TEXT_DARK
            p_pt.space_before = Pt(8)

    # =========================================================================
    # SLIDE 6: Core Feature — Break-Even Math & Cutoff Guards
    # =========================================================================
    slide6 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide6, BG_LIGHT)
    add_header(slide6, "Core Feature 3", "Break-Even Price & Auction Cutoff Guard",
               "Safety guardrails ensuring farmers never risk a long-distance trip on a gamble.")

    # Left Box: Break-Even
    c_be = add_card(slide6, Inches(0.8), Inches(1.75), Inches(5.6), Inches(5.1), fill_color=CARD_BG)
    tf_be = c_be.text_frame
    tf_be.word_wrap = True

    p = tf_be.paragraphs[0]
    p.text = "⚖️ Break-Even Price Calculation"
    p.font.name = FONT_TITLE
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_GREEN

    be_points = [
        "What is it? The exact minimum price the distant mandi must offer to match local net earnings.",
        "Formula:",
        "   Break-Even Price = Local Net Return + Distant Freight + Labor + Spoilage",
        "Example (Pune to Sangamner):",
        "   Local Pune Net Return: ₹1,556 / qtl",
        "   Distant Costs: ₹212 / qtl (freight + fees)",
        "   Break-Even Price: ₹1,768 / qtl",
        "If Sangamner price drops below ₹1,768, traveling there results in a net financial loss! The farmer is safely advised to sell locally in Pune."
    ]
    for pt in be_points:
        p_pt = tf_be.add_paragraph()
        p_pt.text = pt
        p_pt.font.name = FONT_BODY
        p_pt.font.size = Pt(11.5)
        p_pt.font.color.rgb = TEXT_DARK
        p_pt.space_before = Pt(4)

    # Right Box: Auction Cutoff
    c_co = add_card(slide6, Inches(6.9), Inches(1.75), Inches(5.6), Inches(5.1), fill_color=CARD_BG)
    tf_co = c_co.text_frame
    tf_co.word_wrap = True

    p = tf_co.paragraphs[0]
    p.text = "⏱️ Auction Cutoff & Timing Guard"
    p.font.name = FONT_TITLE
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = RED_ACCENT

    co_points = [
        "The Cutoff Reality:",
        "   Most Maharashtra APMCs close morning lot registrations at 11:30 AM or 12:00 PM.",
        "Departure Time Intelligence:",
        "   Mandi Saathi calculates estimated arrival based on distance, vehicle type, and current time.",
        "Late Arrival Warning:",
        "   If arrival is estimated at 12:40 PM, the system warns:",
        "   ⚠️ 'लिलाव वेळ हुकण्याचा संभव (Risk of Missing Cutoff)'",
        "   Distant mandi is automatically flagged or downgraded because arriving after cutoff forces overnight holding or severe distress sale."
    ]
    for pt in co_points:
        p_pt = tf_co.add_paragraph()
        p_pt.text = pt
        p_pt.font.name = FONT_BODY
        p_pt.font.size = Pt(11.5)
        p_pt.font.color.rgb = TEXT_DARK
        p_pt.space_before = Pt(4)

    # =========================================================================
    # SLIDE 7: Farmer Impact Case Study (The Math That Saves Money)
    # =========================================================================
    slide7 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide7, BG_LIGHT)
    add_header(slide7, "Real Farmer Impact", "Case Study: 50 Quintals Tomato from Pune",
               "How Mandi Saathi's math prevented a ₹3,850 loss and delivered +₹18,900 extra profit.")

    # Table Simulation with 3 Cards
    col_data = [
        ("Local Market (Pune)", "Safe Baseline", "₹1,613 / q", "-₹56.54 / q", "₹1,556.46 / q", "₹77,823", "0 km, immediate sale, 0 cutoff risk", CARD_BG, TEXT_DARK),
        ("Headline Trap (Vashi, Mumbai)", "Headline Illusion", "₹1,647 / q", "-₹167.18 / q", "₹1,479.82 / q", "₹73,991", "LOSES ₹3,832 vs staying local due to heavy Mumbai freight!", RGBColor(255, 235, 238), RED_ACCENT),
        ("Mandi Saathi Winner (Sangamner)", "Smart Arbitrage", "₹2,139 / q", "-₹205.02 / q", "₹1,933.98 / q", "₹96,699", "GAINS +₹18,876 net profit after all transport & fees!", LIGHT_GREEN, PRIMARY_GREEN)
    ]

    for i, (mkt_name, badge, gross, costs, net, total, note, bg_col, txt_col) in enumerate(col_data):
        left = Inches(0.8 + i * 3.95)
        c = add_card(slide7, left, Inches(1.75), Inches(3.75), Inches(5.1), fill_color=bg_col, border_color=txt_col)

        tf = c.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.TOP

        p = tf.paragraphs[0]
        p.text = mkt_name
        p.font.name = FONT_TITLE
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = txt_col

        p_b = tf.add_paragraph()
        p_b.text = badge.upper()
        p_b.font.name = FONT_BODY
        p_b.font.size = Pt(10)
        p_b.font.bold = True
        p_b.font.color.rgb = txt_col

        metrics = [
            ("Gross Modal Price:", gross),
            ("Transport & Handling:", costs),
            ("Net In-Pocket / Quintal:", net),
            ("Total In-Pocket Earnings:", total)
        ]
        for m_lbl, m_val in metrics:
            p_m = tf.add_paragraph()
            p_m.text = f"{m_lbl}\n{m_val}"
            p_m.font.name = FONT_BODY
            p_m.font.size = Pt(11)
            p_m.font.bold = True
            p_m.font.color.rgb = TEXT_DARK
            p_m.space_before = Pt(6)

        p_note = tf.add_paragraph()
        p_note.text = f"Outcome:\n{note}"
        p_note.font.name = FONT_BODY
        p_note.font.size = Pt(11)
        p_note.font.bold = True
        p_note.font.color.rgb = txt_col
        p_note.space_before = Pt(8)

    # =========================================================================
    # SLIDE 8: Native Voice AI & Multilingual Product Demo
    # =========================================================================
    slide8 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide8, BG_LIGHT)
    add_header(slide8, "Product Demo", "Voice-First AI in Native Marathi & Hindi",
               "Designed for real rural farmers who prefer speaking over typing.")

    # Left: Chat Dialogue Simulation
    c_chat = add_card(slide8, Inches(0.8), Inches(1.75), Inches(6.8), Inches(5.1), fill_color=CARD_BG)
    tf_ch = c_chat.text_frame
    tf_ch.word_wrap = True

    p = tf_ch.paragraphs[0]
    p.text = "📱 Live Multilingual Dialogue Flow"
    p.font.name = FONT_TITLE
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_GREEN

    convo = [
        ("👨‍🌾 Farmer (Voice - Marathi):", "'1020 किलो क्विंटल आहे. मला पुण्याच्या मध्ये विकायचा आहे.'", BLUE_ACCENT),
        ("🤖 Mandi Saathi (AI Response):", "'तुम्हाला कोणत्या पिकासाठी सल्ला हवा आहे? (उदा. टोमॅटो, कांदा, सोयाबीन, तूर...)'", PRIMARY_GREEN),
        ("👨‍🌾 Farmer (Voice Follow-up):", "'टोमॅटो'", BLUE_ACCENT),
        ("🤖 Mandi Saathi (Smart Advisory):", "'Pune भागातील 1020 क्विंटल टोमॅटोसाठी सर्वात जास्त नफा देणारा बाजार Sangamner आहे!\\n💰 खिशात पडणारा निव्वळ नफा: ₹1,933.98/क्विंटल\\n💵 एकूण निव्वळ उत्पन्न: ₹1,972,660\\n🚚 वाहतूक खर्च: -₹5.44/क्विंटल (154 किमी)\\n⏱️ लिलाव वेळ: सकाळी 12:00 पूर्वी पोहोचावे\\n💡 स्थानिक बाजारापेक्षा +₹233.83/क्विंटल जास्त नफा!'", PRIMARY_GREEN)
    ]

    for speaker, text, col in convo:
        p_sp = tf_ch.add_paragraph()
        p_sp.text = speaker
        p_sp.font.name = FONT_BODY
        p_sp.font.size = Pt(11)
        p_sp.font.bold = True
        p_sp.font.color.rgb = col
        p_sp.space_before = Pt(4)

        p_tx = tf_ch.add_paragraph()
        p_tx.text = text
        p_tx.font.name = FONT_BODY
        p_tx.font.size = Pt(10.5)
        p_tx.font.color.rgb = TEXT_DARK

    # Right: Features of NLP Engine
    c_feat = add_card(slide8, Inches(7.9), Inches(1.75), Inches(4.6), Inches(5.1), fill_color=LIGHT_GREEN, border_color=PRIMARY_GREEN)
    tf_f = c_feat.text_frame
    tf_f.word_wrap = True

    p = tf_f.paragraphs[0]
    p.text = "🎯 Advanced NLP Capabilities"
    p.font.name = FONT_TITLE
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_GREEN

    n_feats = [
        "Colloquial Marathi Extraction: Correctly resolves oblique cases ('पुण्याच्या', 'पुण्यामध्ये', 'नाशिकच्या').",
        "Agricultural Unit Converter: Translates 'पोती' (50kg bags), 'गाडी' (tempo loads), 'टन' (tonnes), and 'किलो' automatically into quintals.",
        "Multi-Turn Session Memory: Remembers quantity and location across consecutive turns.",
        "Zero-Error Audio Speech: Uses Web Speech API for voice capture and native Marathi/Hindi speech synthesis.",
        "Interactive Retry Button: Instant one-click retry bubble if connectivity drops."
    ]
    for nf in n_feats:
        p_nf = tf_f.add_paragraph()
        p_nf.text = "✓ " + nf
        p_nf.font.name = FONT_BODY
        p_nf.font.size = Pt(11)
        p_nf.font.color.rgb = TEXT_DARK
        p_nf.space_before = Pt(6)

    # =========================================================================
    # SLIDE 9: Technical Architecture & Data Pipeline
    # =========================================================================
    slide9 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide9, BG_LIGHT)
    add_header(slide9, "Technical Architecture", "Robust, Low-Latency & Offline-Tolerant",
               "Engineered for high performance, verified calculations, and reliable rural connectivity.")

    arch_cards = [
        ("1. Frontend Layer", BLUE_ACCENT, [
            "Vanilla JS + HTML5 PWA: Zero framework bloat, sub-1-second mobile load time.",
            "Web Speech API: Native voice recognition in 'mr-IN', 'hi-IN', and 'en-IN'.",
            "SpeechSynthesis: Real-time native audio voiceback in farmer's language.",
            "Port-Agnostic Connectivity: Auto-resolves backend on all dev & production ports."
        ]),
        ("2. Backend & NLP", PRIMARY_GREEN, [
            "FastAPI (Python 3.13): Asynchronous, high-throughput REST API.",
            "Hybrid NLP: Deterministic regex parsing + Google Gemini fallback.",
            "Session Cache: In-memory multi-turn conversational context tracking.",
            "Strict Schemas: Pydantic validation across all request & response payloads."
        ]),
        ("3. Data & Economic Engine", GOLD_ACCENT, [
            "Agmarknet Integration: Daily official APMC auction arrivals & prices.",
            "Verified Offline Snapshot: Fallback CSV ensuring zero downtime.",
            "Economic Math Engine: Real distance matrices, fuel tariffs & spoilage curves.",
            "Verified Test Suite: 57/57 automated unit & integration tests passing."
        ])
    ]

    for i, (title, col, pts) in enumerate(arch_cards):
        left = Inches(0.8 + i * 3.95)
        c = add_card(slide9, left, Inches(1.75), Inches(3.75), Inches(5.1))

        stripe = slide9.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, Inches(1.75), Inches(3.75), Inches(0.1))
        stripe.fill.solid()
        stripe.fill.fore_color.rgb = col
        stripe.line.fill.background()

        tf = c.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = FONT_TITLE
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = col

        for pt in pts:
            p_pt = tf.add_paragraph()
            p_pt.text = "• " + pt
            p_pt.font.name = FONT_BODY
            p_pt.font.size = Pt(11.5)
            p_pt.font.color.rgb = TEXT_DARK
            p_pt.space_before = Pt(8)

    # =========================================================================
    # SLIDE 10: Business Model & Market Opportunity
    # =========================================================================
    slide10 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide10, BG_LIGHT)
    add_header(slide10, "Market & Business Model", "Scaling Impact Across 140M+ Indian Farmers",
               "Building a sustainable, high-growth agri-tech ecosystem.")

    biz_cards = [
        ("Free for Small Farmers", "B2C Farmer Adoption", [
            "100% free core advisory: Daily APMC prices, net profit calculations, and voice chat.",
            "Builds massive rural trust and rapid word-of-mouth adoption across Maharashtra villages.",
            "Target: 50,000 active farmers in year 1 across Nashik, Pune & Ahilyanagar belts."
        ], PRIMARY_GREEN),
        ("FPO & Cooperative SaaS", "B2B Enterprise Tier", [
            "Farmer Producer Organizations (FPOs) aggregate 500–2,000 farmers.",
            "Enterprise Dispatch Planner: Aggregates produce across members to plan multi-truck dispatch.",
            "Subscription Model: ₹2,999 - ₹7,999/month per FPO for logistics optimization."
        ], BLUE_ACCENT),
        ("Logistics & Warehouse Monetization", "Marketplace Ecosystem", [
            "Return-Trip Truck Aggregation: Matches farmers with empty return-trip tempos, cutting freight by 35%.",
            "Warehouse Booking Lead-gen: Commission from verified cold storage & dry godowns.",
            "Warehouse Receipt Financing: Partnering with rural banks on verified price collateral."
        ], GOLD_ACCENT)
    ]

    for i, (title, sub, pts, col) in enumerate(biz_cards):
        left = Inches(0.8 + i * 3.95)
        c = add_card(slide10, left, Inches(1.75), Inches(3.75), Inches(5.1))

        stripe = slide10.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, Inches(1.75), Inches(3.75), Inches(0.1))
        stripe.fill.solid()
        stripe.fill.fore_color.rgb = col
        stripe.line.fill.background()

        tf = c.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = FONT_TITLE
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = col

        p_sub = tf.add_paragraph()
        p_sub.text = sub
        p_sub.font.name = FONT_BODY
        p_sub.font.size = Pt(11)
        p_sub.font.bold = True
        p_sub.font.color.rgb = TEXT_MUTED

        for pt in pts:
            p_pt = tf.add_paragraph()
            p_pt.text = "✓ " + pt
            p_pt.font.name = FONT_BODY
            p_pt.font.size = Pt(11)
            p_pt.font.color.rgb = TEXT_DARK
            p_pt.space_before = Pt(8)

    # =========================================================================
    # SLIDE 11: Roadmap & Future Vision
    # =========================================================================
    slide11 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide11, BG_LIGHT)
    add_header(slide11, "Roadmap & Vision", "The Next Steps for Mandi Saathi",
               "From smart selling advisor to complete post-harvest decision engine.")

    phases = [
        ("Phase 1: Now (VORTEX 2K26)", "Core Intelligence Live", [
            "✓ Multi-mandi net profit ranking live.",
            "✓ Voice AI in Marathi, Hindi & English live.",
            "✓ Break-even math & cutoff warnings live.",
            "✓ Verified against official Agmarknet data."
        ], PRIMARY_GREEN),
        ("Phase 2: Q2-Q3 2026", "Zero-App WhatsApp Bot", [
            "• WhatsApp & Telegram Voice Bot: Farmers send voice notes; bot replies with audio advice.",
            "• Collective Truck Pooling: Pool 4–6 small farmers into 1 shared truck.",
            "• Expansion to Gujarat, Madhya Pradesh & Karnataka APMCs."
        ], BLUE_ACCENT),
        ("Phase 3: 2027 & Beyond", "Full Post-Harvest Ecosystem", [
            "• IoT Cold-Chain Integration: Real-time temperature tracking inside transit vehicles.",
            "• Hyperlocal Micro-Weather Alerts: Rain impact on mandi arrival schedules.",
            "• Direct B2B institutional buyer contracts (processing mills, retail chains)."
        ], GOLD_ACCENT)
    ]

    for i, (title, sub, pts, col) in enumerate(phases):
        left = Inches(0.8 + i * 3.95)
        c = add_card(slide11, left, Inches(1.75), Inches(3.75), Inches(5.1))

        stripe = slide11.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, Inches(1.75), Inches(3.75), Inches(0.1))
        stripe.fill.solid()
        stripe.fill.fore_color.rgb = col
        stripe.line.fill.background()

        tf = c.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = FONT_TITLE
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = col

        p_sub = tf.add_paragraph()
        p_sub.text = sub
        p_sub.font.name = FONT_BODY
        p_sub.font.size = Pt(11)
        p_sub.font.bold = True
        p_sub.font.color.rgb = TEXT_MUTED

        for pt in pts:
            p_pt = tf.add_paragraph()
            p_pt.text = pt
            p_pt.font.name = FONT_BODY
            p_pt.font.size = Pt(11.5)
            p_pt.font.color.rgb = TEXT_DARK
            p_pt.space_before = Pt(8)

    # =========================================================================
    # SLIDE 12: Conclusion & Call to Action (Dark Theme)
    # =========================================================================
    slide12 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide12, BG_DARK)

    # Accent Top Banner
    top_bar2 = slide12.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), prs.slide_width, Inches(0.12))
    top_bar2.fill.solid()
    top_bar2.fill.fore_color.rgb = GOLD_ACCENT
    top_bar2.line.fill.background()

    # Title
    tbox12 = slide12.shapes.add_textbox(Inches(1.0), Inches(1.0), Inches(11.3), Inches(1.8))
    tf12 = tbox12.text_frame
    tf12.word_wrap = True
    p1 = tf12.paragraphs[0]
    p1.text = "Mandi Saathi: Transforming Indian Agriculture"
    p1.font.name = FONT_TITLE
    p1.font.size = Pt(36)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_WHITE

    p2 = tf12.add_paragraph()
    p2.text = "From Speculative Guesswork to Guaranteed Take-Home Net Profit"
    p2.font.name = FONT_TITLE
    p2.font.size = Pt(20)
    p2.font.bold = True
    p2.font.color.rgb = GOLD_ACCENT

    # 3 Summary Cards
    concl_cards = [
        ("1. Real In-Pocket Profit", "Never look at gross headline price alone. Calculate true take-home earnings with verified freight, fees & spoilage.", GOLD_ACCENT),
        ("2. Voice-First for Every Farmer", "Zero literacy barrier. Speaks native Marathi & Hindi. Accessible to every farmer with a basic smartphone.", RGBColor(129, 199, 132)),
        ("3. Measurable Economic Impact", "+15% to +25% higher seasonal net profit. Empowering farmers with data sovereignty.", RGBColor(100, 181, 246))
    ]

    for i, (head, desc, col) in enumerate(concl_cards):
        left = Inches(1.0 + i * 3.85)
        c = add_card(slide12, left, Inches(3.2), Inches(3.6), Inches(2.6), fill_color=RGBColor(24, 55, 33), border_color=RGBColor(45, 95, 58))
        tf = c.text_frame
        tf.word_wrap = True
        p_h = tf.paragraphs[0]
        p_h.text = head
        p_h.font.name = FONT_TITLE
        p_h.font.size = Pt(17)
        p_h.font.bold = True
        p_h.font.color.rgb = col

        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(12)
        p_d.font.color.rgb = TEXT_WHITE
        p_d.space_before = Pt(8)

    # Bottom Call to Action Pill
    cta = slide12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(3.2), Inches(6.1), Inches(6.9), Inches(0.8))
    cta.fill.solid()
    cta.fill.fore_color.rgb = GOLD_ACCENT
    cta.line.fill.background()
    tf_cta = cta.text_frame
    p_cta = tf_cta.paragraphs[0]
    p_cta.text = "🌾 Ready for Live Demo & Q&A | Thank You! 🌾"
    p_cta.font.name = FONT_TITLE
    p_cta.font.size = Pt(18)
    p_cta.font.bold = True
    p_cta.font.color.rgb = RGBColor(20, 30, 20)
    p_cta.alignment = PP_ALIGN.CENTER

    prs.save(output_path)
    print(f"Presentation saved successfully to: {output_path}")


if __name__ == "__main__":
    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    out_file = os.path.join(out_dir, "Mandi_Saathi_Pitch_and_Demo_Deck.pptx")
    create_deck(out_file)
