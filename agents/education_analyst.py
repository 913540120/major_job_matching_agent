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

    def run(self, major: str, questions: List[str] = None, previous_report: dict = None) -> dict:
        """
        使用Tavily搜索并使用LLM提取结构化数据来分析指定专业
        
        Args:
            major: 专业名称
            questions: 批判者问题列表，用于深化分析
            previous_report: 之前的分析报告，用于优化模式
        
        Returns:
            dict: 分析报告
        """
        print(f"正在分析专业：{major}...")
        
        # 判断是基础分析还是优化分析
        is_optimization_mode = previous_report is not None and questions is not None
        
        if is_optimization_mode:
            print(f"-> 优化模式：基于 {len(questions)} 个批判问题优化现有报告")
            return self._optimize_existing_report(major, questions, previous_report)
        else:
            print(f"-> 基础模式：进行全新的专业分析")
            return self._perform_basic_analysis(major, questions)
    
    def _perform_basic_analysis(self, major: str, questions: List[str] = None) -> dict:
        """执行基础分析（原有逻辑）"""
        # 构建基础查询  
        base_query = f"{major} 专业课程 核心课程 技能培养"
        
        # 如果有批判者问题，添加相关关键词但要控制长度
        if questions:
            # 提取问题中的关键词，避免查询过长
            question_keywords = []
            for q in questions[:2]:  # 最多处理前2个问题
                # 提取关键词：课程、技能、实践等
                if "课程" in q or "course" in q.lower():
                    question_keywords.append("课程设置")
                if "技能" in q or "skill" in q.lower():
                    question_keywords.append("技能培养")
                if "实践" in q or "practice" in q.lower():
                    question_keywords.append("实践教学")
                if "项目" in q or "project" in q.lower():
                    question_keywords.append("项目经验")
            
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
            print("--> 正在连接Tavily API进行深度搜索...")
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
            
            print("--> Tavily深度搜索完成。")
            
        except Exception as e:
            print(f"--> Tavily搜索失败: {e}")
            print("--> 使用备用分析策略...")
            
            # 备用方案：基于专业名称进行基本分析
            context = f"""
            基于专业名称 '{major}' 的基本分析：
            
            {major}专业通常包含以下核心内容：
            - 基础理论课程
            - 核心专业课程
            - 实践实验课程
            - 综合项目训练
            - 专业技能培养
            
            注意：由于网络搜索暂时不可用，以下分析基于通用教育知识。
            """

        # 步骤 2: OpenAI 提取 (使用更强大的Prompt)
        print("--> 正在连接OpenAI API进行信息提取...")
        print("--> 预计需要30-60秒，请耐心等待...")
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
            print(f"--> 根据 {len(questions)} 个批判问题进行深度分析...")
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
        
        CRITICAL: Ensure both fields are present and are arrays. Do not return nested objects or missing fields.
        """
        
        print("--> 发送请求到DeepSeek AI...")
        response = self.openai_client.chat.completions.create(
            model="deepseek-ai/DeepSeek-R1",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Here is the context about the major '{major}':\n\n{context}"}
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
                "core_courses": [],
                "required_skills": []
            }
            
            for field, default_value in required_fields.items():
                if field not in extracted_data:
                    extracted_data[field] = default_value
                elif not isinstance(extracted_data[field], list):
                    # 如果字段类型不正确，使用默认值
                    extracted_data[field] = default_value
            
            print("--> OpenAI信息提取完成。")
            
        except json.JSONDecodeError as e:
            print(f"--> JSON解析失败: {e}")
            # 返回默认结构
            extracted_data = {
                "core_courses": ["信息提取失败，请重试"],
                "required_skills": ["信息提取失败，请重试"]
            }
        
        report = {
            "major_name": major,
            "analysis_source": "Tavily Search + OpenAI GPT-4o",
            **extracted_data
        }

        print(f"专业 {major} 分析完成。")
        return report
    
    def _optimize_existing_report(self, major: str, questions: List[str], previous_report: dict) -> dict:
        """基于批判问题优化现有报告"""
        print("--> 执行报告优化模式...")
        
        # 构建针对性搜索查询
        query_keywords = []
        for q in questions[:3]:  # 最多处理前3个问题
            if "课程" in q or "course" in q.lower():
                query_keywords.append("课程设置")
            if "技能" in q or "skill" in q.lower():
                query_keywords.append("技能培养")
            if "实践" in q or "practice" in q.lower():
                query_keywords.append("实践教学")
            if "项目" in q or "project" in q.lower():
                query_keywords.append("项目经验")
            if "深度" in q or "depth" in q.lower():
                query_keywords.append("深度学习")
            if "前沿" in q or "advanced" in q.lower():
                query_keywords.append("前沿技术")
        
        # 构建补充查询
        if query_keywords:
            query = f"{major} 专业 " + " ".join(query_keywords[:3])
        else:
            query = f"{major} 专业 补充信息"
        
        # 限制查询长度
        if len(query) > 350:
            query = f"{major} 专业 深度补充"
        
        # 尝试获取补充信息
        additional_context = ""
        try:
            print(f"--> 搜索补充信息: {query}")
            tavily_response = self.tavily_client.search(
                query=query,
                search_depth="basic",  # 使用基础搜索节省资源
                max_results=3
            )
            
            for result in tavily_response['results']:
                additional_context += f"补充信息: {result.get('content', '')}\n"
            
            print("--> 补充信息搜索完成")
            
        except Exception as e:
            print(f"--> 补充信息搜索失败: {e}")
            additional_context = "无法获取补充信息，基于现有报告进行优化。"
        
        # 构建优化提示词
        system_prompt = """
        You are an expert education analyst performing report optimization. Your task is to improve and enhance an existing educational analysis report based on specific critical questions.

        You will receive:
        1. An existing analysis report
        2. Critical questions that need to be addressed
        3. Additional context information (if available)

        Your goal is to:
        - **Enhance** the existing report by addressing the critical questions
        - **Add** missing information that answers the questions
        - **Refine** existing content to be more comprehensive
        - **Maintain** the original structure and valuable information

        Do NOT completely rewrite the report. Instead, OPTIMIZE it by:
        - Adding new courses/skills that address the questions
        - Removing outdated or irrelevant items
        - Enhancing descriptions to be more specific and actionable
        """

        questions_str = "\n".join(f"- {q}" for q in questions)
        system_prompt += f"""
        
        **Critical Questions to Address:**
        {questions_str}
        
        Respond ONLY with a valid JSON object in this format:
        {{
            "core_courses": ["Enhanced Course List"],
            "required_skills": ["Enhanced Skills List"]
        }}
        
        CRITICAL: Ensure both fields are present and are arrays. Focus on ENHANCING, not replacing.
        """
        
        # 构建用户输入
        user_content = f"""
        **Existing Report to Optimize:**
        Major: {previous_report.get('major_name', major)}
        Core Courses: {previous_report.get('core_courses', [])}
        Required Skills: {previous_report.get('required_skills', [])}
        
        **Additional Context for Optimization:**
        {additional_context}
        
        Please optimize this report by addressing the critical questions while maintaining the valuable existing information.
        """
        
        print("--> 发送优化请求到DeepSeek AI...")
        response = self.openai_client.chat.completions.create(
            model="deepseek-ai/DeepSeek-R1",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            response_format={"type": "json_object"}
        )
        
        print("--> 正在解析优化结果...")
        response_content = response.choices[0].message.content
        print(f"--> 收到优化结果: {response_content[:200]}...")
        
        try:
            optimized_data = json.loads(response_content)
            
            # 验证数据结构
            if not isinstance(optimized_data, dict):
                raise ValueError(f"期望字典格式，但收到: {type(optimized_data)}")
            
            # 确保字段存在并且是列表
            for field in ["core_courses", "required_skills"]:
                if field not in optimized_data or not isinstance(optimized_data[field], list):
                    # 如果优化失败，使用原报告的数据
                    optimized_data[field] = previous_report.get(field, [])
            
            print("--> 报告优化完成")
            
        except json.JSONDecodeError as e:
            print(f"--> 优化结果解析失败: {e}")
            # 如果解析失败，使用原报告
            optimized_data = {
                "core_courses": previous_report.get("core_courses", []),
                "required_skills": previous_report.get("required_skills", [])
            }
        
        # 构建优化后的报告
        optimized_report = {
            "major_name": major,
            "analysis_source": "Optimized Report (Tavily + OpenAI)",
            "optimization_questions": questions,
            **optimized_data
        }
        
        print(f"专业 {major} 报告优化完成")
        return optimized_report
