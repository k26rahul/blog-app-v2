from flask import Flask, request, make_response, jsonify

app = Flask(__name__)

CLIENT_ORIGIN = "http://127.0.0.1:5000"


def apply_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = CLIENT_ORIGIN
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    # response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    return response


@app.route("/hello", methods=["GET", "OPTIONS"])
def hello():
    if request.method == "OPTIONS":
        return apply_cors_headers(make_response())

    lang = request.cookies.get("lang", "en")
    messages = {"en": "Hello", "hi": "नमस्ते", "kn": "ನಮಸ್ಕಾರ"}

    response = make_response(messages.get(lang, "Hello"))
    return apply_cors_headers(response)


@app.route("/set-language", methods=["POST", "OPTIONS"])
def set_language():
    if request.method == "OPTIONS":
        return apply_cors_headers(make_response())

    data = request.get_json()
    lang = data.get("lang", "en")

    response = make_response(jsonify({"status": "success", "new_lang": lang}))
    response.set_cookie("lang", lang, samesite="None", secure=True, httponly=True)

    return apply_cors_headers(response)


if __name__ == "__main__":
    app.run(port=5001, debug=True)
