import json

class ReportGenerator:
    def __init__(self):
        print("报告生成官已初始化。")

    def run(self, analysis_result: dict) -> str:
        """
        将最终的分析结果整合成一份专业的报告
        """
        print("正在生成最终分析报告...")
        
        education_data = analysis_result.get('education_data', {})
        industry_data = analysis_result.get('industry_data', {})

        # 临时生成一份格式化的Markdown字符串作为报告
        final_report = f"""
        # 专业-岗位匹配度初步分析报告

        ## 核心摘要
        {analysis_result.get('summary', '无摘要')}

        ---

        ## 教育侧分析 (占位符数据)
        ```json
        {json.dumps(education_data, indent=2, ensure_ascii=False)}
        ```

        ---

        ## 行业侧分析 (来自Tavily的真实数据)
        ```json
        {json.dumps(industry_data, indent=2, ensure_ascii=False)}
        ```
        """
        
        print("最终报告生成完毕。")
        return final_report.strip()
