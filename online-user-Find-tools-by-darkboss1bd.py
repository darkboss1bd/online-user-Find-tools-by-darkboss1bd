from flask import Flask, request, render_template
import logging
import json
from concurrent.futures import ThreadPoolExecutor
import requests
import random

# Logger configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# 🔑 Your contact info — auto-injected into all templates
TELEGRAM_ID = "https://t.me/darkvaiadmin"
WEBSITE_URL = "https://serialkey.top/"

class OSINTTool:
    def __init__(self, username):
        self.username = username
        self.results = {}
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.social_platforms = {
            "GitHub": f"https://api.github.com/users/{self.username}",
            "Instagram": f"https://www.instagram.com/{self.username}/",
            "X": f"https://x.com/{self.username}",
            "LinkedIn": f"https://www.linkedin.com/in/{self.username}/",
            "Medium": f"https://medium.com/@{self.username}",
            "Reddit": f"https://www.reddit.com/user/{self.username}",
            "TikTok": f"https://www.tiktok.com/@{self.username}",
            "Pinterest": f"https://www.pinterest.com/{self.username}",
            "Twitch": f"https://www.twitch.tv/{self.username}",
            "DeviantArt": f"https://www.deviantart.com/{self.username}",
            "Behance": f"https://www.behance.net/{self.username}",
            "Steam": f"https://steamcommunity.com/id/{self.username}",
            "Spotify": f"https://open.spotify.com/user/{self.username}",
            "SoundCloud": f"https://soundcloud.com/{self.username}",
            "Vimeo": f"https://vimeo.com/{self.username}",
            "YouTube": f"https://www.youtube.com/@{self.username}",
            "Telegram": f"https://t.me/{self.username}"
        }

    def validate_profile(self, platform, url):
        """Validate social media profiles using HTTP requests."""
        try:
            logging.info(f"Checking {platform}: {url}")
            response = requests.get(url, headers=self.headers, timeout=10)
            logging.info(f"[{platform}] Response status code: {response.status_code}")

            if response.status_code == 200:
                if platform == "GitHub":
                    data = response.json()
                    self.results[platform] = {
                        "exists": True,
                        "name": data.get("name"),
                        "bio": data.get("bio"),
                        "public_repos": data.get("public_repos"),
                        "followers": data.get("followers"),
                        "following": data.get("following"),
                        "profile_url": data.get("html_url")
                    }
                else:
                    page_content = response.text
                    # Detect "Not Found" pages for LinkedIn, TikTok, etc.
                    not_found_phrases = [
                        "we can’t seem to find the page",
                        "Die gewünschte Seite konnte leider nicht gefunden werden",
                        "Vaya, parece que no podemos encontrar",
                        "Maaf, sepertinya kami tidak dapat menemukan",
                        "Non abbiamo trovato la pagina",
                        "원하시는 페이지를 찾을 수 없습니다",
                        "De pagina waar u naar op zoek bent, kan niet worden gevonden",
                        "Не удаётся найти искомую вами страницу",
                        "Naku, mukhang hindi namin mahanap",
                        "discontinued operating TikTok in Hong Kong"
                    ]
                    if any(phrase in page_content for phrase in not_found_phrases):
                        self.results[platform] = {"exists": False}
                        logging.warning(f"[-] {platform} profile not found (content-based detection): {url}")
                    else:
                        self.results[platform] = {"exists": True, "url": url}
                        logging.info(f"[+] {platform} profile found at {url}")
            else:
                self.results[platform] = {"exists": False}
                logging.warning(f"[-] {platform} profile not found: {url}")

        except Exception as e:
            logging.error(f"Error checking {platform}: {e}")
            self.results[platform] = {"exists": False}

    def run_checks(self):
        """Run all platform checks concurrently."""
        logging.info(f"Starting OSINT search for username: {self.username}")
        with ThreadPoolExecutor(max_workers=10) as executor:
            for platform, url in self.social_platforms.items():
                executor.submit(self.validate_profile, platform, url)
        logging.info(f"Final results: {json.dumps(self.results, indent=4)}")


@app.route('/')
def index():
    """Render homepage with contact info."""
    return render_template('index.html', telegram=TELEGRAM_ID, website=WEBSITE_URL)


@app.route('/osint', methods=['POST'])
def osint_search():
    """Handle form submission and run OSINT tool."""
    username = request.form.get('username')
    if not username:
        return render_template(
            'index.html',
            error="Username is required.",
            telegram=TELEGRAM_ID,
            website=WEBSITE_URL
        )

    osint_tool = OSINTTool(username)
    osint_tool.run_checks()
    results = osint_tool.results
    logging.info(f"Results sent to template: {json.dumps(results, indent=4)}")

    return render_template(
        'results.html',
        username=username,
        results=results,
        telegram=TELEGRAM_ID,
        website=WEBSITE_URL
    )


if __name__ == '__main__':
    # Auto-select random port on each run
    port = random.randint(5000, 9999)
    print(f"🚀 Server starting on RANDOM PORT: {port}")
    print(f"📬 Contact me on Telegram: {TELEGRAM_ID}")
    print(f"🌐 Visit my website: {WEBSITE_URL}")
    app.run(debug=False, host='0.0.0.0', port=port)
