import requests
from bs4 import BeautifulSoup
import os
import re
import sys
from datetime import datetime
import ctypes
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Markdown-style formatting for common HTML tags
MARKDOWN_TAGS = {
    'title': '#',
    'h1': '#',
    'h2': '##',
    'h3': '###',
    'p': '',
    'li': '-'
}

# -----------------------------------------------------------------------------
# Function: is_valid_url
# Purpose : Validates if the provided URL is in proper format and reachable
# -----------------------------------------------------------------------------
def is_valid_url(url, log_lines):
    pattern = re.compile(r'^https?://.+')
    if not pattern.match(url):
        log_lines.append(f"[{datetime.now()}] ⛔ Invalid format: {url}")
        return False
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        if response.status_code >= 400:
            log_lines.append(f"[{datetime.now()}] 🚫 Unreachable ({response.status_code}): {url}")
            return False
    except requests.RequestException as e:
        log_lines.append(f"[{datetime.now()}] ⚠️ Exception: {url} | {str(e)}")
        return False
    log_lines.append(f"[{datetime.now()}] ✅ Valid: {url}")
    return True

# -----------------------------------------------------------------------------
# Function: extract_text_by_tag
# Purpose : Downloads and parses HTML content, formats selected tags into Markdown
# -----------------------------------------------------------------------------
def extract_text_by_tag(url, tags_to_extract):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        return f"\n---\n❌ **Error accessing {url}**: {str(e)}\n---\n"

    soup = BeautifulSoup(response.text, 'html.parser')
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output = [
        f"\n---\n### 🧽 URL: [{url}]({url})",
        f"🕒 Scraped at: {timestamp}\n"
    ]

    for tag in tags_to_extract:
        for element in soup.find_all(tag):
            text = element.get_text(strip=True)
            if text:
                prefix = MARKDOWN_TAGS.get(tag, '')
                output.append(f"{prefix} {text}" if prefix else text)

    output.append("\n---\n")
    return '\n'.join(output)

# -----------------------------------------------------------------------------
# Function: show_popup
# Purpose : Displays a Windows-native popup message box
# -----------------------------------------------------------------------------
def show_popup(title, message):
    MB_OK = 0x0
    ctypes.windll.user32.MessageBoxW(0, message, title, MB_OK)

# -----------------------------------------------------------------------------
# Function: select_output_directory
# Purpose : Opens GUI prompt for selecting the parent directory for output
# -----------------------------------------------------------------------------
def select_output_directory():
    root = tk.Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title="📁 Select Folder to Save Output Folder")
    root.destroy()
    return folder

# -----------------------------------------------------------------------------
# Function: select_input_file
# Purpose : Opens GUI prompt for selecting the input .txt file with sitemap URLs
# -----------------------------------------------------------------------------
def select_input_file():
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    file_path = filedialog.askopenfilename(
        title="📄 Select your sitemap .txt file",
        filetypes=[("Text Files", "*.txt")]
    )
    root.destroy()
    return file_path

# -----------------------------------------------------------------------------
# Function: update_progress
# Purpose : Updates progress bar GUI during scraping process
# -----------------------------------------------------------------------------
def update_progress(progress_var, progress_bar, current, total):
    progress = int((current / total) * 100)
    progress_var.set(progress)
    progress_bar.update()

# -----------------------------------------------------------------------------
# Function: main
# Purpose : Main controller that handles reading URLs, validation, scraping,
#           progress bar updates, file output, and final notification
# -----------------------------------------------------------------------------
def main(input_txt):
    log_lines = []
    valid_urls = []

    # Read URLs from the input file
    with open(input_txt, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]

    base_name = os.path.splitext(os.path.basename(input_txt))[0]
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    # Ask user to select output folder location
    output_root = select_output_directory()
    if not output_root:
        show_popup("❌ Cancelled", "No output folder selected. Exiting.")
        return

    # Create timestamped subfolder to store output
    final_output_dir = os.path.join(output_root, f"{timestamp}-{base_name}")
    os.makedirs(final_output_dir, exist_ok=True)

    output_txt = os.path.join(final_output_dir, f"{base_name}-full_text_output.txt")
    log_txt = os.path.join(final_output_dir, f"{base_name}-log.txt")

    # Initialize progress window
    root = tk.Tk()
    root.title("Scraping in Progress")
    tk.Label(root, text="Scraping URLs...").pack(pady=10)
    progress_var = tk.IntVar()
    progress_bar = ttk.Progressbar(root, length=300, variable=progress_var, maximum=100)
    progress_bar.pack(pady=20)
    root.update()

    # Validate URLs
    for i, url in enumerate(urls):
        if is_valid_url(url, log_lines):
            valid_urls.append(url)
        update_progress(progress_var, progress_bar, i+1, len(urls))

    # Exit if no valid URLs found
    if not valid_urls:
        log_lines.append(f"[{datetime.now()}] ❌ No valid URLs to process.")
        with open(log_txt, 'w', encoding='utf-8') as log_file:
            log_file.write('\n'.join(log_lines))
        show_popup("❌ No Valid URLs", "No valid URLs found. Exiting.")
        root.destroy()
        return

    # Scrape each valid URL
    results = []
    for i, url in enumerate(valid_urls):
        results.append(extract_text_by_tag(url, list(MARKDOWN_TAGS.keys())))
        update_progress(progress_var, progress_bar, i+1, len(valid_urls))

    # Generate and write summary report
    summary_lines = [
        "## 📟 Summary Report\n",
        f"- 📅 Run date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- 📄 Input file: {os.path.basename(input_txt)}",
        f"- 🔗 Total URLs scanned: {len(urls)}",
        f"- ✅ Pages successfully scraped: {len(valid_urls)}",
        f"- ❌ Pages skipped or failed: {len(urls) - len(valid_urls)}",
        "\n---\n"
    ]

    with open(output_txt, 'w', encoding='utf-8') as f:
        f.write('\n'.join(summary_lines) + '\n\n' + '\n\n'.join(results))

    # Save log file
    log_lines.append(f"[{datetime.now()}] ✅ Scraping complete. Output saved to {output_txt}")
    with open(log_txt, 'w', encoding='utf-8') as log_file:
        log_file.write('\n'.join(log_lines))

    # Close progress window and notify user
    root.destroy()
    show_popup("✅ Scraping Complete", f"Output folder:\n{final_output_dir}")

# -----------------------------------------------------------------------------
# Execution Entry Point
# Purpose : Starts the script via file selector and initiates main process
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    input_file = select_input_file()
    if not input_file:
        show_popup("❌ Cancelled", "No input file selected. Exiting.")
        sys.exit()
    main(input_file)
