from fpdf import FPDF
import datetime

class FinanceReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Financeify Pro: Monthly Financial Audit', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf_report(username, df, total_spent, top_cat):
    pdf = FinanceReport()
    pdf.add_page()
    
    # --- Summary Section ---
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"Report for: {username}", 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 10, f"Generated on: {datetime.date.today()}", 0, 1)
    pdf.ln(5)

    # Metrics Box
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 10, "Executive Summary", 1, 1, 'L', fill=True)
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 10, f"Total Expenses: Rs. {total_spent:,.2f}", 1, 1)
    pdf.cell(0, 10, f"Top Category: {top_cat}", 1, 1)
    pdf.ln(10)

    # --- Transaction Table ---
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 10, "Detailed Transaction History", 0, 1)
    
    # Table Header
    pdf.set_fill_color(46, 123, 207)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(80, 10, "Description", 1, 0, 'C', fill=True)
    pdf.cell(40, 10, "Category", 1, 0, 'C', fill=True)
    pdf.cell(40, 10, "Amount", 1, 1, 'C', fill=True)
    
    # Table Rows
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 9)
    for _, row in df.iterrows():
        pdf.cell(80, 8, str(row['Description']), 1)
        pdf.cell(40, 8, str(row['Category']), 1)
        pdf.cell(40, 8, f"{row['Amount']:,.2f}", 1, 1)

    return bytes(pdf.output())