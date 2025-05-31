# AI-Powered Regional Cost of Living Advisor

A comprehensive AI-powered system that helps users make informed decisions about relocating to different Turkish cities by providing detailed cost of living information across multiple categories.

## 🌟 Features

### Multi-Agent Architecture
- **Root Orchestrator**: Central coordination system that manages user interactions and routes requests to specialized agents
- **Real Estate Agent**: Provides property prices, rental costs, and utility expenses with RAG-powered data retrieval
- **Market Agent**: Delivers grocery and food pricing information across different product categories
- **Education Agent**: Offers university tuition fees and educational cost analysis
- **Transportation Agent**: Supplies fuel prices and public transportation costs
- **Summary Agent**: Generates comprehensive cost analysis reports

### Intelligent Conversation Flow
- Natural language processing in both English and Turkish
- Context-aware responses with confidence scoring
- Dynamic tool selection based on user intent
- Structured JSON responses for seamless integration

### Modern Web Interface
- **Frontend**: Angular-based responsive web application
- **Backend**: Flask REST API with JWT authentication
- **Database**: SQLite for user management
- **Real-time Chat**: Interactive conversation interface

## 🏗️ Project Structure

```
AI-Powered-Regional-Cost-of-Living-Advisor/
├── Root-Orchestrator/          # Central coordination system
│   ├── RootLLM.py             # Main orchestrator logic
│   ├── SummaryAgent.py        # Report generation
│   └── AgentOrchestrator.py   # Agent coordination
├── Real_Estate_Agent/         # Property and housing costs
│   ├── RealEstateAgent.py     # Main agent logic
│   ├── RealEstateRAG.py       # RAG implementation
│   ├── Crawl.py              # Data collection
│   └── chroma_db/            # Vector database
├── MarketAgent/               # Grocery and food pricing
│   ├── proj_market_pipeline_agent.py
│   ├── proj_market_pipeline.py
│   └── proj_market_parser.py
├── EducationAgent/            # University costs
│   └── Rag/                  # Education data storage
├── TransportationAgent/       # Transport and fuel costs
│   ├── FuelPriceAgent.py     # Fuel pricing logic
│   ├── FuelPriceCrawler.py   # Data collection
│   └── Transportation_Prices/ # Transport data
├── api/                       # Backend API
│   ├── api.py                # Flask application
│   └── main.py               # API entry point
├── front-end/                 # Angular web application
│   ├── src/                  # Source code
│   ├── package.json          # Dependencies
│   └── angular.json          # Angular configuration
├── proj_llm_agent.py         # Core LLM agent class
├── KeywordAgent.py           # Keyword processing
└── CreateChat.py             # Chat interface
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- Angular CLI
- Google Gemini API Key

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/AI-Powered-Regional-Cost-of-Living-Advisor.git
   cd AI-Powered-Regional-Cost-of-Living-Advisor
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Create .env file
   echo "GOOGLE_API_KEY=your_gemini_api_key_here" > .env
   ```

4. **Run the Flask API**
   ```bash
   cd api
   python api.py
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd front-end
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   ng serve
   ```

4. **Access the application**
   - Frontend: `http://localhost:4200`
   - Backend API: `http://localhost:5000`

## 🎯 Usage

### Web Interface
1. Open your browser and navigate to `http://localhost:4200`
2. Create an account or log in
3. Start a conversation about your relocation plans
4. Ask about specific cost categories:
   - **Real Estate**: "What are rent prices in Istanbul?"
   - **Groceries**: "I need food price information"
   - **Education**: "Tell me about Bogazici University fees"
   - **Transportation**: "What are gas prices in Antalya?"

### API Integration
```python
# Example API usage
import requests

# Login
response = requests.post('http://localhost:5000/api/login', json={
    'username': 'your_username',
    'password': 'your_password'
})

token = response.json()['access_token']

# Get user profile
headers = {'Authorization': f'Bearer {token}'}
profile = requests.get('http://localhost:5000/api/profile', headers=headers)
```

### Direct Agent Usage
```python
from Root-Orchestrator.RootLLM import RootLLM

# Initialize the root agent
root_agent = RootLLM()

# Set user information
root_agent.set_user_info(
    name="John Doe",
    monthly_salary=15000,
    family_size=3,
    current_city="Ankara",
    target_city="Istanbul"
)

# Get response
response = root_agent.root_llm_response("I want to move to Istanbul", [])
print(response)
```

## 🔧 Configuration

### Agent Configuration
Each agent can be configured with different parameters:

```python
# Example agent configuration
agent = LLM_Agent(
    name="Custom Agent",
    role="Your custom role description",
    response_mime_type="application/json",
    model="gemini-2.0-flash",
    temperature=0.95,
    top_p=0.9,
    top_k=40
)
```

### Database Configuration
The system uses SQLite by default. To use a different database:

```python
# In api/api.py
app.config['SQLALCHEMY_DATABASE_URI'] = 'your_database_url_here'
```

## 🤖 AI Agents

### Root Orchestrator
- **Purpose**: Central coordination and user intent analysis
- **Capabilities**: Multi-language support (English/Turkish), tool selection, conversation management
- **Response Format**: Structured JSON with natural language responses

### Real Estate Agent
- **Purpose**: Property pricing and housing cost analysis
- **Data Sources**: Real estate websites, utility companies
- **Features**: RAG-powered search, utility cost calculations, property comparisons

### Market Agent
- **Purpose**: Grocery and food pricing information
- **Coverage**: Various product categories, price comparisons
- **Features**: Real-time price updates, category-based analysis

### Education Agent
- **Purpose**: University tuition and educational costs
- **Coverage**: Turkish universities, program-specific pricing
- **Features**: University-specific searches, cost breakdowns

### Transportation Agent
- **Purpose**: Fuel prices and public transportation costs
- **Coverage**: City-specific fuel prices, public transport fees
- **Features**: Real-time fuel price updates, transport cost analysis

## 📊 Data Sources

- **Real Estate**: HepsieEmlak.com and other property websites
- **Market Prices**: Major grocery chains and market data
- **Education**: University official websites and databases
- **Transportation**: Official fuel price APIs and transport authorities

## 🔒 Security

- JWT-based authentication
- Password hashing with Werkzeug
- CORS configuration for secure cross-origin requests
- Environment variable protection for API keys

## 🌐 API Endpoints

### Authentication
- `POST /api/signup` - User registration
- `POST /api/login` - User authentication
- `GET /api/profile` - Get user profile (requires JWT)

### Chat Interface
- WebSocket connections for real-time chat
- RESTful endpoints for conversation management

## 🧪 Testing

```bash
# Run Python tests
python -m pytest

# Run Angular tests
cd front-end
ng test
```

## 📈 Performance

- **Response Time**: < 3 seconds for most queries
- **Concurrent Users**: Supports multiple simultaneous conversations
- **Data Freshness**: Real-time data updates for pricing information
- **Cost Tracking**: Built-in API usage and cost monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google Gemini API for AI capabilities
- Angular team for the frontend framework
- Flask community for the backend framework
- ChromaDB for vector database functionality

## 📞 Support

For support, email support@example.com or create an issue in the GitHub repository.

## 🔮 Future Enhancements

- [ ] Mobile application development
- [ ] Additional city coverage beyond Turkey
- [ ] Integration with more data sources
- [ ] Advanced analytics and reporting
- [ ] Multi-currency support
- [ ] Offline mode capabilities
- [ ] Voice interface integration

---

**Made with ❤️ for helping people make informed relocation decisions** 