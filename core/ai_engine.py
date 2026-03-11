import json
from openai import AsyncOpenAI

class IntelligenceEngine:
    # 替换为你实际使用的 base_url 和 model
    def __init__(self, api_key, base_url="https://api.deepseek.com/v1"):
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model = "deepseek-chat" 

    def build_prompt(self, repo_info):
        return f"""
        你是一个专业的网络安全威胁情报（CTI）分析师。
        请分析以下从 GitHub 抓取的项目信息，判断其是否为真实的威胁情报或安全工具，并提取关键信息。
        
        **分析规则：**
        1. 严格过滤掉任何与加密货币(Crypto)、游戏外挂(Cheat/Bot/Farm)、空投(Airdrop)相关的垃圾信息，将其标记为 "is_spam": true。
        2. 如果是真实的漏洞 PoC、分析报告或安全工具，标记为 "is_spam": false。
        3. 尽可能提取出影响的组件和 CVE 编号。

        **输入数据：**
        标题: {repo_info['title']}
        描述: {repo_info['description']}

        **输出格式要求（必须是合法的 JSON，不要输出 Markdown 标记，不要输出解释）：**
        {{
            "is_spam": boolean,
            "category": "PoC" | "Tool" | "Report" | "Spam" | "Unknown",
            "cve_id": "CVE-XXXX-XXXX" 或 null,
            "affected_component": "组件名称" 或 null,
            "summary_zh": "用一句简短的中文概括这个项目的作用"
        }}
        """

    async def analyze(self, repo_info):
        prompt = self.build_prompt(repo_info)
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1, # 低温度保证 JSON 输出格式稳定
                response_format={"type": "json_object"} # 强制输出 JSON
            )
            # 解析大模型返回的 JSON 字符串
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            print(f"[!] AI Engine Error parsing {repo_info['title']}: {e}")
            return None
