from proj_market_pipeline import LLM_Market_Pipeline

if __name__ == "__main__":
    pipeline = LLM_Market_Pipeline()
    #writing the output as a json file
    response = pipeline.run_market_pipeline("Chicken Wings")
    print(response)
