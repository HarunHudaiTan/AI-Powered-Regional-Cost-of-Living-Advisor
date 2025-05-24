from EducationAgent.Rag.EducationAgent import EducationAgent
from MarketAgent.proj_market_pipeline_agent import LLM_Market_Pipeline
from Real_Estate_Agent.RealEstateAgent import RealEstateAgent
from TransportationAgent.FuelPriceAgent import Fuel_Prices_Agent

market_agent=LLM_Market_Pipeline()
fuel_price_agent=Fuel_Prices_Agent()
real_estate_agent=RealEstateAgent()
education_agent=EducationAgent()
response1={'natural_response': 'Ankara Keçiören.', 'response_continue': 'STOP', 'action': {'action_number': 1, 'action_confidence': 0.9, 'city_name': 'Ankara Keçiören'}}
def orchestrator_response(response):

    if response['response_continue'] =='STOP' :
        if response["action"]["action_number"] == 1:
            print(real_estate_agent.search_real_estate(response['natural_response']))
        elif response["action"]["action_number"] == 2:
           print( market_agent.run_market_pipeline(response['natural_response']))
        elif response["action"]["action_number"] == 3:
           print( education_agent.generate_education_agent_response(response['natural_response']))
        elif response["action"]["action_number"] == 4:
          print(fuel_price_agent.generate_fuel_price(response['city_name']))


orchestrator_response(response1)

