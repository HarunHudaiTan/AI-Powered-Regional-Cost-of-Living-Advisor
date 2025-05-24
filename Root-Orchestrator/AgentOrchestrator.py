
from EducationAgent.Rag import EducationAgent as EducationAgent
from MarketAgent.proj_market_pipeline_agent import LLM_Market_Pipeline
from Real_Estate_Agent import RealEstateAgent as RealEstateAgent
from TransportationAgent.Transportation_Prices import Public_Transport_Prices_Agent as TransportationAgent
from TransportationAgent import FuelPriceAgent as FuelPriceAgent
from RootLLM import root_llm_response, RootLLM

root_llm=RootLLM()
MarketAgent=LLM_Market_Pipeline()

def orchestrator_response(prompt,root_llm):
    response=root_llm.send_message(prompt)
    if response['response_continue'] =='STOP' :
        if response["action"]["action_number"] == 1:
            print(RealEstateAgent.real_estate_agent_response(response['natural_response']))
        elif response["action"]["action_number"] == 2:
           print( MarketAgent.run_market_pipeline(response['natural_response']))
        elif response["action"]["action_number"] == 3:
           print( EducationAgent.generate_response(response['natural_response']))
        elif response["action"]["action_number"] == 4:
          print(TransportationAgent.generate_response(response['city_name']))


while True:
    promt=input(
    )
    orchestrator_response(promt)