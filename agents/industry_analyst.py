from tavily import TavilyClient
import os
import json
from openai import OpenAI
from typing import List

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

    def run(self, job: str, questions: List[str] = None) -> dict:
        """
        使用Tavily搜索并使用LLM提取结构化数据来分析目标岗位
        可以额外接收一个问题列表，以在分析中获得更具针对性的答案
        """
        print(f"正在使用Tavily分析岗位：{job}...")
        
        # 构建基础查询
        base_query = f"{job} 岗位要求 技能需求 薪资 职责"
        
        # 如果有批判者问题，添加相关关键词但要控制长度
        if questions:
            # 提取问题中的关键词，避免查询过长
            question_keywords = []
            for q in questions[:2]:  # 最多处理前2个问题
                # 提取关键词：技能、薪资、市场、发展等
                if "技能" in q or "skill" in q.lower():
                    question_keywords.append("技能要求")
                if "薪资" in q or "salary" in q.lower():
                    question_keywords.append("薪资待遇")
                if "市场" in q or "market" in q.lower():
                    question_keywords.append("市场需求")
                if "发展" in q or "career" in q.lower():
                    question_keywords.append("职业发展")
            
            if question_keywords:
                # 限制关键词数量，确保总查询长度不超过350字符
                keywords_str = " ".join(question_keywords[:3])
                extended_query = f"{base_query} {keywords_str}"
                
                # 如果仍然太长，就用基础查询
                if len(extended_query) <= 350:
                    query = extended_query
                else:
                    query = base_query
            else:
                query = base_query
        else:
            query = base_query

        # 步骤 1: Tavily 搜索 (带备用方案)
        try:
            print("--> 正在连接Tavily API...")
            print(f"--> 查询长度: {len(query)} 字符")
            print(f"--> 查询内容: {query}")
            
            tavily_response = self.tavily_client.search(
                query=query,
                search_depth="advanced",
                max_results=5
            )
            
            # 构建上下文
            context = ""
            for result in tavily_response['results']:
                context += f"来源: {result.get('url', 'Unknown')}\n"
                context += f"内容: {result.get('content', 'No content')}\n\n"
            
            print("--> Tavily搜索完成。")
            
        except Exception as e:
            print(f"--> Tavily搜索失败: {e}")
            print("--> 使用备用分析策略...")
            
            # 备用方案：基于岗位名称进行基本分析
            context = f"""
            基于岗位名称 '{job}' 的基本分析：
            
            这是一个{job}职位，通常需要以下技能和要求：
            - 相关专业技术技能
            - 编程和开发能力  
            - 分析和解决问题的能力
            - 团队协作能力
            - 持续学习能力
            
            注意：由于网络搜索暂时不可用，以下分析基于通用行业知识。
            """

        # 步骤 2: OpenAI 提取 (增强版Prompt)
        try:
            print("--> 正在连接OpenAI API进行信息提取...")
            print("--> 预计需要30-60秒，请耐心等待...")
            system_prompt = """
            You are an expert recruitment analyst and market researcher. Your task is to extract comprehensive 
            structured information from the provided text about a specific job role.
            
            From the provided context, please extract the following:
            1. **Required Skills**: Technical and soft skills needed for this role
            2. **Main Responsibilities**: Key job duties and expectations
            3. **Salary Range**: Compensation information if available
            4. **Market Trends**: Current industry demands and future outlook for this role
            5. **Career Growth**: Typical progression paths and opportunities
            """

            # 如果有额外问题，动态地加入到Prompt中
            if questions:
                questions_str = "\n".join(f"- {q}" for q in questions)
                print(f"--> 根据 {len(questions)} 个批判问题进行深度分析...")
                system_prompt += f"""
                \n**Important**: While performing the analysis, you MUST specifically address and find answers for the following questions based on the industry context:
                {questions_str}
                Your extracted information should reflect updated insights based on these questions.
                """

            system_prompt += """
            \nRespond ONLY with a valid JSON object in the following format:
            {
                "required_skills": ["skill1", "skill2", ...],
                "responsibilities": ["responsibility1", "responsibility2", ...],
                "salary_range": "e.g., 15k-30k USD or Not Mentioned",
                "market_trends": ["trend1", "trend2", ...],
                "career_growth": ["path1", "path2", ...]
            }
            
            CRITICAL: Ensure ALL fields are present and are arrays/strings as specified. Do not return nested objects or missing fields.
            """
            
            print("--> 发送请求到DeepSeek AI...")
            response = self.openai_client.chat.completions.create(
                model="deepseek-ai/DeepSeek-R1",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Here is the context about the job '{job}':\n\n{context}"}
                ],
                response_format={"type": "json_object"}
            )
            
            print("--> 正在解析AI响应...")
            # 安全的JSON解析
            response_content = response.choices[0].message.content
            print(f"--> 收到响应内容: {response_content[:200]}...")  # 打印前200字符用于调试
            
            try:
                extracted_data = json.loads(response_content)
                
                # 验证返回的数据结构
                if not isinstance(extracted_data, dict):
                    raise ValueError(f"期望字典格式，但收到: {type(extracted_data)}")
                
                # 确保必要字段存在，如果不存在则设置默认值
                required_fields = {
                    "required_skills": [],
                    "responsibilities": [],
                    "salary_range": "Not Mentioned",
                    "market_trends": [],
                    "career_growth": []
                }
                
                for field, default_value in required_fields.items():
                    if field not in extracted_data:
                        extracted_data[field] = default_value
                    elif not isinstance(extracted_data[field], (list, str)):
                        # 如果字段类型不正确，使用默认值
                        extracted_data[field] = default_value
                
                print("--> OpenAI信息提取完成。")
                
            except json.JSONDecodeError as e:
                print(f"--> JSON解析失败: {e}")
                # 返回默认结构
                extracted_data = {
                    "required_skills": ["信息提取失败，请重试"],
                    "responsibilities": ["信息提取失败，请重试"],
                    "salary_range": "Not Mentioned",
                    "market_trends": ["信息提取失败，请重试"],
                    "career_growth": ["信息提取失败，请重试"]
                }
            
            report = {
                "job_title": job,
                "analysis_source": "Tavily Search + OpenAI GPT-4o (Enhanced)",
                **extracted_data
            }

        except Exception as e:
            print(f"--> OpenAI信息提取失败: {e}")
            return {
                "job_title": job,
                "error": "Failed during OpenAI information extraction.",
                "details": str(e),
                "required_skills": ["分析失败"],
                "responsibilities": ["分析失败"],
                "salary_range": "Not Mentioned",
                "market_trends": ["分析失败"],
                "career_growth": ["分析失败"]
            }

        print(f"岗位 {job} 分析完成。")
        return report
