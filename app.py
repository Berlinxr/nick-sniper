import os
import time
from flask import Flask, render_template, request
import requests

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

TOKEN = "USER_TOKEN"

DISCORD_API = "https://discord.com/api/v9/users/@me/pomelo-attempt"

HEADERS = {
    "Authorization": TOKEN,
    "Content-Type": "application/json"
}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/checkfile", methods=["POST"])
def check_file():
    if "file" not in request.files:
        return render_template("index.html", result="Dosya yüklenmedi.")

    file = request.files["file"]

    if file.filename == "" or not file.filename.endswith(".txt"):
        return render_template("index.html", result="Sadece .txt uzantılı dosya yüklenebilir.")

    usernames = file.read().decode("utf-8").splitlines()
    results = []

    for i, username in enumerate(usernames):
        username = username.strip()
        if not username:
            continue

        try:
            res = requests.post(DISCORD_API, headers=HEADERS, json={"username": username})
            data = res.json()

            if res.status_code == 429:
                retry = data.get("retry_after", 5)
                results.append(f"<span style='color:orange'>⏳ Rate limit yedik, {retry}s bekliyoruz...</span>")
                time.sleep(retry)

            if "taken" in data:
                if not data["taken"]:
                    results.append(f"<span style='color:lime'>✅ {username} kullanılabilir</span>")
                else:
                    results.append(f"<span style='color:red'>❌ {username} alınmış</span>")
            else:
                results.append(f"<span style='color:orange'>⚠️ {username}: {data.get('message', 'Bilinmeyen hata')}</span>")

        except Exception as e:
            results.append(f"<span style='color:red'>❌ {username}: {str(e)}</span>")

        time.sleep(2) 

    return render_template("index.html", result="<br>".join(results))


if __name__ == "__main__":
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
