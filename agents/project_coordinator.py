from .education_analyst import EducationAnalyst
from .industry_analyst import IndustryAnalyst
from .data_insight_analyst import DataInsightAnalyst
from .report_generator import ReportGenerator


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
        print(f"开始分析任务：专业 - {major}, 岗位 - {job}")

        # 1. 任务分解与并行分析
        education_report = self.education_analyst.run(major)
        industry_report = self.industry_analyst.run(job)

        # 2. 协同验证与数据挖掘
        analysis_result = self.data_analyst.run(education_report, industry_report)

        # 3. 整合与报告生成
        final_report = self.report_generator.run(analysis_result)
        
        print("分析任务完成。")
        return final_report
