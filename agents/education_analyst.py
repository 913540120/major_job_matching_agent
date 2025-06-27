from tavily import TavilyClient
import os
import json
from openai import OpenAI
from typing import List

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

    def run(self, major: str, questions: List[str] = None) -> dict:
        """
        使用Tavily搜索并使用LLM提取结构化数据来分析指定专业
        可以额外接收一个问题列表，以在分析中获得更具针对性的答案
        """
        print(f"正在使用Tavily分析专业：{major}...")
        
        # 搜索查询保持简洁
        query = f"core curriculum, key skills, and technologies for a '{major}' undergraduate degree"
        
        try:
            # 步骤 1: Tavily 搜索
            print("--> 正在连接Tavily API进行深度搜索...")
            search_results = self.tavily_client.search(query=query, search_depth="advanced", max_results=5)
            context = "\n\n".join([r['content'] for r in search_results['results']])
            print("--> Tavily深度搜索完成。")

            # 步骤 2: OpenAI 提取 (使用更强大的Prompt)
            print("--> 正在连接OpenAI API进行信息提取...")
            system_prompt = """
            You are a helpful academic advisor and curriculum analyst. Your goal is to extract key courses and tangible skills from text about a university major.

            From the provided context, please extract the following:
            1.  **Core Courses**: A list of important course names. Prefer full names if available.
            2.  **Key Skills**: A list of key skills, abilities, and technologies a student would learn.
                - Prioritize specific, technical skills (e.g., Python, Java, TensorFlow, Git).
                - Infer skills from course descriptions.
            """

            # 如果有额外问题，动态地加入到Prompt中
            if questions:
                questions_str = "\n".join(f"- {q}" for q in questions)
                system_prompt += f"""
                \n**Important**: While performing the analysis, you MUST specifically address and find answers for the following questions based on the text:
                {questions_str}
                Your extracted skills and courses should reflect the answers to these questions.
                """

            system_prompt += """
            \nRespond ONLY with a valid JSON object, ensuring the keys are "core_courses" and "required_skills".
            {
                "core_courses": ["Full Course Name 1", "CS 201", ...],
                "required_skills": ["Python", "Algorithm Design", "Teamwork", ...]
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
