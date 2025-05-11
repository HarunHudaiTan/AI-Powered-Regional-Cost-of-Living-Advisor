from proj_llm_agent import LLM_Agent

class Image_Summarizer(LLM_Agent):

    def summarise_image(self, image_path):

        file = self.client.files.upload(file = image_path)

        summary = self.generate_response([file])
        
        return summary