from flask import Flask, render_template_string, request, redirect
import requests

app = Flask(__name__)
cached_titles = []

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>新浪快讯</title></head>
<body>
<h2>新浪财经快讯</h2>
<form method="get" action="/">
  <input type="text" name="q" placeholder="关键词过滤" value="{{ keyword }}">
  <button>搜索</button>
</form>
<form method="post" action="/update"><button>更新</button></form>
<ul>
{% for title in filtered_titles %}
  <li>{{ title }}</li>
{% endfor %}
</ul>
</body>
</html>
"""

def fetch_titles():
    _pool = []
    _url = "http://zhibo.sina.com.cn/api/zhibo/feed?page={}&page_size=20&zhibo_id=152"
    for p in range(1, 10):
        resp = requests.get(_url.format(p), timeout=10)
        data = resp.json()
        _pool.extend([item["rich_text"].strip() for item in data["result"]["data"]["feed"]["list"]])
    return _pool

@app.route("/", methods=["GET"])
def index():
    keyword = request.args.get("q", "").strip()
    filtered_titles = [title for title in cached_titles if keyword.lower() in title.lower()] if keyword else cached_titles
    return render_template_string(HTML_TEMPLATE, filtered_titles=filtered_titles, keyword=keyword)

@app.route("/update", methods=["POST"])
def update():
    global cached_titles
    try:
        cached_titles = fetch_titles()
    except Exception as e:
        print("更新失败：", e)
    return redirect("/")

if __name__ == "__main__":
    cached_titles = fetch_titles()
    app.run(debug=True)
