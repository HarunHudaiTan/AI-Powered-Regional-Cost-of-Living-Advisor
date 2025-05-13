from PyPDF2 import PdfReader



reader = PdfReader("example.pdf")

for i in range(0,len(reader.pages)) :
    page = reader.pages[i]
    text = page.extract_text()

    result = [x for x in text.split("\n") if "➜" in x]
    print(result)