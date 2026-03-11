import asyncio
import redis.asyncio as redis
from collectors.github_monitor import GitHubCollector
from collectors.rss_monitor import RSSCollector  # 导入 RSS 采集器
from core.ai_engine import IntelligenceEngine
from core.database import DatabaseManager

API_KEY = "sk-aa81925cd9b340e79ee322130fed81da"

async def main():
    r_client = redis.from_url("redis://localhost", decode_responses=True)
    db = DatabaseManager()
    ai_engine = IntelligenceEngine(api_key=API_KEY)
    
    # 实例化所有采集器
    github_monitor = GitHubCollector(r_client)
    rss_monitor = RSSCollector(r_client)
    
    print("=== Sentinel OSINT Hunter Engine Started ===")
    
    # 使用 asyncio.gather 并发运行所有采集器
    print("[*] Launching all collectors concurrently...")
    results_list = await asyncio.gather(
        github_monitor.run(),
        rss_monitor.run()
    )
    
    # 将多个列表合并为一个平铺的列表
    all_results = [item for sublist in results_list for item in sublist]
    
    if not all_results:
        print("[i] No new intelligence found in this turn.")
    else:
        print(f"\n[*] Found {len(all_results)} new items. Sending to AI Engine for analysis...\n")
        
        for item in all_results:
            print(f"[-] Analyzing [{item['source']}]: {item['title']}...")
            ai_result = await ai_engine.analyze(item)
            
            if not ai_result:
                continue
                
            if ai_result.get("is_spam"):
                print(f"   [🗑️ Filtered Spam] {item['title']}")
            else:
                print(f"   [🔥 Threat Intel] {ai_result.get('summary_zh')}")
                # 存入数据库
                db.insert_intel(ai_result, item['url'])
                print("   [💾 Saved to Database]\n")

    await r_client.aclose()
    db.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
