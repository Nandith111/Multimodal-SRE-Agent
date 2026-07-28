import markdown
from xhtml2pdf import pisa
import os

markdown_path = r"d:\SRE Agent\Updated_Approach_Document.md"
pdf_path = r"d:\SRE Agent\Updated_Approach_Document_v4.pdf"

with open(markdown_path, 'r', encoding='utf-8') as f:
    text = f.read()

html = markdown.markdown(text, extensions=['tables'])

html_content = f"<html><head><style>body {{ font-family: Helvetica, sans-serif; }} table, th, td {{ border: 1px solid black; border-collapse: collapse; padding: 5px; }}</style></head><body>{html}</body></html>"

with open(pdf_path, "w+b") as result_file:
    pisa_status = pisa.CreatePDF(html_content, dest=result_file)

if pisa_status.err:
    print("Error generating PDF")
else:
    print("PDF generated successfully at", pdf_path)
