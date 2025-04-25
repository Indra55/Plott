# 📊 AI Diagram Generator

<div align="center">

![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![Flask](https://img.shields.io/badge/flask-latest-blue)
![React](https://img.shields.io/badge/react-18.2.0-blue)
![Gemini API](https://img.shields.io/badge/AI-Gemini%202.0-green)

**Transform natural language into beautiful statistical visualizations powered by Google's Gemini API**

[Features](#✨-features) • [Installation](#📋-installation) • [Usage](#🔍-usage) • [Examples](#📝-example-prompts) • [License](#📄-license)

</div>

## ✨ Features

- 💬 **Natural Language Interface** - Request charts using plain English
- 🧠 **AI-Powered Chart Recommendation** - Automatically suggests ideal chart types for your data
- 📊 **Multiple Visualization Types** - Supports various chart types:
  - Bar charts & stacked bar charts
  - Line graphs
  - Pie charts
  - Scatter plots
  - Histograms
  - Heatmaps
  - Boxplots
  - Violin plots
  - Area charts
  - Treemaps
  - Radar charts
  - Bubble charts
  - Funnel charts
- 🤖 **Intelligent Sample Data Generation** - Creates realistic example data when none is provided
- 🎨 **Customization Options** - Control colors, labels, and styling through your prompts
- 💾 **Export Functionality** - Download visualizations in various formats
- 🔄 **Prompt History** - Save and reuse previous visualization requests
- 🌓 **Light/Dark Mode** - Choose your preferred theme
- ♿ **Accessibility Features** - High contrast mode and screen reader support

## 💻 Tech Stack

### Backend
- **Language**: Python 3.8+
- **Framework**: Flask with Flask-CORS and Flask-Limiter
- **AI Model**: Google Gemini 2.0 Flash
- **Data Processing**: Pandas, NumPy
- **Visualization**: Matplotlib, Seaborn, Squarify
- **Environment Management**: python-dotenv

### Frontend
- **Framework**: React 18.2.0
- **Build Tool**: Vite 4.4.5
- **Animation**: Framer Motion
- **HTTP Client**: Axios
- **UI**: Custom CSS with light/dark themes

## 📋 Installation

### Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Backend Setup

1. Clone the repository and navigate to the backend directory:
   ```bash
   git clone https://github.com/yourusername/ai-diagram-generator.git
   cd ai-diagram-generator/backend
   ```

2. Create and activate a virtual environment:
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file and add your Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

5. Start the backend server:
   ```bash
   python app.py
   ```
   The server will start on http://localhost:5000

### Frontend Setup

1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd ai-diagram-generator/frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```
   The frontend will be available at http://localhost:3000

## 🔍 Usage

1. Enter a natural language prompt describing the visualization you need
2. Click "Generate Diagram" or press Enter
3. The application will:
   - Analyze your request using the Gemini API
   - Recommend suitable chart types
   - Generate appropriate sample data if needed
   - Create and display the visualization
4. You can:
   - Download the generated chart
   - Copy the image to clipboard
   - Share the visualization
   - Use the "Magic Enhance" feature to improve your prompt
   - Toggle between light and dark modes
   - Access high contrast mode for better accessibility

## 📝 Example Prompts

| Prompt | Chart Type |
|--------|------------|
| "Create a bar chart showing quarterly sales for 2023 with blue gradient" | Bar Chart |
| "Generate a pie chart for market share of top 5 smartphone brands" | Pie Chart |
| "Show a line graph of temperature trends in New York over the past decade" | Line Chart |
| "Make a scatter plot comparing height and weight for 50 people" | Scatter Plot |
| "Create a heatmap showing the correlation between different stock prices" | Heatmap |
| "Generate a boxplot showing distribution of test scores across 5 schools" | Boxplot |
| "Create a treemap of market capitalization for tech companies" | Treemap |

## 🔧 Troubleshooting

- **API Key Issues**: Ensure your Gemini API key is correctly set in the `.env` file
- **Rate Limiting**: The application has built-in rate limiting (100 requests per day, 20 per hour)
- **Backend Connection**: If you see connection errors, verify the backend server is running

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [Google Gemini API](https://ai.google.dev/products/gemini-api) for powering the AI capabilities
- [Matplotlib](https://matplotlib.org/) and [Seaborn](https://seaborn.pydata.org/) for visualization libraries
- [React](https://reactjs.org/) and [Vite](https://vitejs.dev/) for the frontend framework 