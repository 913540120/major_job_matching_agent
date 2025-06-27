from openai import OpenAI
import json
from typing import Dict, Any

class DataInsightAnalyst:
    def __init__(self, openai_api_key: str):
        if not openai_api_key:
            raise ValueError("API key not found in environment variables.")
        # 注意：使用您指定的SiliconFlow接入点
        self.openai_client = OpenAI(base_url='https://api.siliconflow.cn/v1', api_key=openai_api_key)
        print("数据洞察师已初始化，并被赋予'批判者'角色。")

    def run_critique(self, education_report: dict, industry_report: dict) -> Dict[str, Any]:
        """
        以"批判者"的身份，对教育和行业分析师的报告提出质疑和问题。
        注意：这个方法是为了适配新的"虚拟圆桌会议"范式。
        """
        major_name = education_report.get("major_name", "N/A")
        job_title = industry_report.get("job_title", "N/A")
        print(f"批判者开始审查 {major_name} 和 {job_title} 的分析报告...")

        education_skills = education_report.get("required_skills", [])
        industry_skills = industry_report.get("required_skills", [])
        
        # 如果上游数据不完整，无法进行有意义的批判
        if not education_skills or not industry_skills:
            return { "critique_summary": "上游报告信息不足，无法进行有效批判。", "questions_for_next_round": [] }

        try:
            system_prompt = """
            You are a sharp, critical, and detail-oriented data scientist. Your role is not to find agreements, but to challenge assumptions and identify weaknesses in the analysis provided by an education expert and an industry expert.

            You are given two analysis reports: one on a university major (`education_report`) and one on a job role (`industry_report`). Your task is to:
            1.  **Identify Discrepancies and Gaps**: Scrutinize both skill lists. Where are the mismatches? What crucial industry skills are completely missing from the education side?
            2.  **Challenge Vague Terms**: If the education report lists a generic skill like "programming", but the industry demands specific languages like "Python" and "Go", you must point this out.
            3.  **Formulate Probing Questions**: Based on your analysis, generate a list of specific, actionable questions. These questions should force the other experts to provide more detailed and concrete information in the next round of discussion. The goal is to drive the conversation towards a deeper, more useful consensus.

            Respond ONLY with a valid JSON object in the following format:
            {
                "critique_summary": "A brief summary of the main weaknesses found in the comparison.",
                "questions_for_next_round": ["Question 1?", "Question 2?", "Question 3?"]
            }
            """
            
            user_prompt = f"""
            Here are the reports for your critique:
            Education Report: {json.dumps(education_report, ensure_ascii=False)}
            Industry Report: {json.dumps(industry_report, ensure_ascii=False)}
            Please provide your critique and questions.
            """

            print("--> 正在连接DeepSeek API进行批判性分析...")
            response = self.openai_client.chat.completions.create(
                model="deepseek-ai/DeepSeek-R1",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            critique_result = json.loads(response.choices[0].message.content)
            print("--> 批判性分析完成。")
            return critique_result

        except Exception as e:
            print(f"--> 批判者在执行中出错: {e}")
            return { "error": "Failed during critique analysis.", "details": str(e) }

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
            You are an expert HR analyst and data scientist. Your task is to perform a sophisticated, weighted semantic skill matching analysis between a university major's curriculum and a job's requirements.

            Given two lists of skills, `education_skills` and `industry_skills`, you must perform the following steps:
            1.  **Identify Core Skills**: From the `industry_skills` list, identify the most critical, non-negotiable skills for the job. These are the "core" skills. The rest are "related" skills.
            2.  **Perform Matching**: Match skills from `education_skills` to both core and related industry skills. A single education skill can match multiple industry skills.
            3.  **Categorize Results**: Structure your output clearly, separating matches into `core_skills_matched` and `related_skills_matched`. List any skills required by the industry but not covered by the education as `skill_gaps`.

            Respond ONLY with a valid JSON object in the following format:
            {
                "core_skills_matched": [
                    {"education_skill": "e.g., Machine Learning Coursework", "industry_skill": "e.g., TensorFlow"}
                ],
                "related_skills_matched": [
                    {"education_skill": "e.g., Software Engineering Principles", "industry_skill": "e.g., Git"}
                ],
                "skill_gaps": ["skill_from_industry_list_not_covered"]
            }
            """
            
            user_prompt = f"""
            Please perform a weighted semantic skill matching analysis for the following lists:
            Education Skills: {json.dumps(education_skills, ensure_ascii=False)}
            Industry Skills: {json.dumps(industry_skills, ensure_ascii=False)}
            """

            print("--> 正在连接DeepSeek API进行加权语义分析...")
            response = self.openai_client.chat.completions.create(
                model="deepseek-ai/DeepSeek-R1",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            analysis = json.loads(response.choices[0].message.content)
            print("--> 加权语义分析完成。")

            # --- 全新的加权计分逻辑 ---
            # 核心技能匹配得 5 分，相关技能匹配得 1 分
            CORE_SKILL_WEIGHT = 5
            RELATED_SKILL_WEIGHT = 1

            core_matched_score = len(analysis.get("core_skills_matched", [])) * CORE_SKILL_WEIGHT
            related_matched_score = len(analysis.get("related_skills_matched", [])) * RELATED_SKILL_WEIGHT
            
            actual_score = core_matched_score + related_matched_score
            
            # 总分只计算岗位要求的技能总分
            total_possible_score = (len(analysis.get("core_skills_matched", [])) + 
                                    len(analysis.get("related_skills_matched", [])) + 
                                    len(analysis.get("skill_gaps", []))) * CORE_SKILL_WEIGHT

            match_score_percent = (actual_score / total_possible_score * 100) if total_possible_score > 0 else 0

            analysis_result = {
                "match_score_percent": round(match_score_percent, 2),
                "common_skills_semantic": { # 报告结构也升级
                    "core_matches": analysis.get("core_skills_matched", []),
                    "related_matches": analysis.get("related_skills_matched", [])
                },
                "skill_gaps": analysis.get("skill_gaps", []),
                "education_highlights": education_report.get("core_courses", []),
                "industry_highlights": industry_report.get("responsibilities", []),
                "summary": f"{major_name} 专业与 {job_title} 岗位的加权匹配度为 {match_score_percent:.2f}%。核心技能满足度是关键。"
            }

        except Exception as e:
            print(f"--> 数据洞察师在执行中出错: {e}")
            analysis_result = { "error": "Failed during data insight analysis.", "details": str(e) }

        print("量化匹配分析完成。")
        return analysis_result
