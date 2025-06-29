"""
项目协调官 (ProjectCoordinator)

职责:
1.  作为多智能体团队的"大脑"和"会议主持人"。
2.  管理一个共享的"讨论区"状态(DiscussionState)，记录会议进程。
3.  按顺序和逻辑编排其他智能体(教育、行业、数据洞察)的执行。
4.  实现"发言-批判-修正"的协作范式，通过迭代循环提升分析质量。
5.  整合最终达成共识的分析结果，并移交给报告生成官。
"""
from typing import TypedDict, List, Dict, Any

from .education_analyst import EducationAnalyst
from .industry_analyst import IndustryAnalyst
from .data_insight_analyst import DataInsightAnalyst
from .report_generator import ReportGenerator
import json

# --- 共享状态定义 ---
class DiscussionState(TypedDict):
    """
    定义"虚拟圆桌会议"的共享讨论区状态
    """
    topic: str
    discussion_log: List[Dict[str, Any]]
    education_report: Dict[str, Any]
    industry_report: Dict[str, Any]
    data_insight_report: Dict[str, Any]
    critique_and_questions: List[str]  # 保持向后兼容
    education_questions: List[str]  # 新增：专门针对教育的问题
    industry_questions: List[str]   # 新增：专门针对行业的问题
    is_consensus_reached: bool


class ProjectCoordinator:
    def __init__(self, openai_api_key: str):
        """
        初始化协调官以及其管理的智能体团队
        """
        self.education_analyst = EducationAnalyst(openai_api_key=openai_api_key, composio_api_key=None)
        self.industry_analyst = IndustryAnalyst(openai_api_key=openai_api_key, composio_api_key=None)
        # 注意: 数据洞察师在这里被赋予了"批判者"的新角色
        self.critic_analyst = DataInsightAnalyst(openai_api_key=openai_api_key) 
        print("项目协调官已就位，并召集了教育、行业及批判分析师团队。")

    def _log_discussion(self, state: DiscussionState, speaker: str, content: Any):
        """记录一条讨论到日志中"""
        state["discussion_log"].append({"speaker": speaker, "content": content})

    def run_analysis_discussion(self, major: str, job_title: str, max_rounds: int = 5) -> Dict[str, Any]:
        """
        主持并执行"虚拟圆桌会议"的完整流程
        """
        # 1. 初始化会议状态
        state: DiscussionState = {
            "topic": f"专业[{major}] vs 岗位[{job_title}]",
            "discussion_log": [],
            "education_report": {},
            "industry_report": {},
            "data_insight_report": {},
            "critique_and_questions": [],
            "education_questions": [],
            "industry_questions": [],
            "is_consensus_reached": False
        }
        self._log_discussion(state, "Coordinator", f"会议开始，议题: {state['topic']}")

        for round_num in range(1, max_rounds + 1):
            print(f"\n--- 开始第 {round_num}/{max_rounds} 轮讨论 ---")
            self._log_discussion(state, "Coordinator", f"第 {round_num} 轮讨论开始")

            # 2. 开场陈述 (或根据上一轮问题进行深化分析)
            if round_num == 1:
                # 第一轮，进行基础分析
                print("第一轮：进行基础专业和岗位分析")
                state["education_report"] = self.education_analyst.run(major)
                state["industry_report"] = self.industry_analyst.run(job_title)
            else:
                # 后续轮次，基于批判问题优化现有报告
                print(f"第 {round_num} 轮：基于分类批判问题优化分析报告")
                
                # 教育分析师使用教育相关问题进行优化
                if state["education_questions"]:
                    print(f"教育分析师正基于 {len(state['education_questions'])} 个教育专项问题优化报告")
                    state["education_report"] = self.education_analyst.run(
                        major, 
                        questions=state["education_questions"],
                        previous_report=state["education_report"]
                    )
                else:
                    print("无教育专项问题，教育分析师保持当前报告")
                
                # 行业分析师使用行业相关问题进行优化
                if state["industry_questions"]:
                    print(f"行业分析师正基于 {len(state['industry_questions'])} 个行业专项问题优化报告")
                    state["industry_report"] = self.industry_analyst.run(
                        job_title, 
                        questions=state["industry_questions"],
                        previous_report=state["industry_report"]
                    )
                else:
                    print("无行业专项问题，行业分析师保持当前报告")
            
            self._log_discussion(state, "EducationAnalyst", state["education_report"])
            self._log_discussion(state, "IndustryAnalyst", state["industry_report"])

            # 3. 自由辩论 (调用批判者提出问题)
            critique_result = self.critic_analyst.run_critique(
                state["education_report"],
                state["industry_report"]
            )
            self._log_discussion(state, "CriticAnalyst", critique_result)
            
            # 提取分类的问题
            state["education_questions"] = critique_result.get("education_questions", [])
            state["industry_questions"] = critique_result.get("industry_questions", [])
            state["critique_and_questions"] = critique_result.get("questions_for_next_round", [])  # 保持向后兼容

            # 4. 判断是否达成共识
            has_education_questions = bool(state["education_questions"])
            has_industry_questions = bool(state["industry_questions"])
            
            if not has_education_questions and not has_industry_questions:
                print("批判者未提出进一步问题，会议达成共识。")
                self._log_discussion(state, "Coordinator", "无更多分类问题，达成共识。")
                state["is_consensus_reached"] = True
                break
            
            # 准备下一轮的分类问题
            education_count = len(state["education_questions"])
            industry_count = len(state["industry_questions"])
            print(f"批判者提出分类问题 - 教育: {education_count}个, 行业: {industry_count}个")
            self._log_discussion(state, "Coordinator", 
                f"发现分类问题 - 教育: {education_count}个, 行业: {industry_count}个。准备下一轮讨论。")

        if not state["is_consensus_reached"]:
            print("\n会议达到最大轮次，结束讨论。")
            self._log_discussion(state, "Coordinator", "达到最大讨论轮次，结束。")

        # 5. 最终总结陈词：无论如何，都在最后进行一次量化分析
        print("正在进行最终的量化匹配分析...")
        final_analysis = self.critic_analyst.run(
            state["education_report"], 
            state["industry_report"]
        )
        state["data_insight_report"] = final_analysis
        self._log_discussion(state, "Coordinator", {"consensus_summary": final_analysis})

        # 6. 返回最终的、经过多轮讨论的状态
        return state
