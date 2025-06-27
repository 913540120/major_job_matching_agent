from .education_analyst import EducationAnalyst
from .industry_analyst import IndustryAnalyst
from .data_insight_analyst import DataInsightAnalyst
from .report_generator import ReportGenerator
import json


class ProjectCoordinator:
    def __init__(self, openai_api_key: str, composio_api_key: str):
        self.openai_api_key = openai_api_key
        self.composio_api_key = composio_api_key
        
        # 将配置传递给其他智能体
        self.education_analyst = EducationAnalyst(
            openai_api_key=self.openai_api_key,
            composio_api_key=self.composio_api_key
        )
        self.industry_analyst = IndustryAnalyst(
            openai_api_key=self.openai_api_key,
            composio_api_key=self.composio_api_key
        )
        self.data_analyst = DataInsightAnalyst(openai_api_key=self.openai_api_key)
        self.report_generator = ReportGenerator()

    def run(self, major: str, job: str) -> str:
        """
        运行整个分析工作流
        """
        print(f"--- 分析任务启动：专业[{major}] vs 岗位[{job}] ---")

        # 1. 教育分析师
        education_report = self.education_analyst.run(major)
        print("\n>>> 教育分析师返回报告 (EducationAnalyst Output):")
        print(json.dumps(education_report, indent=2, ensure_ascii=False))
        print("--------------------------------------------------\n")

        # 2. 行业分析师
        industry_report = self.industry_analyst.run(job)
        print("\n>>> 行业分析师返回报告 (IndustryAnalyst Output):")
        print(json.dumps(industry_report, indent=2, ensure_ascii=False))
        print("--------------------------------------------------\n")

        # 3. 数据洞察师
        analysis_result = self.data_analyst.run(education_report, industry_report)
        print("\n>>> 数据洞察师返回报告 (DataInsightAnalyst Output):")
        print(json.dumps(analysis_result, indent=2, ensure_ascii=False))
        print("--------------------------------------------------\n")

        # 4. 报告生成
        final_report = self.report_generator.run(analysis_result)
        
        print("--- 分析任务完成 ---")
        return final_report
