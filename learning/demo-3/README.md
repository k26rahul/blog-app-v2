# Demo 3: Analytics, Cross-Site Tracking & Affiliate Marketing

This repository demonstrates the mechanics of web tracking, personalized recommendations, and targeted advertising using two distinct web applications: a **Shopping App** and a **Lifestyle Blog**.

By running these applications on different hostnames (`127.0.0.1` vs. `localhost`), we simulate a real-world third-party tracking environment to observe how user data is collected, shared, and monetized across the internet.

---

## Part 1: The Shopping App (`http://127.0.0.1:5000`)

A simulated e-commerce platform (similar to Amazon or Flipkart) that meticulously tracks user behavior to provide personalized experiences and aggregate business analytics.

### Core Mechanics

- **Why Track Users?** Real-world e-commerce platforms track navigation to understand inventory performance, calculate conversion rates, and push targeted recommendations that drive higher sales.
- **The Tracking UUID:** When a user first lands on the site, the server generates a UUID (Universally Unique Identifier). This UUID is stored in the database as a new `Visitor` and placed in the user's browser via a `Set-Cookie` header.
- **Logging Visits:** Every subsequent page load sends the cookie back. A `@before_request` interceptor logs the exact URL, page type, and product ID to a `Visit` table, tying the action to the user's UUID.
- **Recommendation Engine:** The homepage queries the user's personal `Visit` history and dynamically renders a "Recently Viewed" section.
- **Cart State:** Because HTTP is stateless, the shopping cart relies entirely on the tracking UUID to remember which unauthenticated user added which items.

### Application Routes

- **`GET /`** : Homepage displaying global recommendations and store links.
- **`GET /store/<category>`** : Lists all products in a category, plus category-specific recommendations.
- **`GET /product/<id>/<slug>`** : Product details page with an "Add to Cart" form.
- **`POST /add_to_cart/<id>`** : Attaches a product to the user's UUID in the database.
- **`GET /cart`** : Displays the user's selected items and a mock checkout.
- **`GET /analytics`** : A static HTML/Vue.js admin dashboard.
- **`GET /api/analytics`** : Returns aggregated JSON statistics (Total visits, top products, active users) for the dashboard.
- **`GET /api/user_interests`** : A CORS-enabled API designed for third parties. It reads the tracking cookie and returns the user's shopping categories, sorted by most recently visited.

---

## Part 2: The Lifestyle App (`http://localhost:5001`)

A content-driven blog focusing on topics like fashion, tech, and health. This app demonstrates how content creators monetize traffic and utilize third-party cookies to show highly targeted content.

### Core Mechanics

- **The Business Model (Affiliate Marketing):** The Lifestyle blog generates revenue through brand collaborations. Articles seamlessly endorse specific products. When a reader clicks the link and makes a purchase, the blog earns a commission.
- **Affiliate Links:** The endorsement links point to the Shopping App but include a specific query parameter (e.g., `?affiliation_id=lifestyle_blog`). In a real system, the e-commerce backend reads this parameter to attribute the sale to the blogger and issue their payout.
- **Cross-Site Tracking (Third-Party Cookies):** Because the Shopping App set its tracking cookie with `SameSite=None; Secure`, it instructed the browser to allow that cookie to travel across different domains.
- When a user visits the Lifestyle App (`localhost`), a background JavaScript `fetch` request is made to the Shopping App's API (`127.0.0.1`).
- The browser automatically attaches the user's Shopping App cookie to this cross-origin request.

- **Targeted Advertising:** The Shopping App calculates the user's shopping categories (sorted by recency) based on the cookie, and returns that data to the Lifestyle App. The Lifestyle App instantly re-filters its article database to show a personalized "For You" section - up to 2 articles per category, 5 articles total - with the most recently visited categories prioritised.

### Application Routes

- **`GET /`** : The blog homepage. Executes the cross-site API fetch to render the targeted "For You" section above the standard article feed.
- **`GET /post/<slug>`** : The article reading page. Displays the content, tags, and the sponsored affiliate link to the Shopping App.

---

## How to Run the Demo

**Note:** You must use different hostnames in your browser to trigger the cross-site cookie behavior.

1. **Start the Shopping App:**

```bash
cd shopping-app
python app.py

```

_Access via:_ `http://127.0.0.1:5000` (Browse heavily to generate tracking data).

2. **Start the Lifestyle App:**

```bash
cd lifestyle-app
python app.py

```

_Access via:_ `http://localhost:5001` (Observe the personalized article recommendations based on your actions in the Shopping App).
