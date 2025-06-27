from openai import OpenAI
import json

class DataInsightAnalyst:
    def __init__(self, openai_api_key: str):
        if not openai_api_key:
            raise ValueError("API key not found in environment variables.")
        # 注意：使用您指定的SiliconFlow接入点
        self.openai_client = OpenAI(base_url='https://api.siliconflow.cn/v1', api_key=openai_api_key)
        print("数据洞察师已初始化，并配备DeepSeek分析工具。")

    def run(self, education_report: dict, industry_report: dict) -> dict:
        """
        使用DeepSeek模型对专业和行业的技能进行语义匹配分析
        """
        major_name = education_report.get("major_name", "N/A")
        job_title = industry_report.get("job_title", "N/A")
        print(f"正在对 {major_name} 和 {job_title} 进行语义技能匹配分析...")

        if "error" in education_report or "error" in industry_report:
             return { "error": "Cannot perform analysis due to upstream failure." }

        education_skills = education_report.get("required_skills", [])
        industry_skills = industry_report.get("required_skills", [])

        if not education_skills or not industry_skills:
            return { "summary": "信息不足，无法进行有效的技能匹配分析。" }

        try:
            system_prompt = """
            You are an expert HR and data analyst. Your task is to perform a semantic skill matching analysis between a university major's curriculum and a job's requirements.

            Given two lists of skills, `education_skills` and `industry_skills`, identify and categorize them.

            Respond ONLY with a valid JSON object in the following format:
            {
                "matched_skills": [
                    {"education_skill": "e.g., Data Structures", "industry_skill": "e.g., Data Structure and Algorithms"}
                ],
                "unmatched_education_skills": ["skill_from_education_list_only"],
                "unmatched_industry_skills": ["skill_from_industry_list_only"]
            }
            """
            
            user_prompt = f"""
            Please perform a semantic skill matching for the following lists:
            Education Skills: {json.dumps(education_skills, ensure_ascii=False)}
            Industry Skills: {json.dumps(industry_skills, ensure_ascii=False)}
            """

            print("--> 正在连接DeepSeek API进行语义分析...")
            response = self.openai_client.chat.completions.create(
                model="deepseek-ai/DeepSeek-R1",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            analysis = json.loads(response.choices[0].message.content)
            print("--> 语义分析完成。")

            match_count = len(analysis.get("matched_skills", []))
            total_job_skills = match_count + len(analysis.get("unmatched_industry_skills", []))
            match_score = match_count / total_job_skills * 100 if total_job_skills > 0 else 0

            analysis_result = {
                "match_score_percent": round(match_score, 2),
                "common_skills_semantic": analysis.get("matched_skills", []),
                "skill_gaps": analysis.get("unmatched_industry_skills", []),
                "education_highlights": education_report.get("core_courses", []),
                "industry_highlights": industry_report.get("responsibilities", []),
                "summary": f"{major_name} 专业与 {job_title} 岗位的语义技能匹配度为 {match_score:.2f}%。"
            }

        except Exception as e:
            print(f"--> 数据洞察师在执行中出错: {e}")
            analysis_result = { "error": "Failed during data insight analysis.", "details": str(e) }

        print("量化匹配分析完成。")
        return analysis_result
