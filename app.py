import streamlit as st
import pandas as pd
import datetime
import json
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
import io
import base64
from PIL import Image
import qrcode
import tempfile

# ==================== CONFIGURATION ====================
CONFIG = {
    'app_name': '🧾 Professional Receipt Generator',
    'company_name': 'ABC MART',
    'company_tagline': 'Your Trust, Our Priority',
    'company_address': '123 Main Street, Lahore, Pakistan',
    'company_phone': '+92 300 1234567',
    'company_email': 'abcmart.pk@gmail.com',
    'currency_symbol': 'PKR',
    'receipt_prefix': 'RCP',
    'date_format': '%d-%m-%Y',
    'time_format': '%I:%M %p',
    'primary_color': '#1a73e8',
    'secondary_color': '#0d47a1',
    'success_color': '#0f9d58',
    'danger_color': '#d93025',
    'tax_default': 10.0,
    'discount_default': 5.0,
    'shipping_default': 0.0,
    'payment_methods': ['Cash', 'Card', 'Easypaisa', 'JazzCash', 'Bank', 'Crypto'],
    'payment_statuses': ['Paid', 'Unpaid', 'Partial'],
    'dark_mode_default': False,
    'auto_save': True,
    'receipt_folder': 'receipts'
}

# ==================== CUSTOM STYLES ====================

def get_custom_css():
    dark_mode = st.session_state.get('dark_mode', CONFIG['dark_mode_default'])
    
    if dark_mode:
        return """
        <style>
        .stApp {
            background: linear-gradient(135deg, #0a0e1a 0%, #1a1f2e 100%);
        }
        .main-header {
            background: linear-gradient(135deg, #1a73e8 0%, #0d47a1 100%);
            padding: 2rem;
            border-radius: 20px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 20px 60px rgba(26, 115, 232, 0.3);
        }
        .main-header h1 {
            margin: 0;
            font-size: 2.8rem;
            font-weight: 700;
        }
        .main-header p {
            margin: 0.5rem 0 0 0;
            opacity: 0.9;
        }
        .dashboard-card {
            background: linear-gradient(145deg, #1a1f2e, #0d1117);
            padding: 1.8rem;
            border-radius: 20px;
            border: 1px solid rgba(255,255,255,0.08);
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            margin-bottom: 1.5rem;
        }
        .stButton>button {
            background: linear-gradient(135deg, #1a73e8 0%, #0d47a1 100%);
            color: white;
            border: none;
            padding: 0.6rem 1.2rem;
            border-radius: 10px;
            font-weight: 600;
            transition: all 0.3s ease;
            width: 100%;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(26, 115, 232, 0.4);
        }
        .stat-number {
            font-size: 2.2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #1a73e8, #4fc3f7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .receipt-container {
            background: white;
            padding: 2rem 2.5rem;
            border-radius: 16px;
            border: 1px solid #e0e0e0;
            color: #000000;
            font-family: Arial, sans-serif;
            width: 100%;
            max-width: 100%;
            margin: 0 auto;
            box-sizing: border-box;
        }
        .receipt-container .row {
            display: flex !important;
            justify-content: space-between !important;
            padding: 8px 0 !important;
            border-bottom: 1px solid #eee !important;
            width: 100% !important;
        }
        .receipt-container .row span {
            color: #000000 !important;
        }
        .receipt-container .header {
            text-align: center !important;
            border-bottom: 2px solid #1a73e8 !important;
            padding-bottom: 15px !important;
            margin-bottom: 15px !important;
            width: 100% !important;
        }
        .receipt-container .header h3 {
            color: #1a73e8 !important;
            margin: 0 !important;
            font-size: 1.8rem !important;
            font-weight: 700 !important;
        }
        .receipt-container .header small {
            color: #666 !important;
            font-size: 0.9rem !important;
        }
        .receipt-container .total {
            border-top: 2px solid #1a73e8 !important;
            padding-top: 15px !important;
            margin-top: 15px !important;
            width: 100% !important;
        }
        .receipt-container .total .row {
            border-bottom: none !important;
            font-size: 1.4rem !important;
            font-weight: 700 !important;
            color: #1a73e8 !important;
        }
        .receipt-container .total .row span {
            color: #1a73e8 !important;
        }
        .receipt-wrapper {
            width: 100% !important;
            padding: 0 !important;
            margin: 0 !important;
        }
        .stColumn {
            padding: 0 0.5rem !important;
        }
        /* Fix for delete button */
        .stButton button[data-testid="baseButton-secondary"] {
            background: #d93025 !important;
        }
        </style>
        """
    else:
        return """
        <style>
        .main-header {
            background: linear-gradient(135deg, #1a73e8 0%, #0d47a1 100%);
            padding: 2rem;
            border-radius: 20px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 20px 60px rgba(26, 115, 232, 0.2);
        }
        .main-header h1 {
            margin: 0;
            font-size: 2.8rem;
            font-weight: 700;
        }
        .main-header p {
            margin: 0.5rem 0 0 0;
            opacity: 0.9;
        }
        .dashboard-card {
            background: white;
            padding: 1.8rem;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.06);
            border: 1px solid rgba(0,0,0,0.05);
            margin-bottom: 1.5rem;
        }
        .stButton>button {
            background: linear-gradient(135deg, #1a73e8 0%, #0d47a1 100%);
            color: white;
            border: none;
            padding: 0.6rem 1.2rem;
            border-radius: 10px;
            font-weight: 600;
            transition: all 0.3s ease;
            width: 100%;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(26, 115, 232, 0.3);
        }
        .stat-number {
            font-size: 2.2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #1a73e8, #4fc3f7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .receipt-container {
            background: white;
            padding: 2rem 2.5rem;
            border-radius: 16px;
            border: 1px solid #e0e0e0;
            color: #000000;
            font-family: Arial, sans-serif;
            width: 100%;
            max-width: 100%;
            margin: 0 auto;
            box-sizing: border-box;
        }
        .receipt-container .row {
            display: flex !important;
            justify-content: space-between !important;
            padding: 8px 0 !important;
            border-bottom: 1px solid #eee !important;
            width: 100% !important;
        }
        .receipt-container .row span {
            color: #000000 !important;
        }
        .receipt-container .header {
            text-align: center !important;
            border-bottom: 2px solid #1a73e8 !important;
            padding-bottom: 15px !important;
            margin-bottom: 15px !important;
            width: 100% !important;
        }
        .receipt-container .header h3 {
            color: #1a73e8 !important;
            margin: 0 !important;
            font-size: 1.8rem !important;
            font-weight: 700 !important;
        }
        .receipt-container .header small {
            color: #666 !important;
            font-size: 0.9rem !important;
        }
        .receipt-container .total {
            border-top: 2px solid #1a73e8 !important;
            padding-top: 15px !important;
            margin-top: 15px !important;
            width: 100% !important;
        }
        .receipt-container .total .row {
            border-bottom: none !important;
            font-size: 1.4rem !important;
            font-weight: 700 !important;
            color: #1a73e8 !important;
        }
        .receipt-container .total .row span {
            color: #1a73e8 !important;
        }
        .receipt-wrapper {
            width: 100% !important;
            padding: 0 !important;
            margin: 0 !important;
        }
        .stColumn {
            padding: 0 0.5rem !important;
        }
        /* Fix for delete button */
        .stButton button[data-testid="baseButton-secondary"] {
            background: #d93025 !important;
        }
        </style>
        """

# ==================== DATA MANAGEMENT ====================

def init_session_state():
    defaults = {
        'receipts': [],
        'receipt_counter': 1,
        'dark_mode': CONFIG['dark_mode_default'],
        'product_items': [],
        'products_db': [],
        'customers_db': [],
        'settings': CONFIG.copy(),
        'editing_product_id': None,
        'editing_receipt_id': None,
        'editing_customer_id': None,
        'keep_cart_after_save': False,
        'pdf_download_ready': None  # Store PDF data for download
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    
    if not os.path.exists(CONFIG['receipt_folder']):
        os.makedirs(CONFIG['receipt_folder'])
    
    data_file = os.path.join(CONFIG['receipt_folder'], 'receipts_data.json')
    if os.path.exists(data_file):
        try:
            with open(data_file, 'r') as f:
                data = json.load(f)
                st.session_state.receipts = data.get('receipts', [])
                st.session_state.receipt_counter = data.get('counter', 1)
                st.session_state.products_db = data.get('products', [])
                st.session_state.customers_db = data.get('customers', [])
        except:
            pass

def save_data():
    try:
        data = {
            'receipts': st.session_state.receipts,
            'counter': st.session_state.receipt_counter,
            'products': st.session_state.products_db,
            'customers': st.session_state.customers_db,
            'last_saved': datetime.datetime.now().strftime(CONFIG['date_format'])
        }
        
        data_file = os.path.join(CONFIG['receipt_folder'], 'receipts_data.json')
        with open(data_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        for receipt in st.session_state.receipts:
            receipt_file = os.path.join(CONFIG['receipt_folder'], f"receipt_{receipt['receipt_number']}.json")
            with open(receipt_file, 'w') as f:
                json.dump(receipt, f, indent=2)
        return True
    except:
        return False

# ==================== QR CODE GENERATION ====================

def generate_qr(receipt_number):
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(f"Receipt: {receipt_number}")
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()
        return qr_base64
    except:
        return None

# ==================== RECEIPT FUNCTIONS ====================

def generate_receipt_number():
    prefix = CONFIG['receipt_prefix']
    timestamp = datetime.datetime.now().strftime("%Y%m%d")
    number = str(st.session_state.receipt_counter).zfill(3)
    st.session_state.receipt_counter += 1
    save_data()
    return f"{prefix}-{timestamp}-{number}"

def calculate_totals(items, discount=0, tax=0, shipping=0):
    if not items:
        return 0, 0, 0, 0, 0
    try:
        subtotal = sum(item.get('total', 0) for item in items)
        discount_amount = (subtotal * discount) / 100
        tax_amount = ((subtotal - discount_amount) * tax) / 100
        grand_total = subtotal - discount_amount + tax_amount + shipping
        return subtotal, discount_amount, tax_amount, shipping, grand_total
    except:
        return 0, 0, 0, 0, 0

# ==================== CUSTOMER MANAGEMENT FUNCTIONS ====================

def add_customer(name, phone, email, address):
    customer = {
        'id': len(st.session_state.customers_db) + 1,
        'name': name,
        'phone': phone,
        'email': email,
        'address': address,
        'total_purchases': 0,
        'total_spent': 0,
        'first_purchase': datetime.datetime.now().strftime(CONFIG['date_format']),
        'last_purchase': datetime.datetime.now().strftime(CONFIG['date_format']),
        'created_at': datetime.datetime.now().strftime(CONFIG['date_format'])
    }
    st.session_state.customers_db.append(customer)
    save_data()
    return customer

def update_customer(customer_id, name, phone, email, address):
    for customer in st.session_state.customers_db:
        if customer['id'] == customer_id:
            customer['name'] = name
            customer['phone'] = phone
            customer['email'] = email
            customer['address'] = address
            break
    save_data()

def delete_customer(customer_id):
    st.session_state.customers_db = [c for c in st.session_state.customers_db if c['id'] != customer_id]
    save_data()

def get_customer_receipts(email):
    return [r for r in st.session_state.receipts if r.get('customer_email') == email]

# ==================== PDF GENERATION - EXACT ABC MART LAYOUT ====================

def generate_pdf(receipt_data):
    """Generate PDF receipt with exact ABC MART layout"""
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                               rightMargin=1.5*cm, leftMargin=1.5*cm,
                               topMargin=2*cm, bottomMargin=2*cm)
        
        styles = getSampleStyleSheet()
        story = []
        
        currency = CONFIG['currency_symbol']
        primary_color = '#1a73e8'
        
        # ===== STYLES =====
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor(primary_color),
            alignment=TA_CENTER,
            spaceAfter=2,
            fontName='Helvetica-Bold'
        )
        
        tagline_style = ParagraphStyle(
            'Tagline',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER,
            spaceAfter=8
        )
        
        contact_style = ParagraphStyle(
            'Contact',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER,
            spaceAfter=2
        )
        
        divider_style = ParagraphStyle(
            'Divider',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor(primary_color),
            alignment=TA_CENTER,
            spaceAfter=6,
            spaceBefore=6
        )
        
        info_label_style = ParagraphStyle(
            'InfoLabel',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            fontName='Helvetica-Bold'
        )
        
        info_value_style = ParagraphStyle(
            'InfoValue',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#333333')
        )
        
        payment_style = ParagraphStyle(
            'Payment',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#333333'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor(primary_color),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            spaceAfter=4
        )
        
        footer_sub_style = ParagraphStyle(
            'FooterSub',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER,
            spaceAfter=8
        )
        
        receipt_no_style = ParagraphStyle(
            'ReceiptNo',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#999999'),
            alignment=TA_CENTER,
            spaceAfter=4
        )
        
        # ===== BUILD RECEIPT =====
        story.append(Paragraph(CONFIG['company_name'], title_style))
        story.append(Paragraph(CONFIG['company_tagline'], tagline_style))
        story.append(Paragraph(CONFIG['company_address'], contact_style))
        story.append(Paragraph(f"Phone: {CONFIG['company_phone']}", contact_style))
        story.append(Paragraph(f"Email: {CONFIG['company_email']}", contact_style))
        story.append(Spacer(1, 0.1*inch))
        
        story.append(Paragraph("—" * 45, divider_style))
        story.append(Spacer(1, 0.05*inch))
        
        info_data = []
        info_data.append([Paragraph("Receipt No", info_label_style), Paragraph(":", info_label_style), 
                         Paragraph(receipt_data.get('receipt_number', 'N/A'), info_value_style)])
        info_data.append([Paragraph("Date", info_label_style), Paragraph(":", info_label_style), 
                         Paragraph(receipt_data.get('date', 'N/A'), info_value_style)])
        info_data.append([Paragraph("Cashier", info_label_style), Paragraph(":", info_label_style), 
                         Paragraph("Admin", info_value_style)])
        info_data.append([Paragraph("Time", info_label_style), Paragraph(":", info_label_style), 
                         Paragraph(receipt_data.get('time', datetime.datetime.now().strftime(CONFIG['time_format'])), info_value_style)])
        info_data.append([Paragraph("Customer", info_label_style), Paragraph(":", info_label_style), 
                         Paragraph(receipt_data.get('customer_name', 'Walk-in Customer'), info_value_style)])
        
        info_table = Table(info_data, colWidths=[1.8*inch, 0.3*inch, 3.5*inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.05*inch))
        
        story.append(Paragraph("—" * 45, divider_style))
        story.append(Spacer(1, 0.05*inch))
        
        item_data = []
        item_data.append([
            Paragraph('<b>Item</b>', styles['Normal']),
            Paragraph('<b>Qty</b>', styles['Normal']),
            Paragraph('<b>Unit Price</b>', styles['Normal']),
            Paragraph('<b>Total Price</b>', styles['Normal'])
        ])
        
        for item in receipt_data.get('items', []):
            item_data.append([
                Paragraph(item.get('name', ''), styles['Normal']),
                str(item.get('quantity', 0)),
                f"{currency} {item.get('price', 0):.2f}",
                f"{currency} {item.get('total', 0):.2f}"
            ])
        
        item_table = Table(item_data, colWidths=[2.5*inch, 0.8*inch, 1.5*inch, 1.8*inch])
        item_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(primary_color)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(item_table)
        story.append(Spacer(1, 0.05*inch))
        
        story.append(Paragraph("—" * 45, divider_style))
        story.append(Spacer(1, 0.05*inch))
        
        subtotal = receipt_data.get('subtotal', 0)
        discount = receipt_data.get('discount', 0)
        discount_amount = receipt_data.get('discount_amount', 0)
        tax = receipt_data.get('tax', 0)
        tax_amount = receipt_data.get('tax_amount', 0)
        grand_total = receipt_data.get('grand_total', 0)
        amount_paid = receipt_data.get('amount_paid', grand_total)
        change_returned = amount_paid - grand_total if amount_paid > grand_total else 0
        
        totals_data = []
        totals_data.append([Paragraph('Subtotal', info_label_style), 
                           Paragraph(f"{currency} {subtotal:.2f}", info_value_style)])
        
        if discount > 0:
            totals_data.append([Paragraph(f'Discount ({discount}%)', info_label_style), 
                               Paragraph(f"-{currency} {discount_amount:.2f}", info_value_style)])
        
        if tax > 0:
            totals_data.append([Paragraph(f'Tax ({tax}%)', info_label_style), 
                               Paragraph(f"{currency} {tax_amount:.2f}", info_value_style)])
        
        totals_data.append([Paragraph('<b>Grand Total</b>', styles['Normal']), 
                           Paragraph(f"<b>{currency} {grand_total:.2f}</b>", styles['Normal'])])
        totals_data.append([Paragraph('Amount Paid', info_label_style), 
                           Paragraph(f"{currency} {amount_paid:.2f}", info_value_style)])
        
        if change_returned > 0:
            totals_data.append([Paragraph('Change Returned', info_label_style), 
                               Paragraph(f"{currency} {change_returned:.2f}", info_value_style)])
        
        totals_table = Table(totals_data, colWidths=[4.2*inch, 2.5*inch])
        totals_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('TEXTCOLOR', (0, -3), (0, -3), colors.HexColor('#333333')),
            ('TEXTCOLOR', (1, -3), (1, -3), colors.HexColor('#333333')),
            ('TEXTCOLOR', (0, -2), (0, -2), colors.HexColor(primary_color)),
            ('TEXTCOLOR', (1, -2), (1, -2), colors.HexColor(primary_color)),
            ('FONTNAME', (0, -2), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -2), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(totals_table)
        story.append(Spacer(1, 0.05*inch))
        
        story.append(Paragraph("—" * 45, divider_style))
        story.append(Spacer(1, 0.05*inch))
        
        story.append(Paragraph(f"Payment Method : {receipt_data.get('payment_method', 'N/A')}", payment_style))
        story.append(Spacer(1, 0.05*inch))
        
        story.append(Paragraph("—" * 45, divider_style))
        story.append(Spacer(1, 0.05*inch))
        
        story.append(Paragraph("Thank you for shopping with us!", footer_style))
        story.append(Paragraph("Please visit again.", footer_sub_style))
        story.append(Spacer(1, 0.05*inch))
        
        qr_data = generate_qr(receipt_data.get('receipt_number', 'N/A'))
        if qr_data:
            try:
                qr_img = base64.b64decode(qr_data)
                qr_io = io.BytesIO(qr_img)
                qr_img_obj = RLImage(qr_io, width=1.2*inch, height=1.2*inch)
                qr_table = Table([[qr_img_obj]], colWidths=[6*inch])
                qr_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                story.append(qr_table)
            except:
                pass
        
        story.append(Spacer(1, 0.05*inch))
        story.append(Paragraph(receipt_data.get('receipt_number', 'N/A'), receipt_no_style))
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    except Exception as e:
        st.error(f"PDF Generation Error: {str(e)}")
        return None

# ==================== RECEIPT PREVIEW ====================

def display_receipt_preview(receipt_data):
    """Display receipt preview in ABC MART style"""
    currency = CONFIG['currency_symbol']
    
    html_content = f"""
    <div class="receipt-wrapper">
    <div class="receipt-container">
        <div class="header">
            <h3>{CONFIG['company_name']}</h3>
            <small>{CONFIG['company_tagline']}</small><br>
            <small>{CONFIG['company_address']}</small><br>
            <small>Phone: {CONFIG['company_phone']}</small><br>
            <small>Email: {CONFIG['company_email']}</small>
        </div>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2px 20px; margin-bottom: 10px; padding-bottom: 10px; border-bottom: 1px solid #ccc;">
            <div><strong>Receipt No</strong><br>{receipt_data.get('receipt_number', 'N/A')}</div>
            <div><strong>Date</strong><br>{receipt_data.get('date', 'N/A')}</div>
            <div><strong>Cashier</strong><br>Admin</div>
            <div><strong>Time</strong><br>{receipt_data.get('time', datetime.datetime.now().strftime(CONFIG['time_format']))}</div>
            <div><strong>Customer</strong><br>{receipt_data.get('customer_name', 'Walk-in Customer')}</div>
        </div>
        
        <div style="border-top: 1px solid #ccc; border-bottom: 1px solid #ccc; padding: 10px 0; margin: 10px 0;">
            <div style="display: grid; grid-template-columns: 2.5fr 0.8fr 1.2fr 1.5fr; font-weight: 700; padding: 8px 0; border-bottom: 2px solid #1a73e8; color: #1a73e8;">
                <span>Item</span>
                <span style="text-align: center;">Qty</span>
                <span style="text-align: right;">Unit Price</span>
                <span style="text-align: right;">Total Price</span>
            </div>
    """
    
    for item in receipt_data.get('items', []):
        html_content += f"""
            <div style="display: grid; grid-template-columns: 2.5fr 0.8fr 1.2fr 1.5fr; padding: 6px 0; border-bottom: 1px dashed #ddd;">
                <span>{item.get('name', '')}</span>
                <span style="text-align: center;">{item.get('quantity', 0)}</span>
                <span style="text-align: right;">{currency} {item.get('price', 0):.2f}</span>
                <span style="text-align: right;">{currency} {item.get('total', 0):.2f}</span>
            </div>
        """
    
    subtotal = receipt_data.get('subtotal', 0)
    discount = receipt_data.get('discount', 0)
    discount_amount = receipt_data.get('discount_amount', 0)
    tax = receipt_data.get('tax', 0)
    tax_amount = receipt_data.get('tax_amount', 0)
    grand_total = receipt_data.get('grand_total', 0)
    amount_paid = receipt_data.get('amount_paid', grand_total)
    change_returned = amount_paid - grand_total if amount_paid > grand_total else 0
    
    html_content += f"""
        </div>
        
        <div style="margin-top: 10px;">
            <div style="display: flex; justify-content: space-between; padding: 4px 0;">
                <span>Subtotal</span>
                <span>{currency} {subtotal:.2f}</span>
            </div>
    """
    
    if discount > 0:
        html_content += f"""
            <div style="display: flex; justify-content: space-between; padding: 4px 0; color: #d93025;">
                <span style="color:#d93025;">Discount ({discount}%)</span>
                <span style="color:#d93025;">-{currency} {discount_amount:.2f}</span>
            </div>
        """
    
    if tax > 0:
        html_content += f"""
            <div style="display: flex; justify-content: space-between; padding: 4px 0; color: #0f9d58;">
                <span style="color:#0f9d58;">Tax ({tax}%)</span>
                <span style="color:#0f9d58;">+{currency} {tax_amount:.2f}</span>
            </div>
        """
    
    html_content += f"""
            <div style="display: flex; justify-content: space-between; padding: 8px 0; font-weight: 700; font-size: 1.2rem; border-top: 2px solid #1a73e8; color: #1a73e8;">
                <span>Grand Total</span>
                <span>{currency} {grand_total:.2f}</span>
            </div>
            <div style="display: flex; justify-content: space-between; padding: 4px 0;">
                <span>Amount Paid</span>
                <span>{currency} {amount_paid:.2f}</span>
            </div>
    """
    
    if change_returned > 0:
        html_content += f"""
            <div style="display: flex; justify-content: space-between; padding: 4px 0; color: #0f9d58;">
                <span style="color:#0f9d58;">Change Returned</span>
                <span style="color:#0f9d58;">{currency} {change_returned:.2f}</span>
            </div>
        """
    
    html_content += f"""
        </div>
        
        <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #ccc; text-align: center;">
            <strong>Payment Method</strong><br>
            {receipt_data.get('payment_method', 'N/A')}
        </div>
        
        <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #ccc; text-align: center; color: #1a73e8; font-weight: 700;">
            Thank you for shopping with us!<br>
            <span style="color: #666; font-weight: 400;">Please visit again.</span>
        </div>
    """
    
    qr_img = generate_qr(receipt_data.get('receipt_number', 'N/A'))
    if qr_img:
        html_content += f"""
        <div style="text-align: center; margin-top: 10px;">
            <img src="data:image/png;base64,{qr_img}" style="width:100px;height:100px;">
        </div>
        """
    
    html_content += f"""
        <div style="text-align: center; margin-top: 5px; color: #999; font-size: 10px;">
            {receipt_data.get('receipt_number', 'N/A')}
        </div>
    </div>
    </div>
    """
    
    st.html(html_content)

# ==================== CREATE NEW RECEIPT ====================

def create_new_receipt():
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.markdown("### 📝 Create New Receipt")
    
    keep_cart = st.checkbox("Keep items in cart after saving", value=st.session_state.get('keep_cart_after_save', False))
    st.session_state.keep_cart_after_save = keep_cart
    
    st.markdown("#### 👤 Customer Information")
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        customer_name = st.text_input("Customer Name", placeholder="Enter customer name", key="cust_name")
    with col_c2:
        customer_contact = st.text_input("Phone", placeholder="Enter phone number", key="cust_phone")
    with col_c3:
        customer_email = st.text_input("Email", placeholder="Enter email", key="cust_email")
    
    customer_address = st.text_area("Address", placeholder="Enter address", key="cust_address", height=50)
    
    if st.session_state.customers_db:
        with st.expander("💡 Quick Customer Select"):
            quick_customer = st.selectbox("Select saved customer", ["Select..."] + [c['name'] for c in st.session_state.customers_db])
            if quick_customer != "Select...":
                customer = next((c for c in st.session_state.customers_db if c['name'] == quick_customer), None)
                if customer:
                    st.info(f"📞 {customer.get('phone', 'N/A')} | ✉️ {customer.get('email', 'N/A')}")
    
    st.divider()
    
    st.markdown("#### 🛒 Products")
    
    selected_product = None
    
    col_p1, col_p2, col_p3, col_p4 = st.columns([2.5, 1.2, 1, 1.2])
    with col_p1:
        if st.session_state.products_db:
            product_options = ["Select product..."] + [p['name'] for p in st.session_state.products_db]
            selected_product = st.selectbox("Select from saved products", product_options, key="product_select")
        else:
            st.info("No products available. Add products in Product Management.")
            selected_product = None
    
    with col_p2:
        qty = st.number_input("Quantity", min_value=1, value=1, key="product_qty")
    
    with col_p3:
        if selected_product and selected_product != "Select product..." and st.session_state.products_db:
            product = next((p for p in st.session_state.products_db if p['name'] == selected_product), None)
            if product:
                st.write(f"Price: **{CONFIG['currency_symbol']} {product['price']:.2f}**")
    
    with col_p4:
        st.write("")
        st.write("")
        if st.button("➕ Add to Cart", use_container_width=True, key="add_to_cart_btn"):
            if selected_product and selected_product != "Select product..." and st.session_state.products_db:
                product = next((p for p in st.session_state.products_db if p['name'] == selected_product), None)
                if product:
                    st.session_state.product_items.append({
                        'name': product['name'],
                        'quantity': qty,
                        'price': product['price'],
                        'total': qty * product['price']
                    })
                    st.success(f"✅ Added {product['name']} to cart!")
                    st.rerun()
            else:
                st.warning("Please select a product first")
    
    with st.expander("➕ Add Custom Product"):
        col_add1, col_add2, col_add3, col_add4 = st.columns([2.5, 1, 1, 1.2])
        with col_add1:
            product_name = st.text_input("Product Name", placeholder="e.g., Laptop", key="custom_name")
        with col_add2:
            product_price = st.number_input("Price", min_value=0.0, value=0.0, step=1.0, format="%.2f", key="custom_price")
        with col_add3:
            product_qty = st.number_input("Qty", min_value=1, value=1, key="custom_qty")
        with col_add4:
            st.write("")
            st.write("")
            if st.button("➕ Add", use_container_width=True, key="add_custom_btn"):
                if product_name and product_price > 0:
                    st.session_state.product_items.append({
                        'name': product_name,
                        'quantity': product_qty,
                        'price': product_price,
                        'total': product_qty * product_price
                    })
                    st.success(f"✅ Added {product_name} to cart!")
                    st.rerun()
                else:
                    st.error("Please enter product name and price")
    
    if st.session_state.product_items:
        st.markdown("#### 📦 Current Items")
        items_df = pd.DataFrame(st.session_state.product_items)
        st.dataframe(
            items_df[['name', 'quantity', 'price', 'total']],
            use_container_width=True,
            hide_index=True,
            column_config={
                "name": "Item",
                "quantity": "Qty",
                "price": st.column_config.NumberColumn("Unit Price", format=f"{CONFIG['currency_symbol']} %.2f"),
                "total": st.column_config.NumberColumn("Total Price", format=f"{CONFIG['currency_symbol']} %.2f")
            }
        )
        
        col_clear1, col_clear2 = st.columns([1, 5])
        with col_clear1:
            if st.button("🗑️ Clear All", use_container_width=True, key="clear_cart"):
                st.session_state.product_items = []
                st.rerun()
    else:
        st.info("No items in cart. Add products above.")
    
    st.divider()
    
    st.markdown("#### 💰 Payment & Receipt Preview")
    
    col_pay1, col_pay2, col_pay3, col_pay4 = st.columns(4)
    with col_pay1:
        discount = st.number_input(
            "Discount (%)", 
            min_value=0.0, 
            max_value=100.0, 
            value=float(st.session_state.get('discount', CONFIG['discount_default'])), 
            step=1.0,
            key="discount_input"
        )
    with col_pay2:
        tax = st.number_input(
            "Tax (%)", 
            min_value=0.0, 
            max_value=50.0,
            value=float(st.session_state.get('tax', CONFIG['tax_default'])), 
            step=1.0,
            key="tax_input"
        )
    with col_pay3:
        amount_paid = st.number_input(
            "Amount Paid", 
            min_value=0.0,
            value=0.0,
            step=100.0,
            key="amount_paid_input"
        )
    with col_pay4:
        payment_method = st.selectbox("Payment Method", CONFIG['payment_methods'], key="payment_method")
    
    notes = st.text_area("📝 Notes", placeholder="Additional notes...", height=60, key="notes_input")
    
    st.divider()
    
    if st.session_state.product_items:
        subtotal, discount_amount, tax_amount, shipping_amount, grand_total = calculate_totals(
            st.session_state.product_items, discount, tax, 0
        )
        
        st.session_state.discount = discount
        st.session_state.tax = tax
        
        if amount_paid == 0:
            amount_paid = grand_total
        
        receipt_data = {
            'shop_name': CONFIG['company_name'],
            'shop_address': CONFIG['company_address'],
            'shop_phone': CONFIG['company_phone'],
            'shop_email': CONFIG['company_email'],
            'receipt_number': generate_receipt_number(),
            'date': datetime.datetime.now().strftime(CONFIG['date_format']),
            'time': datetime.datetime.now().strftime(CONFIG['time_format']),
            'customer_name': customer_name or "Walk-in Customer",
            'customer_contact': customer_contact or "N/A",
            'customer_email': customer_email or "N/A",
            'customer_address': customer_address or "N/A",
            'items': st.session_state.product_items.copy(),
            'subtotal': subtotal,
            'discount': discount,
            'discount_amount': discount_amount,
            'tax': tax,
            'tax_amount': tax_amount,
            'grand_total': grand_total,
            'amount_paid': amount_paid,
            'change_returned': amount_paid - grand_total if amount_paid > grand_total else 0,
            'payment_method': payment_method,
            'notes': notes
        }
        
        display_receipt_preview(receipt_data)
        
        st.divider()
        col_actions1, col_actions2, col_actions3 = st.columns(3)
        
        with col_actions1:
            if st.button("💾 Save Receipt", use_container_width=True, key="save_receipt_btn"):
                receipt_data['id'] = len(st.session_state.receipts) + 1
                st.session_state.receipts.append(receipt_data)
                
                if customer_name and customer_email:
                    existing_customer = next((c for c in st.session_state.customers_db if c['email'] == customer_email), None)
                    if existing_customer:
                        existing_customer['total_purchases'] += 1
                        existing_customer['total_spent'] += grand_total
                        existing_customer['last_purchase'] = receipt_data['date']
                    else:
                        st.session_state.customers_db.append({
                            'id': len(st.session_state.customers_db) + 1,
                            'name': customer_name,
                            'phone': customer_contact,
                            'email': customer_email,
                            'address': customer_address,
                            'total_purchases': 1,
                            'total_spent': grand_total,
                            'first_purchase': receipt_data['date'],
                            'last_purchase': receipt_data['date'],
                            'created_at': datetime.datetime.now().strftime(CONFIG['date_format'])
                        })
                
                if save_data():
                    st.success(f"✅ Receipt {receipt_data['receipt_number']} saved successfully!")
                    st.balloons()
                    
                    if not st.session_state.keep_cart_after_save:
                        st.session_state.product_items = []
                    
                    st.rerun()
                else:
                    st.error("❌ Failed to save receipt. Please try again.")
        
        with col_actions2:
            if st.button("📥 Download PDF", use_container_width=True, key="download_pdf_btn"):
                pdf_buffer = generate_pdf(receipt_data)
                if pdf_buffer:
                    b64 = base64.b64encode(pdf_buffer.getvalue()).decode()
                    # Direct download link - only one button
                    href = f'<a href="data:application/pdf;base64,{b64}" download="receipt_{receipt_data["receipt_number"]}.pdf" style="text-decoration:none;display:block;text-align:center;background:linear-gradient(135deg, #1a73e8, #0d47a1);color:white;padding:0.6rem;border-radius:12px;font-weight:600;">📥 Download PDF</a>'
                    st.markdown(href, unsafe_allow_html=True)
                else:
                    st.error("❌ Failed to generate PDF. Please try again.")
        
        with col_actions3:
            if st.button("🔄 Reset Cart", use_container_width=True, key="reset_receipt"):
                st.session_state.product_items = []
                st.rerun()
    else:
        st.info("Add products to see receipt preview")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== PRODUCT MANAGEMENT ====================

def manage_products():
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.markdown("### 📦 Product Management")
    
    with st.expander("➕ Add New Product", expanded=True):
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            new_name = st.text_input("Product Name", key="new_product_name", placeholder="Enter product name")
        with col2:
            new_price = st.number_input(f"Price ({CONFIG['currency_symbol']})", min_value=0.0, step=1.0, 
                                       format="%.2f", key="new_product_price")
        with col3:
            new_category = st.text_input("Category", key="new_product_category", placeholder="Optional")
        
        if st.button("➕ Add Product", use_container_width=True, key="add_product_btn"):
            if new_name and new_price > 0:
                product = {
                    'id': len(st.session_state.products_db) + 1,
                    'name': new_name,
                    'price': new_price,
                    'category': new_category or "Uncategorized",
                    'created_at': datetime.datetime.now().strftime(CONFIG['date_format'])
                }
                st.session_state.products_db.append(product)
                save_data()
                st.success(f"✅ Product '{new_name}' added successfully!")
                st.rerun()
            else:
                st.error("Please enter product name and price")
    
    st.divider()
    st.markdown("#### 📋 Product List")
    
    if st.session_state.products_db:
        for product in st.session_state.products_db:
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 0.8, 0.8])
                
                with col1:
                    st.markdown(f"**{product['name']}**")
                    st.caption(f"Category: {product.get('category', 'Uncategorized')}")
                
                with col2:
                    st.markdown(f"**{CONFIG['currency_symbol']} {product['price']:.2f}**")
                
                with col3:
                    st.markdown(f"ID: #{product['id']}")
                
                with col4:
                    if st.button("✏️ Edit", key=f"edit_{product['id']}", use_container_width=True):
                        st.session_state.editing_product_id = product['id']
                        st.rerun()
                
                with col5:
                    if st.button("🗑️", key=f"delete_{product['id']}", use_container_width=True):
                        st.session_state.products_db = [p for p in st.session_state.products_db if p['id'] != product['id']]
                        save_data()
                        st.success(f"✅ Product deleted!")
                        st.rerun()
                
                if st.session_state.editing_product_id == product['id']:
                    st.markdown("---")
                    st.markdown(f"**Editing: {product['name']}**")
                    col_e1, col_e2, col_e3, col_e4 = st.columns([2, 1, 1, 1])
                    with col_e1:
                        edit_name = st.text_input("Name", value=product['name'], key=f"edit_name_{product['id']}")
                    with col_e2:
                        edit_price = st.number_input("Price", min_value=0.0, value=product['price'], 
                                                    step=1.0, format="%.2f", key=f"edit_price_{product['id']}")
                    with col_e3:
                        edit_category = st.text_input("Category", value=product.get('category', ''), 
                                                     key=f"edit_cat_{product['id']}")
                    with col_e4:
                        st.write("")
                        st.write("")
                        if st.button("💾 Save", key=f"save_edit_{product['id']}", use_container_width=True):
                            for p in st.session_state.products_db:
                                if p['id'] == product['id']:
                                    p['name'] = edit_name
                                    p['price'] = edit_price
                                    p['category'] = edit_category
                                    break
                            save_data()
                            st.session_state.editing_product_id = None
                            st.success(f"✅ Product updated successfully!")
                            st.rerun()
                    
                    if st.button("❌ Cancel", key=f"cancel_edit_{product['id']}"):
                        st.session_state.editing_product_id = None
                        st.rerun()
                    
                    st.markdown("---")
                
                st.divider()
    else:
        st.info("No products in database. Add your first product above!")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== CUSTOMER MANAGEMENT ====================

def manage_customers():
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.markdown("### 👥 Customer Management")
    
    with st.expander("➕ Add New Customer", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            cust_name = st.text_input("Customer Name", key="cust_name_input", placeholder="Enter name")
            cust_phone = st.text_input("Phone", key="cust_phone_input", placeholder="Enter phone")
        with col2:
            cust_email = st.text_input("Email", key="cust_email_input", placeholder="Enter email")
            cust_address = st.text_area("Address", key="cust_address_input", placeholder="Enter address", height=60)
        
        if st.button("➕ Add Customer", use_container_width=True, key="add_customer_btn"):
            if cust_name and cust_email:
                if not any(c['email'] == cust_email for c in st.session_state.customers_db):
                    add_customer(cust_name, cust_phone, cust_email, cust_address)
                    st.success(f"✅ Customer '{cust_name}' added successfully!")
                    st.rerun()
                else:
                    st.error("Customer with this email already exists!")
            else:
                st.error("Please enter customer name and email")
    
    st.divider()
    st.markdown("#### 📋 Customer List")
    
    if st.session_state.customers_db:
        for customer in st.session_state.customers_db:
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([2, 1.5, 1, 0.8, 0.8])
                
                with col1:
                    st.markdown(f"**{customer['name']}**")
                    st.caption(f"📧 {customer.get('email', 'N/A')}")
                
                with col2:
                    st.markdown(f"📞 {customer.get('phone', 'N/A')}")
                    st.caption(f"📍 {customer.get('address', 'N/A')[:30]}...")
                
                with col3:
                    st.markdown(f"**Purchases:** {customer.get('total_purchases', 0)}")
                    st.caption(f"Spent: {CONFIG['currency_symbol']} {customer.get('total_spent', 0):.2f}")
                
                with col4:
                    if st.button("✏️ Edit", key=f"edit_cust_{customer['id']}", use_container_width=True):
                        st.session_state.editing_customer_id = customer['id']
                        st.rerun()
                
                with col5:
                    if st.button("🗑️", key=f"delete_cust_{customer['id']}", use_container_width=True):
                        delete_customer(customer['id'])
                        st.success(f"✅ Customer deleted!")
                        st.rerun()
                
                if st.session_state.editing_customer_id == customer['id']:
                    st.markdown("---")
                    st.markdown(f"**Editing: {customer['name']}**")
                    col_e1, col_e2 = st.columns(2)
                    with col_e1:
                        edit_name = st.text_input("Name", value=customer['name'], key=f"edit_cust_name_{customer['id']}")
                        edit_phone = st.text_input("Phone", value=customer.get('phone', ''), key=f"edit_cust_phone_{customer['id']}")
                    with col_e2:
                        edit_email = st.text_input("Email", value=customer['email'], key=f"edit_cust_email_{customer['id']}")
                        edit_address = st.text_area("Address", value=customer.get('address', ''), 
                                                   key=f"edit_cust_address_{customer['id']}", height=60)
                    
                    col_actions1, col_actions2 = st.columns(2)
                    with col_actions1:
                        if st.button("💾 Save", key=f"save_cust_edit_{customer['id']}", use_container_width=True):
                            update_customer(customer['id'], edit_name, edit_phone, edit_email, edit_address)
                            st.session_state.editing_customer_id = None
                            st.success(f"✅ Customer updated successfully!")
                            st.rerun()
                    
                    with col_actions2:
                        if st.button("❌ Cancel", key=f"cancel_cust_edit_{customer['id']}", use_container_width=True):
                            st.session_state.editing_customer_id = None
                            st.rerun()
                    
                    st.markdown("---")
                
                with st.expander(f"📄 View Receipts for {customer['name']}"):
                    customer_receipts = get_customer_receipts(customer['email'])
                    if customer_receipts:
                        for r in customer_receipts:
                            st.markdown(f"**{r['receipt_number']}** - {r['date']} - {CONFIG['currency_symbol']} {r['grand_total']:.2f}")
                    else:
                        st.info("No receipts found for this customer")
                
                st.divider()
    else:
        st.info("No customers in database. Add your first customer above!")
    
    if st.session_state.customers_db:
        st.divider()
        if st.button("📥 Export Customers (CSV)", use_container_width=True):
            df = pd.DataFrame(st.session_state.customers_db)
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="customers_export.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== RECEIPT HISTORY - FIXED DELETE ====================

def view_receipt_history():
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.markdown("### 📜 Receipt History")
    
    if st.session_state.receipts:
        search_term = st.text_input("🔍 Search Receipts", placeholder="Search by customer name or receipt number...")
        
        filtered_receipts = st.session_state.receipts
        if search_term:
            filtered_receipts = [
                r for r in filtered_receipts
                if search_term.lower() in r.get('customer_name', '').lower()
                or search_term.lower() in r.get('receipt_number', '').lower()
            ]
        
        if filtered_receipts:
            total = sum(r.get('grand_total', 0) for r in filtered_receipts)
            col_s1, col_s2, col_s3 = st.columns(3)
            with col_s1:
                st.metric("📊 Total Receipts", len(filtered_receipts))
            with col_s2:
                st.metric("💰 Total Revenue", f"{CONFIG['currency_symbol']} {total:,.2f}")
            with col_s3:
                avg = total / len(filtered_receipts) if filtered_receipts else 0
                st.metric("📈 Average Receipt", f"{CONFIG['currency_symbol']} {avg:,.2f}")
            
            st.divider()
            
            df = pd.DataFrame(filtered_receipts)
            display_df = df[['id', 'receipt_number', 'date', 'customer_name', 'grand_total', 'payment_method']]
            display_df.columns = ['ID', 'Receipt #', 'Date', 'Customer', 'Total', 'Payment']
            
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Total": st.column_config.NumberColumn("Total", format=f"{CONFIG['currency_symbol']} %.2f")
                }
            )
            
            selected_id = st.selectbox(
                "Select Receipt to View",
                options=[r['id'] for r in filtered_receipts],
                format_func=lambda x: f"Receipt #{x} - {next(r for r in filtered_receipts if r['id'] == x)['customer_name']}"
            )
            
            if selected_id:
                selected_receipt = next(r for r in filtered_receipts if r['id'] == selected_id)
                
                col_actions1, col_actions2, col_actions3 = st.columns(3)
                with col_actions1:
                    if st.button("👁️ View Receipt", use_container_width=True, key="view_receipt"):
                        st.session_state.editing_receipt_id = selected_id
                        st.rerun()
                
                with col_actions2:
                    pdf_buffer = generate_pdf(selected_receipt)
                    if pdf_buffer:
                        b64 = base64.b64encode(pdf_buffer.getvalue()).decode()
                        href = f'<a href="data:application/pdf;base64,{b64}" download="receipt_{selected_receipt["receipt_number"]}.pdf" style="text-decoration:none;display:block;text-align:center;background:linear-gradient(135deg, #1a73e8, #0d47a1);color:white;padding:0.5rem;border-radius:8px;font-weight:600;">📥 Download PDF</a>'
                        st.markdown(href, unsafe_allow_html=True)
                    else:
                        st.error("PDF generation failed")
                
                with col_actions3:
                    # Fixed Delete Button - Using a proper delete flow
                    delete_key = f"delete_receipt_{selected_id}"
                    if st.button("🗑️ Delete", use_container_width=True, key=delete_key):
                        # Delete the receipt directly without checkbox confusion
                        st.session_state.receipts = [r for r in st.session_state.receipts if r['id'] != selected_id]
                        save_data()
                        st.success(f"✅ Receipt #{selected_id} deleted successfully!")
                        st.rerun()
                
                if st.session_state.editing_receipt_id == selected_id:
                    st.markdown("---")
                    st.markdown("#### 📄 Receipt Details")
                    display_receipt_preview(selected_receipt)
                    
                    if st.button("Close Preview", use_container_width=True):
                        st.session_state.editing_receipt_id = None
                        st.rerun()
        else:
            st.info("No receipts found matching your search")
    else:
        st.info("No receipts saved yet")
    
    if st.session_state.receipts:
        st.divider()
        if st.button("🗑️ Clear All Receipts", use_container_width=True, type="secondary"):
            if st.checkbox("⚠️ Are you sure? This action cannot be undone."):
                st.session_state.receipts = []
                save_data()
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== MAIN APP ====================

def main():
    init_session_state()
    st.markdown(get_custom_css(), unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="main-header">
        <h1>🧾 {CONFIG['app_name']}</h1>
        <p>Professional Receipt Management System</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        
        dark_mode = st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)
        if dark_mode != st.session_state.dark_mode:
            st.session_state.dark_mode = dark_mode
            st.rerun()
        
        st.divider()
        
        st.markdown("### 📋 Navigation")
        page = st.radio("Select Page", 
                       ["New Receipt", "Product Management", "Customer Management", "Receipt History"],
                       label_visibility="collapsed")
        
        st.divider()
        
        st.markdown("### 📊 Statistics")
        total_receipts = len(st.session_state.receipts)
        total_products = len(st.session_state.products_db)
        total_customers = len(st.session_state.customers_db)
        total_revenue = sum(r.get('grand_total', 0) for r in st.session_state.receipts)
        
        st.metric("📄 Total Receipts", total_receipts)
        st.metric("📦 Total Products", total_products)
        st.metric("👥 Total Customers", total_customers)
        st.metric("💰 Total Revenue", f"{CONFIG['currency_symbol']} {total_revenue:,.2f}")
    
    if page == "New Receipt":
        create_new_receipt()
    elif page == "Product Management":
        manage_products()
    elif page == "Customer Management":
        manage_customers()
    elif page == "Receipt History":
        view_receipt_history()

if __name__ == "__main__":
    main()
