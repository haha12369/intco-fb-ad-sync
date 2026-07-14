import requests
import os

# 读取GitHub加密密钥
worker_url = os.getenv("FB_WORKER_URL")
fb_token = os.getenv("FB_ACCESS_TOKEN")
feishu_token = os.getenv("FEISHU_TENANT_TOKEN")
app_token = os.getenv("FEISHU_APP_TOKEN")
table_id = os.getenv("FEISHU_TABLE_ID")

# Meta广告接口请求参数
params = {
    "level": "campaign",
    "date_preset": "last_30d",
    "fields": "campaign_id,campaign_name,impressions,inline_link_clicks,spend,ctr,cpc,actions,date_start,date_stop",
    "limit": 100,
    "access_token": fb_token
}

# 1. 请求Cloudflare代理拉取广告数据
resp = requests.get(worker_url, params=params)
resp.raise_for_status()
ad_data_list = resp.json()["data"]

# 2. 飞书批量新增记录接口
feishu_write_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_create"
headers = {
    "Authorization": f"Bearer {feishu_token}",
    "Content-Type": "application/json"
}

# 循环写入每一条广告数据
for ad in ad_data_list:
    post_body = {
        "records": [
            {
                "fields": {
                    "广告系列ID": ad["campaign_id"],
                    "广告系列名称": ad["campaign_name"],
                    "曝光量": int(ad["impressions"]),
                    "链接点击量": int(ad["inline_link_clicks"]),
                    "花费": float(ad["spend"]),
                    "CTR": float(ad["ctr"]),
                    "CPC": float(ad["cpc"]),
                    "数据起始日": ad["date_start"],
                    "数据结束日": ad["date_stop"]
                }
            }
        ]
    }
    requests.post(feishu_write_url, json=post_body, headers=headers)

print(f"同步完成，共同步 {len(ad_data_list)} 条广告数据")
