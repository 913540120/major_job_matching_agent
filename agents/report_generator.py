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
            error_report = f"""
            # 分析失败
            报告生成失败，原因如下：
            - **错误**: {analysis_result.get('error')}
            - **详情**: {analysis_result.get('details')}
            """
            return textwrap.dedent(error_report)

        report_lines = [
            "# 专业-岗位匹配度分析报告",
            "## 核心摘要",
            f"{analysis_result.get('summary', '无摘要')}",
            "---",
            "## 量化分析",
            f"- **加权匹配度得分**: **{analysis_result.get('match_score_percent', 0)}%**",
            ""
        ]

        # --- 全新、分层的技能匹配报告结构 ---
        
        # 1. 核心技能匹配
        report_lines.append("### **核心技能匹配 (Core Skills)**")
        core_matches = analysis_result.get('common_skills_semantic', {}).get('core_matches', [])
        if not core_matches:
            report_lines.append("- _无核心技能匹配_")
        else:
            for match in core_matches:
                report_lines.append(f"- **{match.get('industry_skill', 'N/A')}** (岗位) <=> **{match.get('education_skill', 'N/A')}** (专业)")
        
        report_lines.append("") # 添加空行

        # 2. 相关技能匹配
        report_lines.append("### 相关技能匹配 (Related Skills)")
        related_matches = analysis_result.get('common_skills_semantic', {}).get('related_matches', [])
        if not related_matches:
            report_lines.append("- _无相关技能匹配_")
        else:
            for match in related_matches:
                report_lines.append(f"- {match.get('industry_skill', 'N/A')} (岗位) <=> {match.get('education_skill', 'N/A')} (专业)")

        report_lines.append("") # 添加空行

        # 3. 技能差距
        report_lines.append("### **主要技能差距 (岗位要求但专业未覆盖)**")
        skill_gaps = analysis_result.get('skill_gaps', [])
        if not skill_gaps:
            report_lines.append("- _无明显技能差距_")
        else:
            for gap in skill_gaps:
                report_lines.append(f"- **{gap}**")

        report_lines.extend([
            "---",
            "## 详情分析",
            "### 教育侧重点",
            "根据分析，该专业的核心课程可能包括：",
            f"- {', '.join(analysis_result.get('education_highlights', ['信息待补充']))}",
            "",
            "### 行业侧重点",
            "根据网络数据分析，该岗位的主要职责包括："
        ])
        
        industry_highlights = analysis_result.get('industry_highlights', ['信息待补充'])
        if not industry_highlights:
            report_lines.append("- _无信息_")
        else:
            for highlight in industry_highlights:
                report_lines.append(f"- {highlight}")
            
        final_report = "\n".join(report_lines)
        print("最终报告生成完毕。")
        return final_report
