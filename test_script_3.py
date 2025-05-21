from proj_market_pipeline_agent import LLM_Market_Pipeline

if __name__ == "__main__":
    pipeline = LLM_Market_Pipeline()
    #writing the output as a json file
    response = pipeline.run_market_pipeline("I can leave about 10000 liras a month for groceries. I have a family of 5")
    print(response.text)
