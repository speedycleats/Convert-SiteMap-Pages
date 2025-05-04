# 🧭 Convert Sitemap Pages to Markdown

A user-friendly Windows application to scrape and convert pages from a sitemap `.txt` file into a single, neatly formatted Markdown `.txt` file. No Python experience required—just drag, click, and go.

---

## 📦 Features

- ✅ Drag-and-drop `.exe` support
- 🧠 Auto-validates URLs
- ✨ GUI folder picker for input and output
- 📊 Real-time progress bar
- 🧾 Markdown-style formatting
- 📄 Log + Summary report generation
- 🔒 Packaged with PyInstaller (no dependencies required)

---

## 🛠 How to Use

1. Run the `Convert-Sitemap-To-TXT.exe` from the `dist/` folder
2. Select your input `.txt` sitemap file (1 URL per line)
3. Choose an output folder when prompted
4. Watch the progress bar
5. Get both a full Markdown-formatted output and a scraping log

---

## 📁 Example Output
/output-folder/
├── sitemap-url-list-20250503-full_text_output.txt
├── sitemap-url-list-20250503-log.txt


---

## 📂 Building from Source

1. Clone this repo  
   `git clone https://github.com/speedycleats/Convert-SiteMap-Pages.git`
2. Create virtual environment  
   `python -m venv venv && venv\Scripts\activate`
3. Install dependencies  
   `pip install -r requirements.txt`
4. Package with PyInstaller  
   `pyinstaller --onefile --windowed --icon=NotebookPencilIcon.ico Convert-Sitemap-To-TXT.py`

---

## 🚀 Roadmap

- [ ] Add estimated time remaining
- [ ] Support `.xml` sitemap parsing
- [ ] Cross-platform builds (macOS/Linux)

---

## 📜 License

MIT License. Use responsibly.

