import schedule
import time
import asyncio
from datetime import datetime

# 导入我们之前写好的核心功能
from main import main as run_crawler_and_ai
from core.reporter import DailyReporter

def daily_osint_job():
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n[{now_str}] 🚀 开始执行每日威胁情报狩猎任务...")
    
    # 第一步：启动并发爬虫与 AI 分析流水线
    print("\n>>> [1/2] 正在启动数据采集与 AI 降噪清洗...")
    try:
        # 因为 main 是异步函数，这里需要用 asyncio.run 来执行它
        asyncio.run(run_crawler_and_ai())
        print("<<< [1/2] 采集与分析落库完成！")
    except Exception as e:
        print(f"[!] 采集任务异常: {e}")
        return

    # 第二步：生成精美的 Markdown 日报
    print("\n>>> [2/2] 正在生成今日情报日报...")
    try:
        reporter = DailyReporter()
        reporter.generate_report()
        print("<<< [2/2] 日报生成完毕！")
    except Exception as e:
        print(f"[!] 日报生成异常: {e}")
        
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🎉 今日 OSINT 任务全部圆满结束！等待下一个周期的到来...\n")

def run_scheduler():
    print("=== Sentinel OSINT 自动调度中心已启动 ===")
    
    # 【生产环境配置】设定每天早上 08:00 准时执行（你可以根据作息修改）
    schedule.every().day.at("08:00").do(daily_osint_job)
    print("[*] 调度规则加载成功：每天 08:00 AM 自动触发狩猎。")

    # 【本地测试配置】为了让你现在就能立刻看到效果，可以取消下面这行的注释
    # 让它现在立刻跑一次，或者设置为每隔 2 分钟跑一次测试：
    # schedule.every(2).minutes.do(daily_osint_job)

    # 保持进程一直活着的死循环
    while True:
        schedule.run_pending()
        time.sleep(1) # 睡1秒防止 CPU 占用过高

if __name__ == "__main__":
    try:
        run_scheduler()
    except KeyboardInterrupt:
        print("\n[!] 调度中心已手动退出。")
