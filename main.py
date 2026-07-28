import os
import sys
import json
import urllib.parse
import urllib.request

# 获取环境变量或命令行参数
CLIENT_ID = os.getenv("CLIENT_ID") or (sys.argv[1] if len(sys.argv) > 1 else None)
CLIENT_SECRET = os.getenv("CLIENT_SECRET") or (sys.argv[2] if len(sys.argv) > 2 else None)
TENANT_ID = os.getenv("TENANT_ID") or (sys.argv[3] if len(sys.argv) > 3 else None)

if not all([CLIENT_ID, CLIENT_SECRET, TENANT_ID]):
    print("❌ 错误：缺少 CLIENT_ID, CLIENT_SECRET 或 TENANT_ID 参数！")
    sys.exit(1)

# 1. 获取 Access Token
token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
token_data = urllib.parse.urlencode({
    'grant_type': 'client_credentials',
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'scope': 'https://graph.microsoft.com/.default'
}).encode('utf-8')

req = urllib.request.Request(token_url, data=token_data, method='POST')

try:
    with urllib.request.urlopen(req) as response:
        res = json.loads(response.read().decode('utf-8'))
        access_token = res.get('access_token')
        print("✅ 成功获取 Access Token！")
except Exception as e:
    print(f"❌ 获取 Token 失败: {e}")
    sys.exit(1)

# 2. 轮询调用多个 API 接口实现真实活跃
endpoints = [
    "https://graph.microsoft.com/v1.0/users",
    "https://graph.microsoft.com/v1.0/applications",
    "https://graph.microsoft.com/v1.0/organization",
    "https://graph.microsoft.com/v1.0/subscribedSkus",
    "https://graph.microsoft.com/v1.0/domains"
]

headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

success_count = 0
for url in endpoints:
    try:
        api_req = urllib.request.Request(url, headers=headers, method='GET')
        with urllib.request.urlopen(api_req) as api_res:
            if api_res.status == 200:
                print(f"✅ 接口调用成功: {url}")
                success_count += 1
    except Exception as e:
        print(f"⚠️ 接口调用异常 ({url}): {e}")

if success_count > 0:
    print(f"\n🎉 保活任务执行成功！共顺利调取 {success_count}/{len(endpoints)} 个 Microsoft Graph 接口。")
else:
    print("\n❌ 所有接口调用失败，请检查 Azure 端是否赋予了对应的 API 权限。")
    sys.exit(1)
