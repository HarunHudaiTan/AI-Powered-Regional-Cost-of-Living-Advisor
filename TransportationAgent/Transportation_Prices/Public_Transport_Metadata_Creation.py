from TransportationAgent.Transportation_City_Name_Formatter import format_city_name


def extract_city_name(chunk):
    """Extract city name from chunk text"""
    try:
        # Split by | and find the City part
        parts = chunk.split('|')
        city_part = [part.strip() for part in parts if part.strip().startswith('City:')][0]
        city_name = city_part.split('City:')[1].strip()
        return format_city_name(city_name)
    except (IndexError, AttributeError):
        return None


def add_meta_data(chunks):
    ids = []
    metadatas = []

    for i, chunk in enumerate(chunks):

        ids.append(str(i+1))

        # Extract city name from chunk
        city_name = extract_city_name(chunk)

        # Determine document name based on chunk index
        if i < 40:  # chunks 1-40 (0-39 in 0-indexed)
            document = "toplu-taşıma_ücretleri_(1-40).pdf"
        else:  # chunks 41-81 (40-80 in 0-indexed)
            document = "toplu-taşıma_ücretleri_(41-81).pdf"

        metadata = {
            'document': document,
            'city': city_name,
        }
        metadatas.append(metadata)

    return ids, metadatas
