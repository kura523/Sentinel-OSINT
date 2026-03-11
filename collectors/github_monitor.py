import httpx
import asyncio
import redis.asyncio as redis # 使用异步 Redis 库

class GitHubCollector:
    def __init__(self, redis_client):
        self.name = "GitHub_CVE_Monitor"
        self.api_url = "https://api.github.com/search/repositories"
        self.redis = redis_client
        # 关键词可以根据你的需求扩展
        self.keywords = ["CVE-2026", "Exploit", "vulnerability scan"]
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            # 如果有 Token，建议加上以提高频率限制: "Authorization": "token YOUR_GITHUB_TOKEN"
        }

    async def fetch(self, keyword):
        params = {
            "q": keyword,
            "sort": "updated",
            "order": "desc",
            "per_page": 5
        }
        async with httpx.AsyncClient(headers=self.headers, follow_redirects=True) as client:
            try:
                resp = await client.get(self.api_url, params=params, timeout=10)
                if resp.status_code == 200:
                    return resp.json().get('items', [])
                else:
                    print(f"[!] GitHub API Error: {resp.status_code}")
                    return []
            except Exception as e:
                print(f"[!] Request Exception: {e}")
                return []

    async def is_new(self, repo_id):
        """利用 Redis 集合判断是否为新发现的情报"""
        # 如果 id 不在集合中，说明是新的
        is_member = await self.redis.sismember("sentinel:seen_ids", str(repo_id))
        return not is_member

    async def run(self):
        all_new_intelligence = []
        for kw in self.keywords:
            print(f"[*] Searching GitHub for: {kw}")
            repos = await self.fetch(kw)
            
            for repo in repos:
                repo_id = repo['id']
                if await self.is_new(repo_id):
                    # 提取核心字段，供后续 AI 处理
                    intel = {
                        "source": "GitHub",
                        "title": repo['name'],
                        "description": repo['description'],
                        "url": repo['html_url'],
                        "stars": repo['stargazers_count'],
                        "updated_at": repo['updated_at']
                    }
                    all_new_intelligence.append(intel)
                    # 标记为已看过
                    await self.redis.sadd("sentinel:seen_ids", str(repo_id))
        
        return all_new_intelligence
