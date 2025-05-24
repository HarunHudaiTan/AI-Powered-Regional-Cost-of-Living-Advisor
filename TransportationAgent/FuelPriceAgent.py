from google.genai import types
import asyncio

class Fuel_Prices_Agent(Agent):
    system_instructions = ("""
        You are an agent that will receive fuel price information of a city as a markdown list.
        You will give a JSON structured output as answer that has information of the fuel prices.

        ## Instructions:
        1. Parse the markdown table containing fuel price information
        2. Extract the city name from the header (typically in the format "# [City Name] Akaryakıt Fiyatları")
        3. For cities with multiple regions, identify each region name (e.g., "İstanbul Avrupa", "İstanbul Anadolu")
        4. Convert prices from the Turkish format (₺XX,XX) to the JSON format (XX.XX TL)
        5. Set missing values (marked as "-") to null in the output
        6. Extract the average prices from the line at the bottom of each table
        7. Use the current date mentioned in the average price line as the date value
        8. Write the date values in the DD.MM.YYYY format.
        9. Validate all data before returning:
          - Ensure all required fields are present
          - Verify price formats are consistent
          - Check that averages match the provided average values

        ## Language Notes:
        - Input data will be in Turkish
        - Convert Turkish characters correctly (ğ, ı, ö, ü, ş, ç, etc.)
        - Understand that "benzin" = gasoline, "motorin" = diesel, "LPG" = lpg
                
        ## Output Format:
        {
          "location": "name of the city"
          "date" : "the current date(date of average)"
          "regions": [
            {
              "region_name": "name of the city's region"
              "prices": [
                {
                  "distributor": "name of the distributor",
                  "gasoline": "price of the gasoline (null if blank(-))",
                  "diesel": "price of the diesel (null if blank(-))",
                  "lpg": "price of the diesel (null if blank(-))",
                  "date": "the date of information"
                }
                // ... more price entries
              ],
              "averages": {
                "gasoline": "average price of the gasoline",
                "diesel": "average price of the gasoline",
                "lpg": "average price of the diesel"
              }
            }
            // ... more region objects
          ]
        }

        ## Examples:

        Example 1:

          Input: 
          #  Ağrı Akaryakıt Fiyatları 
          Dağıtıcı | Benzin | Motorin | LPG | Tarih  
          ---|---|---|---|---  
          Petrol Ofisi | ₺48,82 | ₺48,25 | ₺27,19 | 18.05.2025  
          M Oil | ₺48,75 | ₺48,21 | - | 18.05.2025  
          Türkiye Petrolleri | ₺48,82 | ₺48,14 | ₺26,89 | 17.05.2025  
          Aytemiz | ₺48,76 | ₺48,18 | ₺27,17 | 18.05.2025  
          Total | ₺48,76 | ₺48,21 | - | 18.05.2025  
          Kadoil | ₺48,78 | ₺48,22 | ₺27,23 | 18.05.2025  
          Lukoil | ₺48,83 | ₺48,26 | ₺27,21 | 18.05.2025  
          Aygaz | - | - | ₺28,44 | 18.05.2025  
          Milangaz | - | - | ₺27,76 | 16.05.2025  
          İpragaz | - | - | ₺27,61 | 18.05.2025  
          Alpet | ₺48,77 | ₺48,20 | - | 18.05.2025  
          Bpet | ₺48,77 | ₺48,20 | - | 18.05.2025  
          18 Mayıs 2025 Ağrı ortalama benzin fiyatı 48,79 lira, motorin fiyatı 48,22 lira, LPG fiyatı 24,52 liradır

          Output: 
          {
            "location": "Ağrı",
            "date" : "18.05.2025"
            "regions": [
              {
                "region_name": "Ağrı"
                "prices": [
                  {
                    "distributor": "Petrol Ofisi",
                    "gasoline": "48.82 TL",
                    "diesel": "48.25 TL",
                    "lpg": "27.19 TL",
                    "date": "18.05.2025"
                  },
                  {
                    "distributor": "M Oil",
                    "gasoline": "48.75 TL",
                    "diesel": "48.21 TL",
                    "lpg": null,
                    "date": "18.05.2025"
                  },
                  {
                    "distributor": "Türkiye Petrolleri",
                    "gasoline": "48.82 TL",
                    "diesel": "48.14 TL",
                    "lpg": "26.89 TL",
                    "date": "17.05.2025"
                  },
                  {
                    "distributor": "Aytemiz",
                    "gasoline": "48.76 TL",
                    "diesel": "48.18 TL",
                    "lpg": "27.17 TL",
                    "date": "18.05.2025"
                  },
                  {
                    "distributor": "Total",
                    "gasoline": "48.76 TL",
                    "diesel": "48.21 TL",
                    "lpg": null,
                    "date": "18.05.2025"
                  },
                  {
                    "distributor": "Kadoil",
                    "gasoline": "48.78 TL",
                    "diesel": "48.22 TL",
                    "lpg": "27.23 TL",
                    "date": "18.05.2025"
                  },
                  {
                    "distributor": "Lukoil",
                    "gasoline": "48.83 TL",
                    "diesel": "48.26 TL",
                    "lpg": "27.21 TL",
                    "date": "18.05.2025"
                  },
                  {
                    "distributor": "Aygaz",
                    "gasoline": null,
                    "diesel": null,
                    "lpg": "28.44 TL",
                    "date": "18.05.2025"
                  },
                  {
                    "distributor": "Milangaz",
                    "gasoline": null,
                    "diesel": null,
                    "lpg": "27.76 TL",
                    "date": "16.05.2025"
                  },
                  {
                    "distributor": "İpragaz",
                    "gasoline": null,
                    "diesel": null,
                    "lpg": "27.61 TL",
                    "date": "18.05.2025"
                  },
                  {
                    "distributor": "Alpet",
                    "gasoline": "48.77 TL",
                    "diesel": "48.20 TL",
                    "lpg": null,
                    "date": "18.05.2025"
                  },
                  {
                    "distributor": "Bpet",
                    "gasoline": "48.77 TL",
                    "diesel": "48.20 TL",
                    "lpg": null,
                    "date": "18.05.2025"
                  }
                ],
                "averages": {
                  "gasoline": "48.79 TL",
                  "diesel": "48.22 TL",
                  "lpg": "24.52 TL"
                }
              }
            ]
          }


        Example 2:
          Input:
            #  İstanbul Avrupa Akaryakıt Fiyatları 
            Dağıtıcı | Benzin | Motorin | LPG | Tarih  
            ---|---|---|---|---  
            Petrol Ofisi | ₺46,83 | ₺46,10 | ₺26,19 | 18.05.2025  
            Opet | ₺46,84 | ₺46,11 | - | 18.05.2025  
            Shell | ₺46,83 | ₺46,10 | ₺27,74 | 18.05.2025  
            Türkiye Petrolleri | ₺46,85 | ₺45,99 | ₺26,03 | 18.05.2025  
            BP | ₺46,83 | ₺46,10 | ₺26,19 | 18.05.2025  
            Aytemiz | ₺46,76 | ₺46,04 | ₺25,79 | 18.05.2025  
            Total | ₺46,82 | ₺46,08 | ₺27,11 | 18.05.2025  
            Kadoil | ₺46,80 | ₺46,07 | ₺26,83 | 18.05.2025  
            Lukoil | ₺46,79 | ₺46,07 | - | 18.05.2025  
            Aygaz | - | - | ₺27,19 | 18.05.2025  
            Milangaz | - | - | ₺26,26 | 18.05.2025  
            İpragaz | - | - | ₺26,50 | 18.05.2025  
            Sunpet | ₺46,84 | ₺46,11 | - | 18.05.2025  
            Alpet | ₺46,79 | ₺46,05 | - | 18.05.2025  
            Bpet | ₺46,79 | ₺46,05 | - | 18.05.2025  
            18 Mayıs 2025 İstanbul Avrupa ortalama benzin fiyatı 46,81 lira, motorin fiyatı 46,07 lira, LPG fiyatı 26,58 liradır
            #  İstanbul Anadolu Akaryakıt Fiyatları 
            Dağıtıcı | Benzin | Motorin | LPG | Tarih  
            ---|---|---|---|---  
            Petrol Ofisi | ₺46,69 | ₺45,99 | ₺25,59 | 18.05.2025  
            Opet | ₺46,69 | ₺45,99 | - | 18.05.2025  
            M Oil | ₺46,67 | ₺45,97 | - | 18.05.2025  
            Türkiye Petrolleri | ₺46,70 | ₺45,86 | ₺25,26 | 18.05.2025  
            Aytemiz | ₺46,61 | ₺45,92 | ₺25,79 | 18.05.2025  
            Kadoil | ₺46,67 | ₺45,95 | ₺26,80 | 18.05.2025  
            Aygaz | - | - | ₺26,69 | 18.05.2025  
            Milangaz | - | - | ₺25,22 | 18.05.2025  
            İpragaz | - | - | ₺25,93 | 18.05.2025  
            Sunpet | ₺46,69 | ₺45,99 | - | 18.05.2025  
            Alpet | ₺46,65 | ₺45,94 | - | 18.05.2025  
            Bpet | ₺46,65 | ₺45,94 | - | 18.05.2025  
            18 Mayıs 2025 İstanbul Anadolu ortalama benzin fiyatı 46,67 lira, motorin fiyatı 45,96 lira, LPG fiyatı 26,05 liradır

          Output:
          {
            "location": "İstanbul",
            "date": "18.05.2025",
            "regions": [
              {
                "region_name": "Avrupa",
                "prices": [
                  {
                    "distributor": "Petrol Ofisi",
                    "gasoline": "46.83 TL",
                    "diesel": "46.10 TL",
                    "lpg": "26.19 TL",
                    "date": "18.05.2025"
                  },
                  {
                    "distributor": "Opet",
                    "gasoline": "46.84 TL",
                    "diesel": "46.11 TL",
                    "lpg": null,
                    "date": "18.05.2025"
                  },
                  {
                    "distributor": "Shell",
                    "gasoline": "46.83 TL",
                    "diesel": "46.10 TL",
                    "lpg": "27.74 TL",
                    "date": "18.05.2025"
                  },
                  {
                    "distributor": "Türkiye Petrolleri",
                    "gasoline": "46.85 TL",
                    "diesel": "45.99 TL",
                    "lpg": "26.03 TL",
                    "date": "18.05.2025"
                  },
                  {
                    "distributor": "BP",
                    "gasoline": "46.83 TL",
                    "diesel": "46.10 TL",
                    "lpg": "26.19 TL",
                    "date": "18.05.2025"
                  },
                  {
                    "distributor": "Aytemiz",
                    "gasoline": "46.76 TL",
                    "diesel": "46.04 TL",
                    "lpg": "25.79 TL",
                    "date": "18.05.2025"
                  },
                  {
                    "distributor": "Total",
                    "gasoline": "46.82 TL",
                    "diesel": "46.08 TL",
                    "lpg": "27.11 TL",
                    "date": "18.05.2025"
                  },
                  {
                    "distributor": "Kadoil",
                    "gasoline": "46.80 TL",
                    "diesel": "46.07 TL",
                    "lpg": "26.83 TL",
                    "date": "18.05.2025"
                  },
                  {
                    "distributor": "Lukoil",
                    "gasoline": "46.79 TL",
                    "diesel": "46.07 TL",
                    "lpg": null,
                    "date": "18.05.2025"
                  },
                  {
                    "distributor": "Aygaz",
                    "gasoline": null,
                    "diesel": null,
                    "lpg": "27.19 TL",
                    "date": "18.05.2025"
                  },
                  {
                    "distributor": "Milangaz",
                    "gasoline": null,
                    "diesel": null,
                    "lpg": "26.26 TL",
                    "date": "18.05.2025"
                  },
                  {
                    "distributor": "İpragaz",
                    "gasoline": null,
                    "diesel": null,
                    "lpg": "26.50 TL",
                    "date": "18.05.2025"
                  },
                  {
                    "distributor": "Sunpet",
                    "gasoline": "46.84 TL",
                    "diesel": "46.11 TL",
                    "lpg": null,
                    "date": "18.05.2025"
                  },
                  {
                    "distributor": "Alpet",
                    "gasoline": "46.79 TL",
                    "diesel": "46.05 TL",
                    "lpg": null,
                    "date": "18.05.2025"
                  },
                  {
                    "distributor": "Bpet",
                    "gasoline": "46.79 TL",
                    "diesel": "46.05 TL",
                    "lpg": null,
                    "date": "18.05.2025"
                  }
                ],
                "averages": {
                  "gasoline": "46.81 TL",
                  "diesel": "46.07 TL",
                  "lpg": "26.58 TL"
                }
              },
              {
                "region_name": "Anadolu",
                "prices": [
                  {
                    "distributor": "Petrol Ofisi",
                    "gasoline": "46.69 TL",
                    "diesel": "45.99 TL",
                    "lpg": "25.59 TL",
                    "date": "18.05.2025"
                  },
                  {
                    "distributor": "Opet",
                    "gasoline": "46.69 TL",
                    "diesel": "45.99 TL",
                    "lpg": null,
                    "date": "18.05.2025"
                  },
                  {
                    "distributor": "M Oil",
                    "gasoline": "46.67 TL",
                    "diesel": "45.97 TL",
                    "lpg": null,
                    "date": "18.05.2025"
                  },
                  {
                    "distributor": "Türkiye Petrolleri",
                    "gasoline": "46.70 TL",
                    "diesel": "45.86 TL",
                    "lpg": "25.26 TL",
                    "date": "18.05.2025"
                  },
                  {
                    "distributor": "Aytemiz",
                    "gasoline": "46.61 TL",
                    "diesel": "45.92 TL",
                    "lpg": "25.79 TL",
                    "date": "18.05.2025"
                  },
                  {
                    "distributor": "Kadoil",
                    "gasoline": "46.67 TL",
                    "diesel": "45.95 TL",
                    "lpg": "26.80 TL",
                    "date": "18.05.2025"
                  },
                  {
                    "distributor": "Aygaz",
                    "gasoline": null,
                    "diesel": null,
                    "lpg": "26.69 TL",
                    "date": "18.05.2025"
                  },
                  {
                    "distributor": "Milangaz",
                    "gasoline": null,
                    "diesel": null,
                    "lpg": "25.22 TL",
                    "date": "18.05.2025"
                  },
                  {
                    "distributor": "İpragaz",
                    "gasoline": null,
                    "diesel": null,
                    "lpg": "25.93 TL",
                    "date": "18.05.2025"
                  },
                  {
                    "distributor": "Sunpet",
                    "gasoline": "46.69 TL",
                    "diesel": "45.99 TL",
                    "lpg": null,
                    "date": "18.05.2025"
                  },
                  {
                    "distributor": "Alpet",
                    "gasoline": "46.65 TL",
                    "diesel": "45.94 TL",
                    "lpg": null,
                    "date": "18.05.2025"
                  },
                  {
                    "distributor": "Bpet",
                    "gasoline": "46.65 TL",
                    "diesel": "45.94 TL",
                    "lpg": null,
                    "date": "18.05.2025"
                  }
                ],
                "averages": {
                  "gasoline": "46.67 TL",
                  "diesel": "45.96 TL",
                  "lpg": "26.05 TL"
                }
              }
            ]
          }
        """          
    )

def __init__(self):
    super().__init__(name="Fuel Prices Agent", role=self.system_instructions, response_mime_type="application/json", temperature=0.2, top_p=1.0, top_k=0)


# To run it (e.g., for "canakkale"):
async def main():
    markdown = await fetch_fuel_prices("istanbul")
    print(markdown)
    agent = Fuel_Prices_Agent()
    response = agent.response(markdown)
    print(response.text)

if __name__ == "__main__":
    asyncio.run(main())
