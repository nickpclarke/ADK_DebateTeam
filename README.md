# AI Debate Team 🤖⚖️

A sophisticated multi-agent debate system built with Google's Agent Development Kit (ADK). Watch AI agents research, debate, and analyze complex topics from multiple perspectives.

## 🎯 Features

- **Multi-Agent Architecture**: 5 specialized AI agents working in harmony
- **Intelligent Research**: Parallel research agents investigate both sides using Google Search
- **Structured Debates**: 3-round debate format with opening, response, and rebuttal
- **Balanced Analysis**: Objective summaries highlighting key arguments and evidence
- **Continuous Conversation**: Natural flow allowing multiple debate topics in one session

## 🏗️ Architecture

### Agent Pipeline:
1. **DebateTeamGreeter** - Conversational host and topic extraction
2. **RoleAssignmentAgent** - Defines Proponent vs Opponent positions  
3. **ParallelStanceResearcher** - Simultaneous research on both sides
4. **DebateRoundExecutor** - Conducts structured 3-round debates
5. **DebateSummarizerAgent** - Balanced analysis and return to greeter

### Technical Stack:
- **Google ADK** - Multi-agent orchestration
- **Google Search API** - Real-time research capabilities
- **Vertex AI** - LLM processing via Gemini models
- **Python 3.9+** - Core implementation
- **UV/Poetry** - Dependency management

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Google Cloud Project with Vertex AI enabled
- Google Cloud SDK installed and authenticated

### Local Setup

1. **Clone the repository**:
```bash
git clone <repository-url>
cd ADK_Multiagent
```

2. **Install dependencies**:
```bash
# Using UV (recommended)
uv pip install -r requirements.txt
uv pip install -e .

# Or using pip
pip install -r requirements.txt
pip install -e .
```

3. **Configure environment**:
```bash
# Copy and edit .env file
cp .env.example .env
# Add your Google Cloud credentials
```

4. **Run locally**:
```bash
adk web
```

5. **Open browser** to `http://localhost:8000`

### Sample Interaction
```
User: Hello
Bot: Hello! I'm your host for the Advanced AI Debate Team...

User: renewable energy vs fossil fuels
Bot: Great! Let's debate: renewable energy vs fossil fuels
[Full research → debate → summary process]

Bot: Thanks for the interesting debate! Ready for another topic?
```

## ☁️ Cloud Deployment

### Deploy to Google Cloud:
```bash
python deployment/deploy.py --create \
  --project_id YOUR_PROJECT \
  --location us-central1 \
  --bucket YOUR_BUCKET
```

### Test deployment:
```bash
python deployment/test_deployment.py \
  --resource_id RETURNED_RESOURCE_ID \
  --user_id test_user
```

## 📁 Project Structure

```
ADK_Multiagent/
├── debate_team/           # Main agent package
│   ├── __init__.py       
│   └── agent.py          # All agent definitions
├── deployment/           # Cloud deployment scripts
│   ├── deploy.py        
│   └── test_deployment.py
├── pyproject.toml       # Package configuration
├── requirements.txt     # Dependencies
└── .env                 # Environment variables (not in git)
```

## 🔧 Configuration

### Environment Variables (.env):
```bash
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_CLOUD_STORAGE_BUCKET=your-bucket
GOOGLE_API_KEY=your-api-key
GOOGLE_GENAI_USE_VERTEXAI=1
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Google Agent Development Kit (ADK)](https://github.com/google/adk-python)
- Powered by Vertex AI and Gemini models
- Inspired by structured debate methodologies

## 🐛 Issues & Support

Found a bug? Have a feature request? 
- Open an [issue](../../issues)
- Check out the [discussions](../../discussions)

---

**Ready to watch AI agents debate complex topics?** 🚀 