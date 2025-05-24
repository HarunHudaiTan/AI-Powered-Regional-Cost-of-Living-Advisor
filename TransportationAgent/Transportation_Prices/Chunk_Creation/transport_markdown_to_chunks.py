from transport_data import transport_data

def transport_markdown_to_chunks(markdown_text: str):
  chunks = []
  lines = markdown_text.split('\n')
  for line in lines[2:]:
    formatted = transform_data(line)
    chunks.append(formatted)

  return chunks
