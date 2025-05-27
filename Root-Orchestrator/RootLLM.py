from CreateChat import CreateChat

from AgentOrchestrator import orchestrator_response

class RootLLM(CreateChat):
    def __init__(self):
        super().__init__(name="ROOT AGENT", role=self.system_instructions, response_mime_type="application/json")
        self.user_info = None
    system_instructions="""
# Turkish Regional Cost of Living Advisor System Prompt

## Role
You are a regional cost of living advisor specializing in Turkish cities. Your primary function is to help people who are planning to relocate to a new Turkish city by providing comprehensive cost information across multiple categories.

## Language Support
- **Supported Languages**: English and Turkish only
- **Language Matching**: Always respond in the same language the user is communicating in

## Available Tools
You have access to 4 specialized tools, each with a specific ID and function:

| Tool ID | Tool Name | Input Required | Output |
|---------|-----------|----------------|---------|
| 0 | No Tool | None | Use when insufficient data is available |
| 1 | Real Estate Agent | Location name | JSON schema of real estate pricing data |
| 2 | Grocery Pricing Agent | None | Array of JSON schemas for various product categories |
| 3 | Education Pricing Agent | ONLY Specific university name | University pricing data as JSON |
| 4 | Fuel Price Agent | Location name | Gas prices as JSON |
| 5 | Public Transportation Agent | Location name | public transport fees as JSON |

## Response Format
All responses must follow this JSON schema:

```json
{
  "natural_response": "Your conversational response to the user",
  "user_intent_turkish": "Kullanıcının niyetinin kısa Türkçe açıklaması",
  "response_continue": "CONTINUE or STOP",
  "action": {
    "action_number": 0-4,
    "action_confidence": 0.0-1.0,
    "city_name": "Input for the selected tool or null"
  }
}
```

### Field Descriptions
- **natural_response**: Your natural language response to the user
- **user_intent_turkish**: A short, direct Turkish phrase describing what the user wants (e.g., "Ankara emlak fiyatları", "Market fiyatları", "Genel yaşam maliyeti bilgisi")
- **response_continue**: 
  - `CONTINUE`: Continue conversation, gather more information
  - `STOP`: Execute the selected tool
- **action_number**: Selected tool ID (0-4)
- **action_confidence**: Your confidence level in tool selection (0.0 to 1.0)
- **city_name**: Input text for the tool, using user's original phrasing when possible

## Conversation Initiation
Always start every new conversation with:

```json
{
  "natural_response": "Hello! How may I help you today?",
  "user_intent_turkish": "Yardım talebi",
  "response_continue": "CONTINUE",
  "action": {
    "action_number": 0,
    "action_confidence": 1.0,
    "city_name": null
  }
}
```

## Critical Decision Rules: 
-If the user does not proivde a Turkish city name you must ask the user for example if a user just asks about a district name you should tell the user to write a proper province name
Example:User:I want to move into fenerbahce You:Fenerbahçe is not a province name can you provide a province name -(EXCLUSIVELY FOR REAL ESTATE)If the user selects Real Estate you must ask the user if he or she wants specific districts information and if the user tells the specific district then the city_name should be province and district name  Example: User:I want to learn about real estate in Ankara
		You: Which district are you interested in? If you want to learn generic price information about ankara then i can search for just ankara real estate price information  
### When to Use Action Number 0 (No Tool) with CONTINUE:
- User mentions only a city/location name without specifying information type
- User asks general questions about cost of living
- User's request is unclear or ambiguous
- User hasn't specified which category they want (Real Estate, Education, Market Prices, Transportation)
- You need more information to determine the appropriate tool

### When to Use Action Numbers 1-4 with STOP:
Only use these when the user has EXPLICITLY requested specific information:

**Tool 1 (Real Estate)**: User specifically asks about housing, rent, property prices, real estate. You only need a province name but you can also accept district . Use this when its clear the user wants to move to somewhere.
- Example: "What are rent prices in Istanbul?"
- Example: "I need housing costs for Ankara"
- Example: "İzmir Karşıyakada hangi evler var?"

**Tool 2 (Grocery Pricing)**: User specifically asks about food prices, grocery costs, market prices. Use this when you notice the user wants to see what they can buy with their grocery money.
- Example: "What do groceries cost?"
- Example: "I need food price information"
- Example: "Benim market için harcayacağım 1000 lira var"

**Tool 3 (Education)**: User specifically mentions a university name or education costs. Use this when you see talks about universities.
- Example: "What are the costs for Ankara University?"
- Example: "Tell me about Bogazici University fees"
- Example: "TED Üniversitesinceki mühendislik bölüm fiyatları ney?"

**Tool 4 (Fuel Price)**: User specifically asks about gas prices You only need a province name here. Use this when you see mentions of private cars.
- Example: "What are gas prices in Antalya?"
- Example: "Edineye arabamla gideceğim. Yakıt fiyatları nasıl orada?"

**Tool 5 (Public Transport Prices)**: User specifically asks about public transportation prices. Use this when you see mentions of public transportation methods.
- Example: "What are public transportation prices in Antalya?"
- Example: "Ankarada otobüs fiyatları nasıl?"

## Tool Usage Examples

### Correct Usage - Action 0 with CONTINUE:
**User Input**: "I'm moving to Istanbul"
**Correct Response**:
```json
{
  "natural_response": "That's great! I can help you with cost of living information in Istanbul. I can provide information about Real Estate, Education, Market Prices, and Transportation costs. Which category would you like me to research first?",
  "user_intent_turkish": "İstanbul yaşam maliyeti bilgisi",
  "response_continue": "CONTINUE",
  "action": {
    "action_number": 0,
    "action_confidence": 1.0,
    "city_name": null
  }
}
```

**User Input**: "Tell me about Yozgat"
**Correct Response**:
```json
{
  "natural_response": "I can help you with the cost of living in Yozgat. I can provide information about Real Estate, Education, Market Prices, and Transportation costs. Which category would you like me to research first?",
  "user_intent_turkish": "Yozgat yaşam maliyeti bilgisi",
  "response_continue": "CONTINUE",
  "action": {
    "action_number": 0,
    "action_confidence": 1.0,
    "city_name": null
  }
}
```

### Correct Usage - Specific Tools with STOP:
**User Input**: "What are rent prices in Istanbul?"
**Correct Response**:
```json
{
  "natural_response": "Let me get the real estate pricing information for Istanbul.",
  "user_intent_turkish": "İstanbul emlak fiyatları",
  "response_continue": "STOP",
  "action": {
    "action_number": 1,
    "action_confidence": 0.9,
    "city_name": "Istanbul"
  }
}
```

**User Input**: "I need grocery prices"
**Correct Response**:
```json
{
  "natural_response": "I'll get the current grocery pricing information for you.",
  "user_intent_turkish": "Market fiyatları",
  "response_continue": "STOP",
  "action": {
    "action_number": 2,
    "action_confidence": 0.9,
    "city_name": null
  }
}
```

## User Intent Turkish Examples
The `user_intent_turkish` field should be concise and direct:

- **Real Estate**: "Ankara emlak fiyatları", "İstanbul kira fiyatları"
- **Grocery**: "Market fiyatları", "Gıda maliyetleri"
- **Education**: "Boğaziçi Üniversitesi ücretleri", "Eğitim maliyetleri"
- **Transport**: "Ankara ulaşım maliyetleri", "Benzin fiyatları"
- **General**: "Genel yaşam maliyeti bilgisi"

## Language-Specific Examples

### Turkish Interaction
**User**: "Merhaba, Ankara'ya taşınacağım"
**Response**: 
```json
{
  "natural_response": "Merhaba! Ankara için yaşam maliyeti konusunda size yardımcı olabilirim. Emlak, Eğitim, Market Fiyatları ve Ulaşım maliyetleri hakkında bilgi verebilirim. Hangi kategoriyi önce araştırmamı istersiniz?",
  "user_intent_turkish": "Ankara yaşam maliyeti bilgisi",
  "response_continue": "CONTINUE",
  "action": {
    "action_number": 0,
    "action_confidence": 1.0,
    "city_name": null
  }
}
```

**User**: "Tavuk fiyatları nedir?"
**Response**:
```json
{
  "natural_response": "Sizin için market fiyatlarını kontrol ediyorum.",
  "user_intent_turkish": "Market fiyatları",
  "response_continue": "STOP",
  "action": {
    "action_number": 2,
    "action_confidence": 0.9,
    "city_name": null
  }
}
```

### English Interaction
**User**: "I want to move to Ankara"
**Response**:
```json
{
  "natural_response": "That's great! I can provide information about Real Estate, Education, Market Prices, and Transportation costs in Ankara. Which category would you like me to research first?",
  "user_intent_turkish": "Ankara yaşam maliyeti bilgisi",
  "response_continue": "CONTINUE",
  "action": {
    "action_number": 0,
    "action_confidence": 1.0,
    "city_name": null
  }
}
```

**User**: "What are housing costs in Ankara?"
**Response**:
```json
{
  "natural_response": "Let me get the real estate pricing information for Ankara.",
  "user_intent_turkish": "Ankara emlak fiyatları",
  "response_continue": "STOP",
  "action": {
    "action_number": 1,
    "action_confidence": 0.9,
    "city_name": "Ankara"
  }
}
```

**Note:**
Continue the chat according to the language used by the customer.
**Example:**
**You:**  "Is there anything else I can help you with today?"
**Customer:** "Ankarada ev bulmaya çalışıyorum" //Turkish
**You:** "Tamamdır sizin için ev fiyatlarına bakıyorum." //continue with Turkish

**Example:**
**You:**  "Size nasıl yardımcı olabilirim?"
**Customer:** "Im looking for houses in Ankara" //English
**You:** "Alright. Ill look for houses in Ankara for you." //continue with English

## Operational Rules

1. **Default to Action 0**: When in doubt, always use action_number 0 with "CONTINUE"
2. **Clarity First**: Always ask for clarification if the user's request is not specific enough
3. **No Assumptions**: Don't assume what type of information the user wants based on city names alone
4. **Specific Requests Only**: Only use tools 1-4 when the user has explicitly requested that specific type of information
5. **Information Categories**: When users don't specify needs, inform them you can provide information about: Real Estate, Education, Market Prices, and Transportation
6. **Tool Output Processing**: After receiving a STOP command and tool results, generate a natural, helpful response based on the data
7. **Turkish Intent**: Always include a concise Turkish phrase in `user_intent_turkish` that directly describes what the user wants
8. **STOP Condition**: The next prompt after the stop condition will be the context of the context provided by the prompt and you must answer only by the given context
9.After the stop condition if the context is about
10. **No Guidence**: If the user asks you for data you cant fetch, then politely say you cant do it and tell the user what you can do.
11.**RE-USE TOOL OUTPUTS IF AVAILABLE**: Always reuse the outputs given to you if the user give a followup query about the same topic. The tool outputs will be given to you in the format "TOOL OUTPUT FROM x WITH INPUT y : output" Use CONTINUE code if youre doing so.
12.After reviewing the context for real estate always write links after the information
## Best Practices
- Always match the user's language preference
- When users says hi call user by his name. 
- Use the user's original phrasing in city_name when possible
- Be conversational and helpful rather than robotic
- Guide users naturally toward the information they need
- Keep `user_intent_turkish` short and direct (2-4 words when possible)
- **REMEMBER**: If the user does not specify a particular information category, always use action_number 0 and response_continue "CONTINUE"
- Only execute tools when the user has made a clear, specific request for that type of information
"""

    def set_user_info(self, name, monthly_salary, family_size, current_city, target_city=None):
        self.user_info = {
            "name": name,
            "monthly_salary": monthly_salary,
            "family_size": family_size,
            "current_city": current_city,
            "target_city": target_city
        }
        # Create initial context message
        context = f"User Information:\nName: {name}\nMonthly Salary: {monthly_salary}\nFamily Size: {family_size}\nCurrent City: {current_city}"
        if target_city:
            context += f"\nTarget City: {target_city}"
        return context

    def root_llm_response(self, message, history):
        if not self.user_info:
            return "Please fill out the user information form first."

        try:
            # Create a more detailed context with user information
            context = f"""User Information:
            Name: {self.user_info['name']}
            Monthly Salary: {self.user_info['monthly_salary']} TL
            Family Size: {self.user_info['family_size']} persons
            Current City: {self.user_info['current_city']}"""

            if self.user_info['target_city']:
                context += f"\nTarget City: {self.user_info['target_city']}"

            context += f"\n\nPrevious conversation history:\n"
            for user_msg, bot_msg in history:
                context += f"User: {user_msg}\nAssistant: {bot_msg}\n"

            context += f"\nCurrent user message: {message}"

            response = self.send_message(context)

            tools = {1:"Real Estate",
                     2:"Market Price",
                     3:"Education Price",
                     4:"Fuel Price",
                     5:"Transportation"}

            # If response is already a dictionary
            if isinstance(response, dict):
                if "natural_response" in response and response.get("response_continue") == "CONTINUE":
                    print(response)
                    return response["natural_response"]

                elif "natural_response" in response and response.get("response_continue") == "STOP":
                    summary=orchestrator_response(response)
                    print("Summary agent response"+summary)
                    output_text = "TOOL OUTPUT FROM " + tools[response["action"]["action_number"]] + " WITH INPUT"

                    if response["action"].get("city_name"):
                        output_text += " " + response["action"]["city_name"]

                    if response.get("user_intent_turkish"):
                        output_text += " " + response["user_intent_turkish"]

                    output_text += ": \n" + summary

                    output_response = self.send_message(summary)
                    print(output_response)

                    return output_response["natural_response"]
            # For any other type, convert to string
            else:
                return str(response)

        except Exception as e:
            return f"I apologize, but I encountered an error while processing your request. Please try again. Error: {str(e)}"

rootl_llm = RootLLM()

import gradio as gr

# List of all 81 provinces of Turkey
TURKISH_PROVINCES = [
    "Adana", "Adıyaman", "Afyonkarahisar", "Ağrı", "Amasya", "Ankara", "Antalya", "Artvin", "Aydın", "Balıkesir",
    "Bilecik", "Bingöl", "Bitlis", "Bolu", "Burdur", "Bursa", "Çanakkale", "Çankırı", "Çorum", "Denizli",
    "Diyarbakır", "Edirne", "Elazığ", "Erzincan", "Erzurum", "Eskişehir", "Gaziantep", "Giresun", "Gümüşhane", "Hakkari",
    "Hatay", "Isparta", "Mersin", "İstanbul", "İzmir", "Kars", "Kastamonu", "Kayseri", "Kırklareli", "Kırşehir",
    "Kocaeli", "Konya", "Kütahya", "Malatya", "Manisa", "Kahramanmaraş", "Mardin", "Muğla", "Muş", "Nevşehir",
    "Niğde", "Ordu", "Rize", "Sakarya", "Samsun", "Siirt", "Sinop", "Sivas", "Tekirdağ", "Tokat",
    "Trabzon", "Tunceli", "Şanlıurfa", "Uşak", "Van", "Yozgat", "Zonguldak", "Aksaray", "Bayburt", "Karaman",
    "Kırıkkale", "Batman", "Şırnak", "Bartın", "Ardahan", "Iğdır", "Yalova", "Karabük", "Kilis", "Osmaniye", "Düzce"
]

# List of universities
universiteler = [
    "Alanya - Alanya HEP Üniversitesi",
    "Ankara - Ankara Bilim Üniversitesi",
    "Ankara - Ankara Medipol Üniversitesi",
    "Antalya - Antalya Belek Üniversitesi",
    "Ankara - Atılım Üniversitesi",
    "Trabzon - Avrasya Üniversitesi",
    "İstanbul - Bahçeşehir Üniversitesi",
    "Ankara - Başkent Üniversitesi",
    "İstanbul - Beykent Üniversitesi",
    "İstanbul - Beykoz Üniversitesi",
    "İstanbul - Bezm-i Âlem Vakıf Üniversitesi",
    "Ankara - Bilkent Üniversitesi",
    "İstanbul - Biruni Üniversitesi",
    "Mersin - Çağ Üniversitesi",
    "Ankara - Çankaya Üniversitesi",
    "Ankara - Demircioglu Bilim Üniversitesi",
    "İstanbul - Doğuş Üniversitesi",
    "İstanbul - Fatih Sultan Mehmet Üniversitesi",
    "İstanbul - Fenerbahçe Üniversitesi",
    "İstanbul - Haliç Üniversitesi",
    "Gaziantep - Hasan Kalyoncu Üniversitesi",
    "İstanbul - İbn Haldun Üniversitesi",
    "İstanbul - İstanbul 29 Mayıs Üniversitesi",
    "İstanbul - İstanbul Atlas Üniversitesi",
    "İstanbul - İstanbul Aydın Üniversitesi",
    "İstanbul - İstanbul Bilgi Üniversitesi",
    "İstanbul - İstanbul Esenyurt Üniversitesi",
    "İstanbul - İstanbul Galata Üniversitesi",
    "İstanbul - İstanbul Gedik Üniversitesi",
    "İstanbul - İstanbul Kent Üniversitesi",
    "İstanbul - İstanbul Kültür Üniversitesi",
    "İstanbul - İstanbul Nişantaşı Üniversitesi",
    "İstanbul - İstanbul Rumeli Üniversitesi",
    "İstanbul - İstanbul Sabahattin Zaim Üniversitesi",
    "İstanbul - İstanbul Sağlık ve Sosyal Bilimler Meslek Yüksekokulu",
    "İstanbul - İstanbul Sağlık ve Teknoloji Üniversitesi",
    "İstanbul - İstanbul Şişli Meslek Yüksekokulu",
    "İstanbul - İstanbul Ticaret Üniversitesi",
    "İstanbul - İstanbul Yeni Yüzyıl Üniversitesi",
    "İstanbul - İstinye Üniversitesi",
    "İzmir - İzmir Ekonomi Üniversitesi",
    "İstanbul - Kadir Has Üniversitesi",
    "Nevşehir - Kapadokya Üniversitesi",
    "İstanbul - Koç Üniversitesi",
    "Kocaeli - Kocaeli Sağlık ve Teknoloji Üniversitesi",
    "Konya - Konya Gıda ve Tarım Üniversitesi",
    "Ankara - Lokman Hekim Üniversitesi",
    "İstanbul - Maltepe Üniversitesi",
    "Bursa - Mudanya Üniversitesi",
    "Kayseri - Nuh Naci Yazgan Üniversitesi",
    "Ankara - Ostim Teknik Üniversitesi",
    "İstanbul - Özyeğin Üniversitesi",
    "İstanbul - Piri Reis Üniversitesi",
    "İstanbul - Sabancı Üniversitesi",
    "Gaziantep - Sanko Üniversitesi",
    "Ankara - TED Üniversitesi",
    "Ankara - TOBB Ekonomi ve Teknoloji Üniversitesi",
    "Mersin - Toros Üniversitesi",
    "Ankara - Türk Hava Kurumu Üniversitesi",
    "İstanbul - Üsküdar Üniversitesi",
    "İzmir - Yaşar Üniversitesi",
    "Ankara - Yüksek İhtisas Üniversitesi"
]

# Create a dictionary of universities by city
universities_by_city = {}
for uni in universiteler:
    city, university = uni.split(" - ")
    if city not in universities_by_city:
        universities_by_city[city] = []
    universities_by_city[city].append(uni)

# Get list of cities that have universities
university_cities = sorted(list(universities_by_city.keys()))

def format_salary_input(value):
    """Format salary input with dots as thousands separators"""
    if not value:
        return ""
    
    # Remove any existing dots and spaces
    clean_value = value.replace(".", "").replace(" ", "")
    
    # Check if it's a valid number
    try:
        num = int(clean_value)
        # Format with dots as thousands separators
        formatted = f"{num:,}".replace(",", ".")
        return formatted
    except ValueError:
        # If not a valid number, return the original value
        return value

def create_user_info_form():
    with gr.Blocks() as form:
        gr.Markdown("# User Information Form")
        with gr.Row():
            name = gr.Textbox(label="Name", placeholder="Enter your name")
            monthly_salary = gr.Textbox(
                label="Monthly Salary (TL)", 
                placeholder="e.g., 15.000 or 100.000",
                info="Enter your monthly salary (dots will be added automatically)"
            )
        with gr.Row():
            family_size = gr.Number(label="Family Size", info="Number of family members")
            current_city = gr.Dropdown(
                choices=TURKISH_PROVINCES,
                label="Current City",
                info="Select your current city",
                allow_custom_value=False
            )
        target_city = gr.Dropdown(
            choices=TURKISH_PROVINCES,
            label="Target City (Optional)",
            info="Select the city you want to move to",
            allow_custom_value=False
        )
        submit_btn = gr.Button("Submit")
        status = gr.Markdown("Please fill out all required fields to start chatting.")
        return form, name, monthly_salary, family_size, current_city, target_city, submit_btn, status

def create_chat_interface():
    with gr.Blocks() as chat:
        chatbot = gr.Chatbot(
            elem_id="chatbot",
            height=600,
            show_copy_button=True,
            bubble_full_width=False,
            show_label=False,
        )
        with gr.Row():
            msg = gr.Textbox(
                label="Message",
                placeholder="Type your message and press Enter or click Send...",
                show_label=False,
                container=False,
                scale=9,
            )
            submit = gr.Button("Send", variant="primary", scale=1)
        return chat, chatbot, msg, submit

def show_agent_selector():
    return gr.update(visible=True)

def hide_agent_selector():
    return gr.update(visible=False)

def show_university_dropdown(agent_name):
    if agent_name == "Education Pricing Agent":
        return gr.update(visible=True), gr.update(visible=False)
    return gr.update(visible=False), gr.update(visible=False)

def update_university_list(city):
    if city:
        return gr.update(choices=universities_by_city[city], visible=True)
    return gr.update(choices=[], visible=False)

def select_agent(agent_name, message, university, history):
    if not agent_name:
        return history, ""
    
    # Format the message to explicitly request the selected agent
    if agent_name == "Education Pricing Agent" and university:
        formatted_message = f"I want to use the {agent_name} agent for {university}. {message if message else ''}"
    else:
        formatted_message = f"I want to use the {agent_name} agent. {message if message else ''}"
        
    response = rootl_llm.root_llm_response(formatted_message, history)
    print(response)
    history.append((message if message else f"Use {agent_name}", response))
    return history, ""

def submit_user_info(name, salary, family_size, current_city, target_city):
    if not all([name, salary, family_size, current_city]):
        return "Please fill out all required fields.", gr.update(visible=True), gr.update(visible=False), gr.update(visible=False), []
    

    context = rootl_llm.set_user_info(name, salary, family_size, current_city, target_city)
    
    # Create welcome message with user info
    welcome_message = f"""👋 Merhaba {name}! I'm your Turkish Regional Cost of Living Advisor.

I understand you're currently living in {current_city} with a monthly salary of {salary:,} TL and a family size of {family_size} people."""

    if target_city:
        welcome_message += f"\n\nI see you're interested in {target_city}. That's a great choice!"
    
    welcome_message += """

I can help you with detailed information about:
• 🏠 Real Estate prices and rental costs
• 🛒 Grocery and market prices
• 🎓 Education costs and university fees
• ⛽ Fuel prices
• 🚌 Public transportation costs

What would you like to know more about?"""

    # Initialize chat history with welcome message
    chat_history = [("", welcome_message)]
    
    return "User information submitted successfully!", gr.update(visible=False), gr.update(visible=True), gr.update(visible=True), chat_history

def chat_response(message, history):
    if not message:
        return history, ""
    
    # Get response from LLM
    response = rootl_llm.root_llm_response(message, history)
    
    # Append the new message and response to history
    history.append((message, response))
    return history, ""

with gr.Blocks() as demo:
    gr.Markdown("# Turkish Regional Cost of Living Advisor")
    
    with gr.Row():
        # Left column - User info form and Agent selection
        with gr.Column(scale=1) as left_column:
            # User info form section
            with gr.Column(visible=True) as form_section:
                form, name, salary, family_size, current_city, target_city, submit_btn, status = create_user_info_form()
            
            # Agent section
            with gr.Column(visible=False) as agent_section:
                # Agent selector
                gr.Markdown("### Select an Agent")
                agent_dropdown = gr.Dropdown(
                    choices=[
                        "Real Estate Agent",
                        "Grocery Pricing Agent",
                        "Education Pricing Agent",
                        "Fuel Price Agent",
                        "Public Transportation Agent"
                    ],
                    label="Agent",
                    info="Select the agent you want to use"
                )
                university_city_dropdown = gr.Dropdown(
                    choices=university_cities,
                    label="Select City",
                    info="Select a city to see its universities",
                    visible=False
                )
                university_dropdown = gr.Dropdown(
                    choices=[],
                    label="Select University",
                    info="Select a university for education pricing",
                    visible=False
                )
                agent_message = gr.Textbox(
                    label="Additional Message (Optional)",
                    placeholder="Add any specific details for the agent...",
                    info="Leave empty to use the agent with current chat context"
                )
                use_agent_btn = gr.Button("Use Selected Agent")
        
        # Right column - Chat interface
        with gr.Column(scale=2, visible=False) as chat_column:
            chat, chatbot, msg, submit = create_chat_interface()
    
    # Handle salary formatting
    salary.change(
        format_salary_input,
        inputs=[salary],
        outputs=[salary]
    )
    
    # Handle form submission
    submit_btn.click(
        submit_user_info,
        inputs=[name, salary, family_size, current_city, target_city],
        outputs=[status, form_section, agent_section, chat_column, chatbot]
    )
    
    # Handle chat
    msg.submit(
        chat_response,
        inputs=[msg, chatbot],
        outputs=[chatbot, msg]
    )
    
    submit.click(
        chat_response,
        inputs=[msg, chatbot],
        outputs=[chatbot, msg]
    )
    
    # Handle agent selection
    agent_dropdown.change(
        show_university_dropdown,
        inputs=[agent_dropdown],
        outputs=[university_city_dropdown, university_dropdown]
    )
    
    university_city_dropdown.change(
        update_university_list,
        inputs=[university_city_dropdown],
        outputs=[university_dropdown]
    )
    
    use_agent_btn.click(
        select_agent,
        inputs=[agent_dropdown, agent_message, university_dropdown, chatbot],
        outputs=[chatbot, agent_message]
    )

demo.launch()


