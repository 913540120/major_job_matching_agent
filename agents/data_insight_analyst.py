class DataInsightAnalyst:
    def __init__(self):
        print("数据洞察师已初始化。")

    def run(self, education_report: dict, industry_report: dict) -> dict:
        """
        对专业报告和行业报告进行交叉验证和数据分析
        """
        major_name = education_report.get("major_name", "N/A")
        job_title = industry_report.get("job_title", "N/A")
        print(f"正在对 {major_name} 和 {job_title} 进行量化匹配分析...")

        if "error" in industry_report:
             return {
                "error": "Cannot perform analysis due to industry analyst failure.",
                "details": industry_report.get("details")
            }

        major_skills = set(education_report.get("required_skills", []))
        job_skills = set(industry_report.get("required_skills", []))
        
        common_skills = major_skills.intersection(job_skills)
        match_score = len(common_skills) / len(job_skills) * 100 if job_skills else 0
        
        analysis_result = {
            "match_score_percent": round(match_score, 2),
            "common_skills": list(common_skills),
            "skill_gaps": list(job_skills - major_skills),
            "education_highlights": education_report.get("core_courses", []),
            "industry_highlights": industry_report.get("responsibilities", []),
            "summary": f"{major_name} 专业与 {job_title} 岗位的技能匹配度为 {match_score:.2f}%。"
        }

        print("量化匹配分析完成。")
        return analysis_result
