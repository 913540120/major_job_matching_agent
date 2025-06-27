import json
import textwrap

class ReportGenerator:
    def __init__(self):
        print("报告生成官已初始化。")

    def run(self, analysis_result: dict) -> str:
        """
        将最终的分析结果整合成一份专业的报告
        """
        print("正在生成最终分析报告...")

        if "error" in analysis_result:
            return f"""
            # 分析失败
            报告生成失败，原因如下：
            - **错误**: {analysis_result.get('error')}
            - **详情**: {analysis_result.get('details')}
            """

        industry_highlights_list = analysis_result.get('industry_highlights', ['信息待补充'])
        industry_highlights_str = '\n- '.join(industry_highlights_list)

        final_report_str = f"""
        # 专业-岗位匹配度分析报告

        ## 核心摘要
        {analysis_result.get('summary', '无摘要')}

        ---

        ## 量化分析
        - **语义匹配度得分**: **{analysis_result.get('match_score_percent', 0)}%**
        
        ### 语义匹配技能
        {self.format_matched_skills(analysis_result.get('common_skills_semantic', []))}

        ### 主要技能差距 (岗位要求但专业未覆盖)
        - {', '.join(analysis_result.get('skill_gaps', ['无']))}

        ---

        ## 详情分析

        ### 教育侧重点
        根据分析，该专业的核心课程可能包括：
        - {', '.join(analysis_result.get('education_highlights', ['信息待补充']))}

        ### 行业侧重点
        根据网络数据分析，该岗位的主要职责包括：
        - {industry_highlights_str}
        
        """
        
        final_report = textwrap.dedent(final_report_str)
        print("最终报告生成完毕。")
        return final_report.strip()

    def format_matched_skills(self, matched_skills: list) -> str:
        if not matched_skills:
            return "- 无"
        
        lines = []
        for match in matched_skills:
            lines.append(f"- **{match['industry_skill']}** (岗位) <=> **{match['education_skill']}** (专业)")
        return "\n".join(lines)
