from flask import Flask

app = Flask(__name__)

HTML_PAGE = """
<main>
    <div id="result">...</div>
    <button onclick="fetchHello()">Get Message</button>
    
    <select id="langDropdown">
        <option value="en">English</option>
        <option value="hi">Hindi</option>
        <option value="kn">Kannada</option>
    </select>

    <script>
        async function fetchHello() {
            const response = await fetch('http://127.0.0.1:5001/hello', {
                method: 'GET',
                credentials: 'include'
            });
            const text = await response.text();
            document.getElementById('result').innerText = text;
        }

        document.getElementById('langDropdown').addEventListener('change', async function(event) {
            await fetch('http://127.0.0.1:5001/set-language', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ lang: event.target.value })
            });
        });
    </script>
</main>
"""


@app.route("/")
def index():
    return HTML_PAGE


if __name__ == "__main__":
    app.run(port=5000, debug=True)
