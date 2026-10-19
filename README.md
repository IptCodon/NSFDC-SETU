# NSFDC-SETU 🇮🇳

### Bridging the Gap Between Citizens and Welfare Schemes Through Technology

**NSFDC-SETU** is a Python-based digital platform designed to simplify access to government welfare schemes and support services. It brings together scheme discovery, location-based information, partner identification, and chatbot assistance in a single interface.

The project aims to make welfare-related information easier to discover and navigate through an accessible, technology-driven platform.

## ✨ Features

- **Interactive User Interface:** Provides a centralized interface for exploring welfare-related information.
- **Scheme Discovery:** Helps users discover relevant government welfare schemes.
- **Geolocation Services:** Supports location-based functionality to help users find relevant information.
- **Partner Locator:** Uses district and partner data to support the discovery of relevant organizations and service partners in Odisha.
- **Chatbot Assistance:** Provides a conversational interface to help users navigate the platform.
- **Structured Data Management:** Uses JSON files to organize district, partner, and scheme information.

## 🛠️ Tech Stack

- **Python** — Core application logic
- **Streamlit** — Web application interface
- **JSON** — Structured data storage
- **Folium / streamlit-folium** — Interactive map functionality, where used

## 📁 Project Structure

```text
NSFDC-SETU/
│
├── app.py
├── backend.py
├── chatbot.py
├── geo_locator.py
│
├── data/
│   ├── districts.json
│   ├── odisha_partners.json
│   └── schemes.json
│
├── .gitignore
└── README.md
```

### Code Overview

**`app.py` — Main Application**
- Serves as the main entry point for the Streamlit application.
- Brings together the user interface and the platform's features.

**`backend.py` — Backend Logic**
- Contains supporting application logic and data-processing functionality.
- Helps separate backend operations from the user interface.

**`chatbot.py` — Chatbot Module**
- Contains the chatbot functionality.
- Supports conversational assistance within the platform.

**`geo_locator.py` — Location Services**
- Contains geolocation-related functionality.
- Supports location-based features and partner discovery.

### Data Directory

- **`districts.json`** — Stores district-related information.
- **`odisha_partners.json`** — Stores information about partners in Odisha.
- **`schemes.json`** — Stores structured information about welfare schemes.

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/IptCodon/NSFDC-SETU.git
cd NSFDC-SETU
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

On Linux or macOS:

```bash
source .venv/bin/activate
```

### 3. Install Dependencies

Install the libraries required by the project. For example, if they are used by your application:

```bash
pip install streamlit folium streamlit-folium
```

Install any additional packages imported by the project files.

### 4. Run the Application

```bash
streamlit run app.py
```

Open the local URL displayed in your terminal to access the application.

## 🎯 Project Objective

NSFDC-SETU aims to improve the discoverability of welfare schemes and related services by bringing information, location-based tools, and conversational assistance together in one platform.

## 🔮 Future Improvements

- Improve scheme recommendations based on user eligibility.
- Expand district-wise partner information.
- Enhance chatbot responses and query handling.
- Improve accessibility, validation, and error handling.
- Expand data coverage and keep scheme information up to date.

## 👨‍💻 Development

This repository contains an independently continued and modified version of the NSFDC-SETU project. The implementation and future improvements will continue to evolve.

For contributions, suggestions, or bug reports, please open an issue in the repository.

---

**Built with Python and Streamlit.**
