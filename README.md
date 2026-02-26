# 🤖 LinkedInAuto

An intelligent job application automation pipeline that combines browser automation with a Hugging Face QA model to autonomously complete and submit LinkedIn Easy Apply applications — end to end.

---

## 🧠 How It Works

```
LinkedIn Job Listings
        │
        ▼
Job Filter & Scraper (Selenium)
        │
        ▼
Application Form Parser
        │
        ▼
Hugging Face QA Model (DistilBERT)
  ├── Work authorization questions
  ├── Visa / sponsorship fields
  └── Technical screening questions
        │
        ▼
Auto-Submit + Application Logger
```

---

## ⚡ Key Features

- **Smart Form Parsing** — DistilBERT-based extractive QA model dynamically reads and answers application form fields with **95% accuracy**, including work authorization, technical screening, and custom questions
- **End-to-End Automation** — Headless Selenium suite navigates job search, applies filters, opens listings, and submits applications without human input
- **Application Logging** — All submitted applications are logged with job title, company, date, and status for tracking
- **Scale** — Successfully automated 100+ job applications, reducing per-application time by **90%**

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Browser Automation | Selenium WebDriver (headless) |
| QA Model | Hugging Face Transformers (DistilBERT) |
| NLP | Hugging Face `pipeline("question-answering")` |
| Language | Python 3.10+ |

---

## 🚀 Getting Started

```bash
# Clone the repo
git clone https://github.com/DivyaNamburG/LinkedInAuto.git
cd LinkedInAuto

# Install dependencies
pip install -r requirements.txt

# Configure your profile
cp config.example.json config.json
# Edit config.json with your job preferences and answers

# Run the bot
python main.py
```

---

## ⚙️ Configuration

Edit `config.json` to set your preferences:

```json
{
  "job_title": "Software Engineer",
  "location": "New Jersey",
  "easy_apply_only": true,
  "answers": {
    "authorized_to_work": "Yes",
    "require_sponsorship": "No",
    "years_of_experience": "4"
  }
}
```

---

## 📁 Project Structure

```
LinkedInAuto/
├── main.py                # Entry point
├── scraper.py             # Job listing scraper
├── form_parser.py         # Form field detection
├── qa_model.py            # Hugging Face QA inference
├── submitter.py           # Application submission logic
├── logger.py              # Application tracking
├── config.example.json    # Config template
└── requirements.txt
```

---

## 📊 Results

| Metric | Value |
|---|---|
| Applications Submitted | 100+ |
| Form Answer Accuracy | 95% |
| Time Saved per Application | ~90% reduction vs. manual |

---

## ⚠️ Note

This tool is intended for personal productivity and educational purposes. Use responsibly and in accordance with LinkedIn's Terms of Service.
