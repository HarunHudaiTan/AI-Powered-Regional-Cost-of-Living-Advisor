import fitz 
from fpdf import FPDF
import os
from proj_llm_agent import LLM_Agent
from proj_image_summarizer import Image_Summarizer

class PDF_Processor:
    def __init__(self):
        self.agent = Image_Summarizer(
            name="PDF Processor",
            role="""
            You are an AI assistant that helps summarise given Image inputs into text summary. 
            You must focus on important aspects such as numerical data in graphs and what values they relate to.
            Your task is to describe the image in a text format that's usable as a reference for concrete proof. 
            Your output should also include some basic insights about the data in the image.
            """,
            temperature=0.95
        )

    def process_pdf(self, input_pdf_path, temp_image_dir='temp_images'):
        # Create output filename automatically
        base_name = os.path.splitext(os.path.basename(input_pdf_path))[0]
        output_pdf_path = f"{base_name}_processed.pdf"

        os.makedirs(temp_image_dir, exist_ok=True)
        doc = fitz.open(input_pdf_path)
        processed_text = []

        for i, page in enumerate(doc):
            text = page.get_text()
            processed_text.append(text)

            images = page.get_images(full=True)
            for img_index, img in enumerate(images):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                image_filename = f"{temp_image_dir}/page_{i}_img_{img_index}.{image_ext}"

                with open(image_filename, "wb") as img_file:
                    img_file.write(image_bytes)

                summary = self.agent.summarise_image(image_filename).text
                processed_text.append(f"\n[Image Summary]: {summary}\n")

        doc.close()

        # Write to new PDF
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.add_font('ArialUnicode', '', 'arial_unicode.ttf', uni=True)
        pdf.set_font('ArialUnicode', '', 12)

        for block in processed_text:
            pdf.multi_cell(0, 10, block)

        pdf.output(output_pdf_path)

        print(f"Processed PDF saved to: {output_pdf_path}")

        # Clean up: Delete the temporary image files
        for filename in os.listdir(temp_image_dir):
            file_path = os.path.join(temp_image_dir, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)

        # Optionally, delete the temporary image directory if it's empty
        if not os.listdir(temp_image_dir):  # Check if directory is empty
            os.rmdir(temp_image_dir)

        return output_pdf_path
        