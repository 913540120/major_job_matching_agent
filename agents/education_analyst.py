from tavily import TavilyClient
import os
import json
from openai import OpenAI

class EducationAnalyst:
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

        print("教育分析师已初始化，并配备Tavily搜索和OpenAI分析工具。")

    def run(self, major: str) -> dict:
        """
        使用Tavily搜索并使用LLM提取结构化数据来分析指定专业
        """
        print(f"正在使用Tavily分析专业：{major}...")
        query = f"curriculum, core courses, and required skills for a bachelor's degree in '{major}'"
        
        try:
            # 步骤 1: Tavily 搜索
            print("--> 正在连接Tavily API...")
            search_results = self.tavily_client.search(query=query, search_depth="advanced", max_results=5)
            context = "\n\n".join([result['content'] for result in search_results['results']])
            print("--> Tavily搜索完成。")

            # 步骤 2: OpenAI 提取
            print("--> 正在连接OpenAI API进行信息提取...")
            system_prompt = """
            You are an expert academic advisor. Your task is to extract structured information 
            about a university major from the provided text. From the context, please extract:
            1. A list of core course names or course codes.
            2. A list of key skills, which are the abilities, technologies, or tools a student is expected to learn (e.g., "programming in Python", "algorithm design", "database management", "machine learning").

            Respond ONLY with a valid JSON object in the following format:
            {
                "core_courses": ["course1", "course2", ...],
                "required_skills": ["skill1", "skill2", ...]
            }
            """
            
            response = self.openai_client.chat.completions.create(
                model="deepseek-ai/DeepSeek-R1",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Here is the context about the major '{major}':\n\n{context}"}
                ],
                response_format={"type": "json_object"}
            )
            
            extracted_data = json.loads(response.choices[0].message.content)
            print("--> OpenAI信息提取完成。")
            
            report = {
                "major_name": major,
                "analysis_source": "Tavily Search + OpenAI GPT-4o",
                **extracted_data
            }

        except Exception as e:
            print(f"--> 教育分析师在执行中出错: {e}")
            report = {
                "major_name": major,
                "error": "Failed during education analysis.",
                "details": str(e)
            }

        print(f"专业 {major} 分析完成。")
        return report
