class DataInsightAnalyst:
    def __init__(self):
        print("数据洞察师已初始化。")

    def run(self, education_report: dict, industry_report: dict) -> dict:
        """
        对专业报告和行业报告进行交叉验证和数据分析
        
        注意：此阶段暂时只传递数据，不做复杂分析
        """
        major_name = education_report.get("major_name", "")
        job_title = industry_report.get("job_title", "")
        print(f"正在整合 {major_name} 和 {job_title} 的分析结果...")

        # TODO: 以后将在这里加入LLM来从原始数据中提取结构化信息
        
        analysis_result = {
            "education_data": education_report,
            "industry_data": industry_report,
            "summary": f"已整合 {major_name} 专业的初步分析和对 {job_title} 岗位的Tavily搜索原始结果。"
        }

        print("数据整合完成。")
        return analysis_result
