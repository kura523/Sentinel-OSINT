import sqlite3
import os
from datetime import date
from jinja2 import Template

class DailyReporter:
    def __init__(self, db_path="sentinel.db", output_dir="reports"):
        self.db_path = db_path
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        # 定义 Markdown 模板
        self.template_str = """# 🛡️ Sentinel OSINT 威胁情报日报
**生成日期：** {{ today }}

---

## 🚨 今日高危漏洞 (PoC & CVE)
{% if pocs %}
{% for item in pocs %}
### 🔴 {{ item.cve_id or '未分配 CVE' }} - {{ item.component or '未知组件' }}
* **情报摘要**: {{ item.summary }}
* **原始来源**: [点击查看详情]({{ item.url }})
{% endfor %}
{% else %}
*今日暂未监控到新增的高危漏洞。*
{% endif %}

---

## 🛠️ 最新开源安全工具与报告
{% if tools %}
{% for item in tools %}
* **[{{ item.category }}]** {{ item.summary }}
  * 影响组件: {{ item.component or 'N/A' }}
  * 来源: {{ item.url }}
{% endfor %}
{% else %}
*今日暂无相关工具更新。*
{% endif %}

---
*本报告由 Sentinel OSINT 引擎自动生成。*
"""

    def get_todays_intel(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        today_str = date.today().strftime('%Y-%m-%d')
        
        # 获取今日所有情报
        cursor.execute('''
            SELECT cve_id, category, component, summary, url 
            FROM intelligence 
            WHERE discovered_at LIKE ?
        ''', (f'{today_str}%',))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    def generate_report(self):
        intel_list = self.get_todays_intel()
        
        # 分类数据
        pocs = [i for i in intel_list if i['category'] == 'PoC']
        tools = [i for i in intel_list if i['category'] in ['Tool', 'Report']]
        
        # 渲染模板
        template = Template(self.template_str)
        markdown_content = template.render(
            today=date.today().strftime('%Y年%m月%d日'),
            pocs=pocs,
            tools=tools
        )
        
        # 保存到文件
        filename = f"{self.output_dir}/Threat_Intel_Daily_{date.today().strftime('%Y%m%d')}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(markdown_content)
            
        print(f"[✔] 今日威胁情报日报已生成: {filename}")

if __name__ == "__main__":
    reporter = DailyReporter()
    reporter.generate_report()
