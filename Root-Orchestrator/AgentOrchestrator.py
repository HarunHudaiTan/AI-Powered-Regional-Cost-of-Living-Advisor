from EducationAgent.Rag.EducationAgent import EducationAgent
from MarketAgent.proj_market_pipeline_agent import LLM_Market_Pipeline
from Real_Estate_Agent.RealEstateAgent import RealEstateAgent
from TransportationAgent.FuelPriceAgent import Fuel_Prices_Agent
from TransportationAgent.Transportation_Prices.Public_Transport_Prices_Agent import Public_Transport_Prices_Agent
from SummaryAgent import SummaryAgent
market_agent=LLM_Market_Pipeline()
fuel_price_agent=Fuel_Prices_Agent()
real_estate_agent=RealEstateAgent()
education_agent=EducationAgent()
transporation_agent=Public_Transport_Prices_Agent()
summary_agent=SummaryAgent()

def orchestrator_response(response):

    if response['response_continue'] =='STOP' :
        output=""
        if response["action"]["action_number"] == 1:
            output= real_estate_agent.search_real_estate(response['user_intent_turkish'],response["action"]['city_name'])
            return outout
        elif response["action"]["action_number"] == 2:
            output = market_agent.run_market_pipeline(response['user_intent_turkish'])
        elif response["action"]["action_number"] == 3:
            output = education_agent.generate_education_agent_response(response['user_intent_turkish'])
        elif response["action"]["action_number"] == 4:
            output = fuel_price_agent.generate_fuel_price(response["action"]['city_name'])
        elif response["action"]["action_number"] == 5:
            output = transporation_agent.generate_transport_price_response(response["action"]['city_name'])
        return summary_agent.generate_summary_agent_response(output,response["action"]["action_number"])

