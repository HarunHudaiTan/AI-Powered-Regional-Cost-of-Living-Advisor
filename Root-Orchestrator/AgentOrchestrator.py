from EducationAgent.Rag.EducationAgent import EducationAgent
from MarketAgent.proj_market_pipeline_agent import LLM_Market_Pipeline
from Real_Estate_Agent.RealEstateAgent import RealEstateAgent
from TransportationAgent.Transportation_Prices.Public_Transport_Prices_Agent import Public_Transport_Prices_Agent

market_agent=LLM_Market_Pipeline()
fuel_price_agent=Public_Transport_Prices_Agent()
real_estate_agent=RealEstateAgent()
education_agent=EducationAgent()
def orchestrator_response(response):

    if response['response_continue'] =='STOP' :
        if response["action"]["action_number"] == 1:
           return real_estate_agent.search_real_estate(response['user_intent_turkish'],response["action"]['city_name'])
        elif response["action"]["action_number"] == 2:
           return market_agent.run_market_pipeline(response['user_intent_turkish'])
        elif response["action"]["action_number"] == 3:
          return education_agent.generate_education_agent_response(response['user_intent_turkish'])
        elif response["action"]["action_number"] == 4:
            return fuel_price_agent.generate_transport_price_response(response["action"]['city_name'])


# orchestrator_response(response1)
