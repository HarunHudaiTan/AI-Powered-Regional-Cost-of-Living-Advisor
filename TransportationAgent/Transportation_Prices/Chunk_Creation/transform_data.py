def transform_data(input_string):
  """Transforms the input string into a more structured format."""

  parts = input_string.split('|')
  city_code = parts[1].strip() if len(parts) > 1 else None
  city_name = parts[2].strip() if len(parts) > 2 else None

  output_string = f"City Code: {city_code} | City: {city_name} | "

  transportation_modes = []
  i = 3
  while i < len(parts) - 1:
    transportation_type = parts[i].strip()
    fare_info = parts[i + 1].strip()

    if transportation_type and fare_info:
      transportation_modes.append(
        f"Transportation: {transportation_type} | Price: {fare_info}"
      )
    i += 2

  output_string += ' || '.join(transportation_modes)

  return output_string