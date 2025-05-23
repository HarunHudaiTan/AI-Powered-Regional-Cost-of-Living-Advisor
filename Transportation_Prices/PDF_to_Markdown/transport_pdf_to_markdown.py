from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions

def transport_pdf_to_markdown(pdf_name: str):
  pipeline_options = PdfPipelineOptions(do_table_structure=True)
  pipeline_options.table_structure_options.do_cell_matching = False

  converter = DocumentConverter(
    format_options={
      InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
  )

  convertion = converter.convert(pdf_name)

  return convertion.document.export_to_markdown()