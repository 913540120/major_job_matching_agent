from tavily import TavilyClient
import os
import json
from openai import OpenAI

class IndustryAnalyst:
    def __init__(self, openai_api_key: str, composio_api_key: str):
        self.composio_api_key = composio_api_key
        
        # 初始化Tavily客户端
        tavily_api_key = os.getenv("TAVILY_API_KEY")
        if not tavily_api_key:
            raise ValueError("TAVILY_API_KEY not found in environment variables.")
        self.tavily_client = TavilyClient(api_key=tavily_api_key)

        # 初始化OpenAI客户端
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables.")
        self.openai_client = OpenAI(base_url='https://api.siliconflow.cn/v1',api_key=openai_api_key)
        
        print("行业分析师已初始化，并配备Tavily搜索和OpenAI分析工具。")

    def run(self, job: str) -> dict:
        """
        使用Tavily搜索并使用LLM提取结构化数据来分析目标岗位
        """
        print(f"正在使用Tavily分析岗位：{job}...")
        query = f"'{job}' job description, required skills, and responsibilities"
        
        # 步骤 1: Tavily 搜索
        try:
            print("--> 正在连接Tavily API...")
            search_results = self.tavily_client.search(query=query, search_depth="advanced", max_results=5)
            context = "\n\n".join([result['content'] for result in search_results['results']])
            print("--> Tavily搜索完成。")
        except Exception as e:
            print(f"--> Tavily搜索失败: {e}")
            return {
                "job_title": job,
                "error": "Failed during Tavily search.",
                "details": str(e)
            }

        # 步骤 2: OpenAI 提取
        try:
            print("--> 正在连接OpenAI API进行信息提取...")
            system_prompt = """
            You are an expert recruitment analyst. Your task is to extract structured information 
            from the provided text based on job search results.
            Please extract the required skills, main responsibilities, and an estimated salary range.
            Respond ONLY with a valid JSON object in the following format:
            {
                "required_skills": ["skill1", "skill2", ...],
                "responsibilities": ["responsibility1", "responsibility2", ...],
                "salary_range": "e.g., 15k-30k USD or Not Mentioned"
            }
            """
            
            response = self.openai_client.chat.completions.create(
                model="deepseek-ai/DeepSeek-R1",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Here is the context about the job '{job}':\n\n{context}"}
                ],
                response_format={"type": "json_object"}
            )
            
            extracted_data = json.loads(response.choices[0].message.content)
            print("--> OpenAI信息提取完成。")
            
            report = {
                "job_title": job,
                "analysis_source": "Tavily Search + OpenAI GPT-4o",
                **extracted_data
            }

        except Exception as e:
            print(f"--> OpenAI信息提取失败: {e}")
            return {
                "job_title": job,
                "error": "Failed during OpenAI information extraction.",
                "details": str(e)
            }

        print(f"岗位 {job} 分析完成。")
        return report
