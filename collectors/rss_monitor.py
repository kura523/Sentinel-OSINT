import httpx
import asyncio
import feedparser
import redis.asyncio as redis

class RSSCollector:
    def __init__(self, redis_client):
        self.name = "Security_RSS_Monitor"
        self.redis = redis_client
        # 高质量安全博客 RSS 订阅源
        self.feeds = [
            "https://www.bleepingcomputer.com/feed/",          # BleepingComputer (综合安全新闻)
            "https://feeds.feedburner.com/TheHackersNews",     # The Hacker News (漏洞与攻击事件)
            "https://googleprojectzero.blogspot.com/feeds/posts/default", # 谷歌 Project Zero (硬核漏洞分析)
            "https://unit42.paloaltonetworks.com/feed/"        # Palo Alto Unit 42 (APT与威胁情报)
        ]
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    async def fetch_and_parse(self, url):
        """异步获取 XML 内容并交给 feedparser 解析"""
        async with httpx.AsyncClient(headers=self.headers, follow_redirects=True) as client:
            try:
                resp = await client.get(url, timeout=15)
                if resp.status_code == 200:
                    # 使用 asyncio.to_thread 防止 feedparser 阻塞异步事件循环
                    feed = await asyncio.to_thread(feedparser.parse, resp.text)
                    return feed.entries
                else:
                    print(f"[!] RSS Fetch Error ({resp.status_code}): {url}")
                    return []
            except Exception as e:
                print(f"[!] RSS Request Exception on {url}: {e}")
                return []

    async def is_new(self, article_url):
        """利用 Redis 集合判断文章是否已处理过"""
        # RSS 的最佳唯一标识符通常是文章链接 (link)
        is_member = await self.redis.sismember("sentinel:seen_urls", article_url)
        return not is_member

    async def run(self):
        all_new_intelligence = []
        for feed_url in self.feeds:
            print(f"[*] Fetching RSS feed: {feed_url}")
            entries = await self.fetch_and_parse(feed_url)
            
            # 限制每个源每次只取最新的 5 篇文章，避免冷启动时数据爆炸
            for entry in entries[:5]:
                link = entry.get('link', '')
                if not link:
                    continue
                    
                if await self.is_new(link):
                    # 提取核心字段，清洗掉可能存在的 HTML 标签
                    # 有些 RSS 的描述在 summary 字段，有些在 description 字段
                    description = entry.get('summary', entry.get('description', ''))
                    
                    intel = {
                        "source": "RSS_Blog",
                        "title": entry.get('title', ''),
                        "description": description[:1000],  # 截取前 1000 字符喂给大模型足够了
                        "url": link,
                        "published_at": entry.get('published', '')
                    }
                    all_new_intelligence.append(intel)
                    # 标记为已看过
                    await self.redis.sadd("sentinel:seen_urls", link)
        
        return all_new_intelligence
