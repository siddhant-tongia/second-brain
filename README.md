<p align="center">
  <img src="https://img.icons8.com/3d-fluency/94/brain.png" width="100" alt="Second Brain Logo"/>
</p>

<h1 align="center">🧠 Second Brain</h1>

<p align="center">
  <b>Your AI-Powered Personal Knowledge Management System</b><br/>
  <i>Save it. Search it. Remember it — forever.</i>
</p>

<p align="center">
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.8+"/></a>
  <a href="https://www.mysql.com/"><img src="https://img.shields.io/badge/MySQL-8.0+-orange?style=for-the-badge&logo=mysql&logoColor=white" alt="MySQL 8.0+"/></a>
  <a href="https://openrouter.ai/"><img src="https://img.shields.io/badge/AI-OpenRouter-purple?style=for-the-badge&logo=openai&logoColor=white" alt="OpenRouter AI"/></a>
  <a href="https://github.com/siddhant-tongia/second-brain/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge" alt="License MIT"/></a>
</p>

---

## 🌟 What is Second Brain?

**Second Brain** is a CLI-based personal knowledge vault that lets you save, organize, and retrieve your most valuable resources — articles, tutorials, ideas, and bookmarks — using **AI-powered semantic search**.

Stop losing bookmarks in browser tabs. Stop forgetting that *one amazing article* you read last month. Let your Second Brain remember it for you.

> **📌 Status:** Backend (CLI) is complete & functional. A beautiful UI is coming within the next week — stay tuned!

---

## ✨ Features

| Feature | Description |
|---|---|
| 📝 **Add Resources** | Save resources with a title, category, description, and optional link |
| 🤖 **AI-Powered Search** | Ask questions in natural language and the AI finds the most relevant saved resources |
| 📂 **Browse by Category** | Filter and view resources by predefined categories |
| ✏️ **Update Resources** | Edit any field of an existing resource |
| 🗑️ **Delete Resources** | Remove one or multiple resources at once |
| 🔒 **SQL Injection Safe** | Whitelisted column names prevent injection attacks on update queries |

---

## 🧩 Architecture

```
┌──────────────────────────────────────────────────┐
│                   Second Brain                   │
├──────────────────────────────────────────────────┤
│                                                  │
│   User ──► CLI Menu ──► MySQL Database           │
│                │                                 │
│                ├──► AI Search                    │
│                │      │                          │
│                │      ├──► Fetch all resources   │
│                │      ├──► Build prompt           │
│                │      ├──► OpenRouter API (LLM)  │
│                │      └──► Return matched IDs    │
│                │                                 │
│                ├──► CRUD Operations              │
│                └──► Category Browsing            │
│                                                  │
└──────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **MySQL 8.0+** (running locally)
- **OpenRouter API Key** — get one free at [openrouter.ai](https://openrouter.ai/)

### 1. Clone the Repository

```bash
git clone https://github.com/siddhant-tongia/second-brain.git
cd second-brain
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up the Database

```bash
mysql -u root -p < schema.sql
```

Or run the SQL manually:

```sql
CREATE DATABASE IF NOT EXISTS second_brain;
USE second_brain;

CREATE TABLE IF NOT EXISTS resources (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  category VARCHAR(100) NOT NULL,
  short_description TEXT NOT NULL,
  link VARCHAR(500) DEFAULT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
PASSWORD=your_mysql_password
API_KEY=your_openrouter_api_key
Model=tencent/hy3:free
```

### 5. Run the App

```bash
python app.py
```

---

## 🎮 Usage

Once launched, you'll see an interactive menu:

```
===== Second Brain =====
1. Add Resource
2. Search by AI
3. Browse by Category
4. Update Resource
5. Delete Resource
6. Exit
Enter your choice (1-6):
```

### 🤖 AI Search Example

```
> What resources do I have about machine learning?

ID: 3
Title: Andrew Ng's ML Course
Category: AI Resources
Description: Stanford's free machine learning course on Coursera
Link: https://coursera.org/learn/machine-learning
---
```

The AI understands **intent and context** — not just keywords. Ask "something to stay motivated" and it'll find your **Motivation** resources even if the word "motivated" never appears in them.

---

## 📁 Project Structure

```
second-brain/
├── app.py              # Main application — CLI + AI search + CRUD
├── schema.sql          # MySQL database schema
├── requirements.txt    # Python dependencies
├── .env                # Environment variables (git-ignored)
├── .gitignore          # Git ignore rules
└── README.md           # You are here!
```

---

## 📦 Categories

Resources are organized into these categories:

| # | Category | Use Case |
|---|----------|----------|
| 1 | 🤖 AI Resources | ML tutorials, AI papers, tools & APIs |
| 2 | 💡 Business Ideas | Startup concepts, side projects, market insights |
| 3 | 🧮 DSA Concepts | Data structures, algorithms, competitive programming |
| 4 | 🔥 Motivation | Quotes, talks, success stories |
| 5 | 🌱 Personal Growth | Productivity, habits, self-improvement |

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| **Python** | Core application language |
| **MySQL** | Persistent resource storage |
| **OpenAI SDK** | LLM API communication |
| **OpenRouter** | AI model gateway (uses `tencent/hy3:free`) |
| **python-dotenv** | Secure environment variable management |

---

## 🗺️ Roadmap

- [x] Core CRUD operations
- [x] AI-powered semantic search
- [x] Category-based browsing
- [x] SQL injection prevention
- [x] Environment variable management
- [ ] 🎨 **Web UI** (coming this week!)
- [ ] 🏷️ Tag-based search
- [ ] 📊 Dashboard with analytics
- [ ] 📤 Export to Markdown / Notion
- [ ] 🔐 User authentication

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 👤 Author

**Siddhant Tongia**

- GitHub: [@siddhant-tongia](https://github.com/siddhant-tongia)

---

<p align="center">
  <b>⭐ If you found this useful, give it a star!</b><br/>
  <i>Built with ❤️ and a lot of bookmarks that needed organizing.</i>
</p>