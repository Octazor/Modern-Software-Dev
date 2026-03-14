# Weather MCP Server (Week 3 Assignment)

## 📌 Overview

This project implements a custom MCP (Model Context Protocol) server using Python.  
The server integrates with an external Weather API (Open-Meteo) and exposes weather-related tools that can be accessed via Claude Desktop.

The server runs locally using STDIO transport and is fully compatible with Claude Desktop MCP integration.

---

## 🎯 Assignment Objectives Fulfilled

- ✅ Use a real external API
- ✅ Expose at least two MCP tools
- ✅ Implement typed parameters
- ✅ Handle error scenarios
- ✅ Run locally via STDIO
- ✅ Provide setup documentation

---

## 🌤️ External API Used

**API Name:** Open-Meteo  
**Website:** https://open-meteo.com/  
**Features Used:**
- Geocoding API (convert city name → latitude & longitude)
- Weather Forecast API (current weather & multi-day forecast)

No API key is required.

---

## 🛠️ MCP Tools Implemented

### 1️⃣ get_current_weather

**Description:**  
Returns current weather information for a given city.

**Parameters:**
- `city` (string) — Name of the city

**Example Usage in Claude:**
```
Cuaca sekarang di Jakarta?
```

---

### 2️⃣ get_weather_forecast

**Description:**  
Returns weather forecast for a given city for a specified number of days.

**Parameters:**
- `city` (string) — Name of the city
- `days` (integer, default = 3) — Number of forecast days

**Example Usage in Claude:**
```
Forecast 5 hari di Bandung
```

---

## 🧑‍💻 Installation & Setup

### 1️⃣ Clone or Create Project Folder

```bash
mkdir week3-weather-mcp
cd week3-weather-mcp
```

---

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
```

Activate environment:

Windows:
```bash
venv\Scripts\activate
```

Mac/Linux:
```bash
source venv/bin/activate
```

---

### 3️⃣ Install Dependencies

```bash
pip install "mcp[cli]" httpx
```

---

### 4️⃣ Run with Claude Desktop

Open Claude Desktop:

Settings → Developer → MCP Servers → Edit Config

Add configuration:

```json
{
  "mcpServers": {
    "weather-server": {
      "command": "C:\\FULL\\PATH\\TO\\venv\\Scripts\\python.exe",
      "args": ["C:\\FULL\\PATH\\TO\\server.py"]
    }
  }
}
```

Restart Claude Desktop.

---

## 🧪 Testing the Server

After configuration, test in Claude chat:

Examples:

- Cuaca sekarang di Surabaya?
- Bagaimana suhu di Bali hari ini?
- Forecast 3 hari di Makassar?

Claude will automatically call the MCP tools.

---

## ⚙️ Technical Implementation Details

- Python 3.10+
- MCP Python SDK (`FastMCP`)
- STDIO transport for Claude Desktop compatibility
- Async HTTP requests using `httpx`
- Error handling for invalid city input

---

## 🚀 Possible Improvements

- Add humidity & precipitation probability
- Format response for cleaner output
- Add logging
- Deploy as remote HTTP MCP server

---

## 📸 Demonstration

The MCP server successfully runs and connects to Claude Desktop, allowing real-time weather queries.

---

## 👨‍🎓 Author

Name: [YOUR NAME]  
Course: Modern Software Development  
Week: 3 Assignment  
Year: 2026
