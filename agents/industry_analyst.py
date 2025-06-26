from tavily import TavilyClient
import os

class IndustryAnalyst:
    def __init__(self, composio_api_key: str):
        self.composio_api_key = composio_api_key
        tavily_api_key = os.getenv("TAVILY_API_KEY")
        if not tavily_api_key:
            raise ValueError("TAVILY_API_KEY not found in environment variables.")
        self.tavily_client = TavilyClient(api_key=tavily_api_key)
        print("行业分析师已初始化，并配备Tavily搜索工具。")

    def run(self, job: str) -> dict:
        """
        分析目标岗位的市场需求和技能要求
        """
        print(f"正在使用Tavily分析岗位：{job}...")

        # 使用Tavily进行搜索
        query = f"'{job}' job description, required skills, and responsibilities"
        try:
            search_results = self.tavily_client.search(query=query, search_depth="advanced", max_results=5)
            
            # 目前，我们只返回原始搜索结果以便观察
            report = {
                "job_title": job,
                "analysis_source": "Tavily Search",
                "raw_search_results": search_results
            }
        except Exception as e:
            print(f"Tavily搜索失败: {e}")
            report = {
                "job_title": job,
                "error": "Tavily search failed.",
                "details": str(e)
            }

        print(f"岗位 {job} 分析完成。")
        return report
