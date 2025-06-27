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
        
        # 升级的搜索查询
        query1 = f"core curriculum and course descriptions for a '{major}' undergraduate degree"
        query2 = f"key skills and technologies learned by a '{major}' graduate"
        
        try:
            # 步骤 1: Tavily 搜索 (合并两次搜索结果)
            print("--> 正在连接Tavily API进行深度搜索...")
            search_results1 = self.tavily_client.search(query=query1, search_depth="advanced", max_results=3)
            search_results2 = self.tavily_client.search(query=query2, search_depth="advanced", max_results=3)
            
            context = "\n\n---Course Information---\n" + "\n\n".join([r['content'] for r in search_results1['results']])
            context += "\n\n---Skills Information---\n" + "\n\n".join([r['content'] for r in search_results2['results']])
            print("--> Tavily深度搜索完成。")

            # 步骤 2: OpenAI 提取 (使用更强大的Prompt)
            print("--> 正在连接OpenAI API进行信息提取...")
            system_prompt = """
            You are an expert academic advisor. Your task is to extract structured information about a university major from the provided text, which is a mix of course descriptions and skill discussions.
            
            From the context, please perform the following:
            1.  Extract a list of core course names.
            2.  **Infer and list the key skills**. Skills are abilities, technologies, or tools a student is expected to learn. You should infer them from both the course descriptions and explicit skill mentions (e.g., a "Data Structures" course implies "algorithm design" as a skill).

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
