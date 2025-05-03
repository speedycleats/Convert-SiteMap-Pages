import requests
from bs4 import BeautifulSoup
import os
import re
import sys
import multiprocessing
from functools import partial
from datetime import datetime
import ctypes

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
# Purpose : Checks if a URL is properly formatted and reachable
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
# Purpose : Scrapes a page and formats content using Markdown
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
        f"\n---\n### 🧭 URL: [{url}]({url})",
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
# Purpose : Windows-native message box on completion
# -----------------------------------------------------------------------------
def show_popup(title, message):
    MB_OK = 0x0
    ctypes.windll.user32.MessageBoxW(0, message, title, MB_OK)

# -----------------------------------------------------------------------------
# Function: main
# Purpose : Orchestrates validation, scraping, logging, and output writing
# -----------------------------------------------------------------------------
def main(input_txt, processes=6):
    # Terminal color codes for Windows PowerShell
    GREEN = '\033[92m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'

    if not os.path.exists(input_txt):
        print(f"{RED}❌ Input file not found: {input_txt}{RESET}")
        return

    with open(input_txt, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]

    base_name = os.path.splitext(os.path.basename(input_txt))[0]
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_txt = f"{base_name}-{timestamp}-full_text_output.txt"
    log_txt = f"{base_name}-{timestamp}-log.txt"

    log_lines = []
    valid_urls = []

    print(f"{CYAN}\n🔎 Validating {len(urls)} URLs...\n{RESET}")
    for url in urls:
        if is_valid_url(url, log_lines):
            valid_urls.append(url)

    print(f"{GREEN}\n✅ {len(valid_urls)} valid URLs found. Beginning scrape...\n{RESET}")
    if not valid_urls:
        log_lines.append(f"[{datetime.now()}] ❌ No valid URLs to process.")
        with open(log_txt, 'w', encoding='utf-8') as log_file:
            log_file.write('\n'.join(log_lines))
        print(f"{RED}❌ No valid URLs. Exiting.{RESET}")
        return

    with multiprocessing.Pool(processes=processes) as pool:
        extract_partial = partial(extract_text_by_tag, tags_to_extract=list(MARKDOWN_TAGS.keys()))
        results = pool.map(extract_partial, valid_urls)

    summary_lines = [
        "## 🧾 Summary Report\n",
        f"- 📅 Run date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- 📄 Input file: {os.path.basename(input_txt)}",
        f"- 🔗 Total URLs scanned: {len(urls)}",
        f"- ✅ Pages successfully scraped: {len(valid_urls)}",
        f"- ❌ Pages skipped or failed: {len(urls) - len(valid_urls)}",
        "\n---\n"
    ]

    with open(output_txt, 'w', encoding='utf-8') as f:
        f.write('\n'.join(summary_lines) + '\n\n' + '\n\n'.join(results))

    log_lines.append(f"[{datetime.now()}] ✅ Scraping complete. Output saved to {output_txt}")
    with open(log_txt, 'w', encoding='utf-8') as log_file:
        log_file.write('\n'.join(log_lines))

    # -----------------------------------------------------------------------------
    # Section: Final Output and User Notification
    # Purpose : Print full file paths, open them, and display a popup summary
    # -----------------------------------------------------------------------------
    output_full_path = os.path.abspath(output_txt)
    log_full_path = os.path.abspath(log_txt)
    folder_path = os.path.dirname(output_full_path)

    print(f"{GREEN}\n📄 Done! Output saved to: {output_full_path}{RESET}")
    print(f"{CYAN}🧾 Log saved to: {log_full_path}{RESET}")
    print(f"{YELLOW}📁 Output folder: {folder_path}{RESET}")
    print(f"\n📋 You can copy the above path to access files manually.\n")

    try:
        os.system(f'start "" "{output_full_path}"')
        os.system(f'start "" "{log_full_path}"')
    except Exception as e:
        print(f"{YELLOW}⚠️ Could not open files automatically: {e}{RESET}")

    popup_message = (
        "✅ Scraping Complete\n\n"
        f"📄 Output file:\n{output_full_path}\n\n"
        f"🧾 Log file:\n{log_full_path}\n\n"
        f"📁 Folder:\n{folder_path}\n\n"
        "You can right-click this message and press Ctrl+C to copy."
    )

    show_popup("✅ Scraping Complete", popup_message)


# -----------------------------------------------------------------------------
# Execution Entry Point
# Purpose : Allows drag-and-drop execution or manual prompting
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = input("Enter path to .txt file with sitemap URLs:\n> ").strip()

    main(input_file)
