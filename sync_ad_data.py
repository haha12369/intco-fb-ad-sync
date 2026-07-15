import requests
import os

# 读取仓库永久密钥，无需手动维护短期token
worker_url = os.getenv("FB_WORKER_URL")
fb_token = os.getenv("FB_ACCESS_TOKEN")
app_id = os.getenv("FEISHU_APP_ID")
app_secret = os.getenv("FEISHU_APP_SECRET")
feishu_app_token = os.getenv("FEISHU_APP_TOKEN")
feishu_table_id = os.getenv("FEISHU_TABLE_ID")

# 内置函数：每次运行自动申请全新有效飞书鉴权token，解决2小时过期问题
def get_feishu_token():
    auth_url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    resp = requests.post(auth_url, json={
        "app_id": app_id,
        "app_secret": app_secret
    })
    result = resp.json()
    if result["code"] != 0:
        raise Exception(f"获取飞书鉴权失败，返回信息：{result}")
    return result["tenant_access_token"]

# 第一步：通过Cloudflare代理拉取Meta近30天广告数据
meta_params = {
    "level": "campaign",
    "date_preset": "last_30d",
    "fields": "campaign_id,campaign_name,impressions,inline_link_clicks,spend,ctr,cpc,actions,date_start,date_stop",
    "limit": 100,
    "access_token": fb_token
}
meta_resp = requests.get(worker_url, params=meta_params, timeout=30)
meta_resp.raise_for_status()
ad_list = meta_resp.json()["data"]
print(f"成功拉取广告数据，总条数：{len(ad_list)}")

# 第二步：自动刷新飞书token，写入多维表格
valid_token = get_feishu_token()
write_api = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{feishu_app_token}/tables/{feishu_table_id}/records/batch_create"
headers = {
    "Authorization": f"Bearer {valid_token}",
    "Content-Type": "application/json"
}

# 循环逐条写入表格
for ad_item in ad_list:
    req_body = {
        "records": [
            {
                "fields": {
                    "广告系列ID": ad_item["campaign_id"],
                    "广告系列名称": ad_item["campaign_name"],
                    "曝光量": int(ad_item["impressions"]),
                    "链接点击量": int(ad_item["inline_link_clicks"]),
                    "花费": float(ad_item["spend"]),
                    "CTR": float(ad_item["ctr"]),
                    "CPC": float(ad_item["cpc"]),
                    "数据起始日": ad_item["date_start"],
                    "数据结束日": ad_item["date_stop"]
                }
            }
        ]
    }
    requests.post(write_api, json=req_body, headers=headers)

print("🎉 全部广告数据已同步写入飞书多维表格，执行完成！")
