from flask import Flask, request, make_response

app = Flask(__name__)

# Bare-bones HTML embedded directly
HTML_PAGE = """
<main>
    <h2>Demo 1: Request & Header Inspector</h2>
    <button onclick="getHello()">Send GET /hello</button>
    <br><br>
    <input type="text" id="email" placeholder="Email">
    <input type="password" id="password" placeholder="Password">
    <button onclick="postLogin()">Send POST /login</button>
</main>

<script>
    async function getHello() {
        const response = await fetch('/hello');
        const text = await response.text();
        console.log("GET /hello Response:", text);
    }

    async function postLogin() {
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        
        const response = await fetch('/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: email, password: password })
        });
        
        const data = await response.json();
        console.log("POST /login Response:", data);
    }
</script>
"""


@app.route("/")
def index():
    return HTML_PAGE


@app.route("/hello", methods=["GET"])
def hello():
    return "Hello from the server!"


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email", "Unknown")

    return {"message": f"Welcome, {email}!", "echoed_data": data}


@app.route("/theme-demo")
def theme_demo():
    # 1. Read the cookie (default to 'light' if not present)
    current_theme = request.cookies.get("theme", "light")

    # 2. Determine colors based on the cookie
    if current_theme == "dark":
        bg_color = "#222222"
        text_color = "#ffffff"
    else:
        bg_color = "#ffffff"
        text_color = "#000000"

    # 3. Bare-bones HTML with string interpolation
    html = f"""
    <main style="background-color: {bg_color}; color: {text_color}; height: 100vh; padding: 20px;">
        <h1>This is {current_theme} mode</h1>
        <button onclick="toggleTheme()">Toggle Theme</button>
        
        <script>
            async function toggleTheme() {{
                // Send a request to the server to change the cookie
                await fetch('/toggle-theme', {{ method: 'POST' }});
            }}
        </script>
    </main>
    """
    return html


@app.route("/toggle-theme", methods=["POST"])
def toggle_theme():
    # Check current theme and flip it
    current_theme = request.cookies.get("theme", "light")
    new_theme = "dark" if current_theme == "light" else "light"

    # Create the response object
    response = make_response({"status": "success", "new_theme": new_theme})

    # Instruct the browser to set the cookie
    response.set_cookie("theme", new_theme, max_age=2592000)  # 30 days

    return response


if __name__ == "__main__":
    app.run(debug=True, port=5000)
