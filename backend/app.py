from flask import Flask, render_template
import requests
from bs4 import BeautifulSoup
from flask_cors import CORS
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
CORS(app)

SIGNS = {
    1: "Aries",
    2: "Taurus",
    3: "Gemini",
    4: "Cancer",
    5: "Leo",
    6: "Virgo",
    7: "Libra",
    8: "Scorpio",
    9: "Sagittarius",
    10: "Capricorn",
    11: "Aquarius",
    12: "Pisces"
}

def get_horoscope(sign):
    url = f"https://www.horoscope.com/us/horoscopes/general/horoscope-general-daily-today.aspx?sign={sign}"

    session = requests.Session()
    session.trust_env = False

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36"
        )
    }

    try:
        res = session.get(url, headers=headers, timeout=10)

        soup = BeautifulSoup(res.text, "html.parser")

        paragraph = soup.find("p")

        if paragraph:
            return paragraph.get_text(strip=True)

        return "No horoscope found."

    except Exception as e:
        return f"Error: {str(e)}"


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/horoscope")
def horoscope():
    horoscopes = []

    for sign_num, sign_name in SIGNS.items():
        text = get_horoscope(sign_num)

        horoscopes.append({
            "name": sign_name,
            "text": text
        })

    return render_template("horoscope.html", horoscopes=horoscopes)

# API ROUTE - ALL HOROSCOPES

@app.route("/api/horoscope")
def api_horoscope():

    with ThreadPoolExecutor(max_workers=12) as executor:

        results = list(
            executor.map(
                lambda sign: {
                    "id": sign[0],
                    "sign": sign[1],
                    "horoscope": get_horoscope(sign[0])
                },
                SIGNS.items()
            )
        )

    return jsonify({
        "success": True,
        "count": len(results),
        "data": results
    })


# API ROUTE - SINGLE SIGN

@app.route("/api/horoscope/<int:sign>")
def api_single_horoscope(sign):

    if sign not in SIGNS:

        return jsonify({
            "success": False,
            "error": "Invalid sign"
        }), 400

    result = {
        "id": sign,
        "sign": SIGNS[sign],
        "horoscope": get_horoscope(sign)
    }

    return jsonify({
        "success": True,
        "data": result
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
