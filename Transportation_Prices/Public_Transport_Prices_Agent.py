from google.genai import types

class Public_Transport_Prices_Agent(Agent):
    system_instructions = ("""
        You are an agent that will receive public transportation price information of a city as a plain text string.
        You will give a JSON structured output as answer that has information of the transportation prices.

        ## Instructions:
        1. Parse the input string: The input will be a plain text string containing transportation price information for a city.

        2. Extract the city name:** Extract the city name from the input string, typically following the pattern "City: [City Name]".

        3. Process Transportation Types:** The input string will contain one or more transportation types, separated by "||". For each transportation type:
           - Extract the transportation type name (e.g., "Otobüsler", "Marmaray (ORTALAMA FİYATLAR)").
           - Extract the client types and their corresponding prices. The prices will be in the format "Type: Price TL" (e.g., "Tam: 27 TL").
           - Create a `clients` array containing objects with `"type"` and `"price"` keys for each client type.

        4. Maintain Price Format: The prices should be kept as strings, including the "TL" currency symbol (e.g., `"27 TL"`, `"13.18 TL"`). Do not convert to numbers.

        5. Missing Values: There are no missing values to handle. All client types for a given transportation type will have a price.

        6. No Averages or Dates: Do not extract or include any average prices or dates. This information is not present in the input format.

        7. Output JSON: Construct a JSON object with the following structure:


        ## Output Format:
	{
  	  "city": "name of the city",
  	  "transportation": [
    	    {
              "type": "the name or names of transportation types",
              "clients": [
	        {
                  "type": "the type of the client",
                  "price": "price of transportation for that client"
                }
                // ... more client entries
              ]
            }
            // ... more transportation objects
          ]
        }  


        ## Examples:

        Example 1:

          Input: 
          City Code: 34 | City: İSTANBUL | Transportation: Otobüsler, Metro, Tramvay, Teleferik | Price: Tam: 27 TL, Öğrenci: 13.18 TL, İndirimli: 19.33 TL ||
	  Transportation: Marmaray (ORTALAMA FİYATLAR) | Price: Tam: 43.63 TL, Öğrenci: 20.59 TL, İndirimli: 30.74 TL ||
	  Transportation: Metrobüs (ORTALAMA FİYATLAR) | Price: Tam: 31.53 TL, Öğrenci: 11.98 TL, İndirimli: 18.60 TL ||
	  Transportation: Vapur ve Deniz Motorları (ORTALAMA FİYATLAR) | Price: Tam: 44.42 TL, Öğrenci: 22.08 TL, İndirimli: 31.35 TL

          Output: 
          {
  	    "city": "İstanbul",
  	    "transportation": [
    	      {
                "type": "Otobüsler, Metro, Tramvay, Teleferik",
                "clients": [
	          {
                    "type": "Tam",
                    "price": "27 TL"
                  },
                  {
                    "type": "Öğrenci",
                    "price": "13.18 TL"
                  },
		  {
                    "type": "İndirimli",
                    "price": "19.33 TL"
                  },
                ]
              },
	      {
                "type": "Marmaray (ORTALAMA FİYATLAR)",
                "clients": [
	          {
                    "type": "Tam",
                    "price": "43.63 TL"
                  },
                  {
                    "type": "Öğrenci",
                    "price": "20.59 TL"
                  },
		  {
                    "type": "İndirimli",
                    "price": "30.74 TL"
                  },
                ]
              },
	      {
                "type": "Metrobüs (ORTALAMA FİYATLAR)",
                "clients": [
	          {
                    "type": "Tam",
                    "price": "31.53 TL"
                  },
                  {
                    "type": "Öğrenci",
                    "price": "11.98 TL"
                  },
		  {
                    "type": "İndirimli",
                    "price": "18.60 TL"
                  },
                ]
              },
	      {
                "type": "Vapur ve Deniz Motorları (ORTALAMA FİYATLAR)",
                "clients": [
	          {
                    "type": "Tam",
                    "price": "44.42 TL"
                  },
                  {
                    "type": "Öğrenci",
                    "price": "22.08 TL"
                  },
		  {
                    "type": "İndirimli",
                    "price": "31.35 TL"
                  },
                ]
              }
            ]
          }  


        Example 2:
        City Code: 54 | City: SAKARYA (ADAPAZARI) | Transportation: Otobüsler | Price: Tam: 13.50 TL, Öğrenci: 4,35 TL, 60 - 65 Yaş: 6.75 TL, Öğretmen: 11.48 TL || 
        Transportation: Minibüsler | Price: Tam: 19.50 TL, Öğrenci: 17.50 TL ||
        Transportation: Adaray | Price: Tam: 15 TL, Öğrenci: 4,83 TL, 60 - 65 Yaş: 7.50 TL, Öğretmen: 12,75 TL

          Output:
          {
            "city": "Sakarya (Adapazarı)",
  	    "transportation": [
              {
                "type": "Otobüsler",
      		"clients": [
        	  {
                    "type": "Tam",
          	    "price": "13.50 TL"
       		  },
                  {
                    "type": "Öğrenci",
                    "price": "4,35 TL"
                  },
                  {
                    "type": "60 - 65 Yaş",
                    "price": "6.75 TL"
                  },
                  {
                    "type": "Öğretmen",
                    "price": "11.48 TL"
                  }
                ]
              },
     	      {
                "type": "Minibüsler",
                "clients": [
                  {
                    "type": "Tam",
                    "price": "19.50 TL"
                  },
                  {
                    "type": "Öğrenci",
                    "price": "17.50 TL"
                  }
                ]
              },
              {
                "type": "Adaray",
                "clients": [
                  {
                    "type": "Tam",
                    "price": "15 TL"
                  },
                  {
                    "type": "Öğrenci",
                    "price": "4,83 TL"
                  },
                  {
                    "type": "60 - 65 Yaş",
                    "price": "7.50 TL"
                  },
                  {
                    "type": "Öğretmen",
                    "price": "12,75 TL"
                  }
                ]
              }
            ]
          }
        """          
    )

    config = types.GenerateContentConfig(system_instruction=system_instructions,)

    def __init__(self):
        super().__init__(self.config)


def main():
    agent = Public_Transport_Prices_Agent()
    response = agent.response("City Code: 41 | City: KOCAELİ (İZMİT) | Transportation: Otobüsler. Minibüsler | Price: Tam: 27 TL, İndirimli: 17.50 TL || Transportation: Tramvay | Price: Tam: 23 TL, İndirimli: 13.50 TL || Transportation: Deniz Ulaşımı | Price: Tam: 32 TL, İndirimli: 24 TL")
    print(response.text)

main()