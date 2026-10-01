# 🏛️ Discover Pakistan Autonomous Media Agent

> **Autonomous Scenic Tourism, Culture & Alpine Travel Dossier Generator**

This repository runs a fully automated, AI-driven content generation and publishing pipeline for **Discover Pakistan** across Meta platforms (Facebook Page & Instagram Business).

---

## ⚡ Setup & Deployment to GitHub Actions

### 1. Configure GitHub Repository Secrets & Variables
Navigate to **Settings → Secrets and variables → Actions** in this GitHub repository:

#### 🔑 Secrets (`Secrets` tab):
- **`GEMINI_API_KEY`**: Your Google Gemini API Key (generates high-converting headlines, body text, and captions).
- **`ACCESS_TOKEN`**: Meta Graph API User/Page Access Token with `pages_manage_posts`, `pages_read_engagement`, and `instagram_content_publish` permissions.

#### ⚙️ Variables (`Variables` tab) *(Optional — pre-configured by default)*:
- **`FB_PAGE_ID`**: Default: `1304442402758898`
- **`IG_BUSINESS_ACCOUNT_ID`**: Default: `17841438750095367`

---

## 📅 Automated Scheduling

This repository runs autonomously on a GitHub Actions cron schedule:
- **Schedule**: `0 5 * * *` UTC (Peak audience engagement time)
- **Workflow File**: `.github/workflows/daily_publish.yml`

You can also trigger runs on-demand from the **Actions** tab with custom topics or format choices.

---

## 💻 Local Development

1. **Clone & Setup Environment:**
   ```bash
   git clone <repo-url>
   cd discover-pakistan
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure `.env`:**
   ```bash
   cp .env.example .env
   # Add your GEMINI_API_KEY and ACCESS_TOKEN
   ```

3. **Run Agent Locally:**
   ```bash
   # Generate editorial card without publishing:
   python run_agent.py --format card --no-publish

   # Generate and publish live:
   python run_agent.py --format card
   ```

---

## 📂 Architecture

- **`run_agent.py`**: Standalone runner orchestrating prompt synthesis and rendering.
- **`video_engine/`**: Studio-grade editorial typography and card compositor.
- **`agents/`**: Multi-model Gemini content director.
- **`publish_reels.py`**: Resilient Meta Graph API upload handler.
- **`assets/fonts/`**: Arabic, Urdu Nastaliq, and Latin typography assets.
