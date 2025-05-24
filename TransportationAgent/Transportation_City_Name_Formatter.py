def format_city_name(city_name):
    """Convert Turkish city names to lowercase and remove Turkish-specific characters."""
    replacements = str.maketrans({
        'Ç': 'C', 'ç': 'c',
        'Ğ': 'G', 'ğ': 'g',
        'İ': 'I', 'ı': 'i',
        'Ö': 'O', 'ö': 'o',
        'Ş': 'S', 'ş': 's',
        'Ü': 'U', 'ü': 'u'
    })
    return city_name.translate(replacements).lower()