import requests
import os

# 仅读取2个必须密钥
worker_url = os.getenv("FB_WORKER_URL")
fb_token = os.getenv("FB_ACCESS_TOKEN")

# Meta广告接口请求参数
params = {
    "level": "campaign",
    "date_preset": "last_30d",
    "fields": "campaign_id,campaign_name,impressions,inline_link_clicks,spend,ctr,cpc,actions,date_start,date_stop",
    "limit": 100,
    "access_token": fb_token
}

# 请求Cloudflare代理拉取广告数据
try:
    resp = requests.get(worker_url, params=params, timeout=30)
    resp.raise_for_status()
    ad_data_list = resp.json()["data"]
    print(f"✅ Meta广告数据拉取成功，共获取 {len(ad_data_list)} 条广告数据")
except Exception as e:
    print(f"❌ 拉取广告数据失败：{str(e)}")
    exit(1)
