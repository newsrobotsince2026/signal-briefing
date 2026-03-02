import requests
import os
from datetime import datetime

SERVERCHAN_KEY = os.environ.get("SERVERCHAN_KEY", "")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "")

def get_url(repo):
    if "/" not in repo:
        return "https://newsrobotsince2026.github.io/signal-briefing/"
    username, reponame = repo.split("/", 1)
    return "https://" + username + ".github.io/" + reponame + "/"

def send_wechat(title, content):
    if not SERVERCHAN_KEY:
        print("No SERVERCHAN_KEY — skipping.")
        return
    url = "https://sctapi.ftqq.com/" + SERVERCHAN_KEY + ".send"
    resp = requests.post(url, data={"title": title, "desp": content}, timeout=15)
    result = resp.json()
    if result.get("code") == 0:
        print("WeChat notification sent!")
    else:
        print("WeChat failed: " + str(result))

if __name__ == "__main__":
    now = datetime.utcnow().strftime("%Y-%m-%d")
    link = get_url(GITHUB_REPO)
    title = "SIGNAL 每周情报简报已更新 " + now
    content = "本周简报已更新！\n\n点击查看：" + link + "\n\n本期涵盖：\n- 政治外交\n- 商业经济\n- 科技\n- 冲突安全\n\n自动生成于 " + now
    send_wechat(title, content)
