# 🕸️ Convert Sitemap Pages to Full TXT

This Python utility takes a plain text list of sitemap URLs, scrapes each page, and exports clean, markdown-formatted `.txt` files — ideal for archiving, search indexing, or ingestion into tools like ChatGPT.

---

## ✅ Features

- 🌐 **Input**: `.txt` file with one URL per line
- ✅ **Validates** each URL for format and reachability
- ⚙️ **Multiprocessing** support for fast scraping
- 🧾 **Markdown-formatted output** organized by tag (h1, h2, p, li)
- 📊 **Summary section** at the top of each output
- 🗂 **Separate log file** with HTTP status and exceptions
- 🪟 **GUI folder picker** for saving output to a custom location
- 🧷 **Output organized into a timestamped folder**
- 🎨 **Color-coded console output**
- 🪄 **Popup notification** when scraping is complete

---

## 📂 Input Format

Your `.txt` file should contain one sitemap URL per line:

```txt
https://example.com/page1
https://example.com/page2
