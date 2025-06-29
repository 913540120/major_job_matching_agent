import streamlit as st
from dotenv import load_dotenv
import os
import time
from typing import Dict, Any, List
import traceback
import threading

from agents.report_generator import ReportGenerator
from agents.project_coordinator import ProjectCoordinator

# 加载环境变量
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 设置页面配置
st.set_page_config(
    page_title="智岗匹配分析平台",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化会话状态
if 'analysis_state' not in st.session_state:
    st.session_state.analysis_state = 'idle'  # idle, running, completed, error
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'coordinator' not in st.session_state:
    st.session_state.coordinator = None
if 'current_round' not in st.session_state:
    st.session_state.current_round = 0
if 'analysis_progress' not in st.session_state:
    st.session_state.analysis_progress = []

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    .round-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        margin: 10px 0;
    }
    .agent-card {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        background-color: #f8f9fa;
    }
    .educator-card {
        border-left: 5px solid #28a745;
    }
    .industry-card {
        border-left: 5px solid #ffc107;
    }
    .critic-card {
        border-left: 5px solid #dc3545;
    }
    .coordinator-card {
        border-left: 5px solid #6f42c1;
    }
    .skill-match {
        background-color: #d4edda;
        color: #155724;
        padding: 5px 10px;
        border-radius: 5px;
        margin: 2px;
        display: inline-block;
    }
    .skill-gap {
        background-color: #f8d7da;
        color: #721c24;
        padding: 5px 10px;
        border-radius: 5px;
        margin: 2px;
        display: inline-block;
    }
    .status-info {
        background-color: #d1ecf1;
        color: #0c5460;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
        border-left: 4px solid #bee5eb;
    }
    .warning-box {
        background-color: #fff3cd;
        color: #856404;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
        border-left: 4px solid #ffd700;
    }
</style>
""", unsafe_allow_html=True)

def safe_execute_with_timeout(func, timeout=60, *args, **kwargs):
    """安全执行函数，包含超时和错误处理"""
    try:
        result = [None]
        error = [None]
        
        def target():
            try:
                result[0] = func(*args, **kwargs)
            except Exception as e:
                error[0] = e
        
        thread = threading.Thread(target=target)
        thread.start()
        thread.join(timeout)
        
        if thread.is_alive():
            return None, f"操作超时 ({timeout}秒)"
        
        if error[0]:
            return None, f"执行出错: {str(error[0])}"
        
        return result[0], None
        
    except Exception as e:
        error_msg = f"执行出错: {str(e)}"
        st.error(error_msg)
        print(f"Error in {func.__name__}: {traceback.format_exc()}")
        return None, error_msg

def display_skills_analysis(analysis: Dict[str, Any]):
    """显示技能分析结果"""
    try:
        if "common_skills_semantic" in analysis:
            semantic_data = analysis["common_skills_semantic"]
            
            # 核心技能匹配
            st.subheader("🎯 核心技能匹配")
            core_matches = semantic_data.get("core_matches", [])
            if core_matches:
                for match in core_matches:
                    # 处理字符串格式或字典格式
                    if isinstance(match, str):
                        st.markdown(f"""
                        <div class="skill-match">
                            ✅ <strong>{match}</strong>
                        </div>
                        """, unsafe_allow_html=True)
                    elif isinstance(match, dict):
                        st.markdown(f"""
                        <div class="skill-match">
                            ✅ <strong>{match.get('industry_skill', 'N/A')}</strong> ↔ {match.get('education_skill', 'N/A')}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="skill-match">
                            ✅ <strong>{str(match)}</strong>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("暂无核心技能匹配")
            
            # 相关技能匹配
            st.subheader("🔗 相关技能匹配")
            related_matches = semantic_data.get("related_matches", [])
            if related_matches:
                for match in related_matches:
                    # 处理字符串格式或字典格式
                    if isinstance(match, str):
                        st.markdown(f"""
                        <div class="skill-match">
                            ✓ {match}
                        </div>
                        """, unsafe_allow_html=True)
                    elif isinstance(match, dict):
                        st.markdown(f"""
                        <div class="skill-match">
                            ✓ {match.get('industry_skill', 'N/A')} ↔ {match.get('education_skill', 'N/A')}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="skill-match">
                            ✓ {str(match)}
                        </div>
                        """, unsafe_allow_html=True)
        
        # 技能差距
        if analysis.get("skill_gaps"):
            st.subheader("⚠️ 技能差距")
            for gap in analysis["skill_gaps"]:
                gap_text = gap if isinstance(gap, str) else str(gap)
                st.markdown(f"""
                <div class="skill-gap">
                    ❌ {gap_text}
                </div>
                """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"显示技能分析时出错: {str(e)}")
        print(f"Error in display_skills_analysis: {e}")

class StableAnalysisUI:
    def __init__(self):
        self.progress_container = st.empty()
        self.status_container = st.empty()
        self.results_container = st.container()
        
    def update_progress(self, current_round: int, max_rounds: int, status: str):
        """更新进度条和状态"""
        try:
            with self.progress_container.container():
                progress = min(current_round / max_rounds, 1.0)
                st.progress(progress, text=f"第 {current_round}/{max_rounds} 轮 - {status}")
                
                # 更新会话状态
                st.session_state.current_round = current_round
        except Exception as e:
            print(f"Progress update error: {e}")
    
    def display_round_header(self, round_num: int, max_rounds: int):
        """显示轮次标题"""
        try:
            with self.status_container.container():
                st.markdown(f"""
                <div class="round-header">
                    <h3>📋 第 {round_num}/{max_rounds} 轮讨论</h3>
                </div>
                """, unsafe_allow_html=True)
        except Exception as e:
            print(f"Round header error: {e}")
    
    def display_status(self, message: str, message_type: str = "info"):
        """显示状态消息"""
        try:
            if message_type == "info":
                st.info(f"ℹ️ {message}")
            elif message_type == "success":
                st.success(f"✅ {message}")
            elif message_type == "warning":
                st.warning(f"⚠️ {message}")
            elif message_type == "error":
                st.error(f"❌ {message}")
        except Exception as e:
            print(f"Status display error: {e}")
    
    def display_agent_analysis(self, agent_name: str, analysis: Dict[str, Any]):
        """显示智能体分析结果"""
        try:
            with self.results_container:
                if agent_name == "教育分析师":
                    with st.expander(f"📚 {agent_name} - 专业分析", expanded=True):
                        if analysis.get("error"):
                            st.error(f"分析失败: {analysis['error']}")
                            return
                            
                        col1, col2 = st.columns(2)
                        with col1:
                            st.subheader("核心课程")
                            courses = analysis.get("core_courses", [])
                            if courses:
                                display_count = min(len(courses), 8)
                                for course in courses[:display_count]:
                                    st.write(f"• {course}")
                                if len(courses) > 8:
                                    st.write(f"• ... 及其他 {len(courses) - 8} 门课程")
                            else:
                                st.write("暂无课程信息")
                        
                        with col2:
                            st.subheader("培养技能")
                            skills = analysis.get("required_skills", [])
                            if skills:
                                display_count = min(len(skills), 10)
                                for skill in skills[:display_count]:
                                    st.write(f"• {skill}")
                                if len(skills) > 10:
                                    st.write(f"• ... 及其他 {len(skills) - 10} 项技能")
                            else:
                                st.write("暂无技能信息")
                
                elif agent_name == "行业分析师":
                    with st.expander(f"🏢 {agent_name} - 岗位分析", expanded=True):
                        if analysis.get("error"):
                            st.error(f"分析失败: {analysis['error']}")
                            return
                            
                        # 使用更好的布局展示更多信息
                        col1, col2 = st.columns(2)
                        with col1:
                            st.subheader("技能要求")
                            skills = analysis.get("required_skills", [])
                            if skills:
                                for skill in skills:
                                    st.write(f"• {skill}")
                            else:
                                st.write("暂无技能要求信息")
                            
                            # 薪资信息
                            if analysis.get("salary_range"):
                                st.subheader("💰 薪资范围")
                                st.write(analysis["salary_range"])
                        
                        with col2:
                            st.subheader("主要职责")
                            responsibilities = analysis.get("responsibilities", [])
                            if responsibilities:
                                for resp in responsibilities:
                                    st.write(f"• {resp}")
                            else:
                                st.write("暂无职责信息")
                        
                        # 新增：市场趋势和职业发展（全宽显示）
                        if analysis.get("market_trends"):
                            st.subheader("📈 市场趋势")
                            trends = analysis["market_trends"]
                            for trend in trends:
                                st.write(f"🔸 {trend}")
                        
                        if analysis.get("career_growth"):
                            st.subheader("🚀 职业发展路径")
                            growth_paths = analysis["career_growth"]
                            for path in growth_paths:
                                st.write(f"🔸 {path}")
                
                elif agent_name == "批判分析师":
                    questions = analysis.get("questions_for_next_round", [])
                    if questions:
                        with st.expander(f"🤔 {agent_name} - 批判性问题", expanded=True):
                            st.subheader("提出的深度问题:")
                            for i, question in enumerate(questions, 1):
                                st.write(f"{i}. {question}")
                            
                            # 如果问题太多，发出警告
                            if len(questions) > 3:
                                st.markdown(f"""
                                <div class="warning-box">
                                    ⚠️ 批判者提出了 {len(questions)} 个问题，这可能导致分析时间较长
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.success("🎉 批判分析师未发现进一步问题，分析质量已达标！")
                
                # 批判分析师特殊显示
                elif agent_name == "批判分析师":
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("### 📊 批判总结")
                        critique_summary = analysis.get("critique_summary", "无总结信息")
                        st.write(critique_summary)
                    
                    with col2:
                        st.markdown("### 🎯 质疑统计")
                        education_q_count = len(analysis.get("education_questions", []))
                        industry_q_count = len(analysis.get("industry_questions", []))
                        
                        metrics_col1, metrics_col2 = st.columns(2)
                        with metrics_col1:
                            st.metric("教育专项问题", education_q_count, help="针对专业课程和技能培养的质疑")
                        with metrics_col2:
                            st.metric("行业专项问题", industry_q_count, help="针对岗位需求和市场趋势的质疑")
                    
                    # 显示分类问题详情
                    if analysis.get("education_questions"):
                        with st.expander("📚 教育专项质疑问题", expanded=True):
                            for i, question in enumerate(analysis["education_questions"], 1):
                                st.write(f"**{i}.** {question}")
                    
                    if analysis.get("industry_questions"):
                        with st.expander("🏢 行业专项质疑问题", expanded=True):
                            for i, question in enumerate(analysis["industry_questions"], 1):
                                st.write(f"**{i}.** {question}")
                    
                    if not analysis.get("education_questions") and not analysis.get("industry_questions"):
                        st.success("🎉 未发现需要进一步质疑的问题，分析质量良好！")
        except Exception as e:
            st.error(f"显示{agent_name}结果时出错: {str(e)}")

def initialize_coordinator():
    """初始化协调官（仅一次）"""
    if st.session_state.coordinator is None:
        try:
            st.session_state.coordinator = ProjectCoordinator(openai_api_key=OPENAI_API_KEY)
            return True
        except Exception as e:
            st.error(f"初始化协调官失败: {str(e)}")
            return False
    return True

def should_continue_analysis(critique_result: Dict[str, Any], round_num: int, max_rounds: int) -> bool:
    """智能判断是否应该继续分析（适配分类问题模式）"""
    # 获取分类问题
    education_questions = critique_result.get("education_questions", [])
    industry_questions = critique_result.get("industry_questions", [])
    all_questions = critique_result.get("questions_for_next_round", [])
    
    # 没有任何问题，达成共识
    if not education_questions and not industry_questions:
        return False
    
    # 达到最大轮数
    if round_num >= max_rounds:
        return False
    
    # 检查每个类别的问题数量（分别判断，避免总数过多的误判）
    education_count = len(education_questions)
    industry_count = len(industry_questions)
    
    # 单个类别问题过多才警告（而不是总数）
    if education_count > 6 or industry_count > 6:
        st.warning(f"⚠️ 单个领域问题过多（教育: {education_count}个, 行业: {industry_count}个），为避免过度分析，将在下一轮后结束")
        return round_num < max_rounds - 1
    
    # 检查问题质量（避免重复或无意义问题）
    critique_summary = critique_result.get("critique_summary", "")
    if len(critique_summary) < 30:  # 降低阈值，批判总结过短可能是因为问题很精准
        st.info("ℹ️ 批判质量检测：问题较为精准，将继续深化分析")
    
    # 总问题数量合理性检查（放宽限制）
    total_questions = education_count + industry_count
    if total_questions > 10:  # 从5提高到10
        st.warning(f"⚠️ 问题总数较多（{total_questions}个），将限制下一轮为最后一轮")
        return round_num < max_rounds - 1
    
    return True

def run_stable_analysis(coordinator, major: str, job_title: str, max_rounds: int, ui: StableAnalysisUI):
    """稳定运行分析流程"""
    try:
        # 初始化分析状态
        state = {
            "topic": f"专业[{major}] vs 岗位[{job_title}]",
            "education_report": {},
            "industry_report": {},
            "data_insight_report": {},
            "critique_and_questions": [],  # 保持向后兼容
            "education_questions": [],     # 新增：教育专项问题
            "industry_questions": [],      # 新增：行业专项问题
            "is_consensus_reached": False
        }
        
        ui.display_status("🎯 项目协调官已就位，正在召集专家团队...")
        
        # 限制最大轮数，避免无限循环
        effective_max_rounds = min(max_rounds, 6)  # 硬限制最多6轮
        
        for round_num in range(1, effective_max_rounds + 1):
            ui.display_round_header(round_num, effective_max_rounds)
            ui.update_progress(round_num, effective_max_rounds, f"进行第 {round_num} 轮分析...")
            
            # 检查是否应该强制停止（防止无限循环）
            if round_num > 3 and len(st.session_state.analysis_progress) > 10:
                ui.display_status("⚠️ 检测到过多API调用，为保护系统资源，将结束分析", "warning")
                break
            
            # 第一轮：基础分析
            if round_num == 1:
                # 教育分析师分析
                ui.display_status("📚 教育分析师正在分析专业信息...")
                education_result, error = safe_execute_with_timeout(
                    coordinator.education_analyst.run, 90, major  # 增加到90秒
                )
                if error:
                    ui.display_status(f"教育分析失败: {error}", "error")
                    return None
                state["education_report"] = education_result
                ui.display_agent_analysis("教育分析师", state["education_report"])
                
                # 行业分析师分析
                ui.display_status("🏢 行业分析师正在分析岗位需求...")
                industry_result, error = safe_execute_with_timeout(
                    coordinator.industry_analyst.run, 90, job_title  # 增加到90秒
                )
                if error:
                    ui.display_status(f"行业分析失败: {error}", "error")
                    return None
                state["industry_report"] = industry_result
                ui.display_agent_analysis("行业分析师", state["industry_report"])
            else:
                # 后续轮次：深化分析
                education_question_count = len(state.get('education_questions', []))
                industry_question_count = len(state.get('industry_questions', []))
                ui.display_status(f"🔄 进入定向优化模式：教育问题 {education_question_count} 个，行业问题 {industry_question_count} 个")
                
                # 教育分析师定向优化
                if state.get('education_questions'):
                    limited_education_questions = state['education_questions'][:3]  # 最多处理3个问题
                    ui.display_status(f"📚 教育分析师正在基于 {len(limited_education_questions)} 个教育专项问题优化...（预计需要60-90秒）")
                    education_result, error = safe_execute_with_timeout(
                        coordinator.education_analyst.run, 120, major,  # 优化模式增加到120秒
                        questions=limited_education_questions,
                        previous_report=state["education_report"]
                    )
                    if error:
                        ui.display_status(f"教育分析优化失败: {error}", "error")
                        if "超时" in str(error):
                            ui.display_status("🔄 教育分析优化超时，将使用现有报告继续分析", "warning")  
                            # 不break，继续使用之前的报告
                        else:
                            break
                    state["education_report"] = education_result
                    ui.display_agent_analysis("教育分析师", state["education_report"])
                else:
                    ui.display_status("📚 教育分析师：无专项问题，保持当前分析结果", "info")
                
                # 行业分析师定向优化
                if state.get('industry_questions'):
                    limited_industry_questions = state['industry_questions'][:3]  # 最多处理3个问题
                    ui.display_status(f"🏢 行业分析师正在基于 {len(limited_industry_questions)} 个行业专项问题优化...（预计需要60-90秒）")
                    industry_result, error = safe_execute_with_timeout(
                        coordinator.industry_analyst.run, 120, job_title,  # 优化模式增加到120秒
                        questions=limited_industry_questions,
                        previous_report=state["industry_report"]
                    )
                    if error:
                        ui.display_status(f"行业分析优化失败: {error}", "error")
                        if "超时" in str(error):
                            ui.display_status("🔄 行业分析优化超时，将使用现有报告继续分析", "warning")
                        else:
                            ui.display_status("使用之前的行业分析结果继续", "warning")
                    else:
                        state["industry_report"] = industry_result
                        ui.display_agent_analysis("行业分析师", state["industry_report"])
                else:
                    ui.display_status("🏢 行业分析师：无专项问题，保持当前分析结果", "info")
            
            # 批判分析
            ui.display_status("🤔 批判分析师正在进行质疑和审查...")
            critique_result, error = safe_execute_with_timeout(
                coordinator.critic_analyst.run_critique, 90,  # 从60秒增加到90秒
                state["education_report"],
                state["industry_report"]
            )
            if error:
                ui.display_status(f"批判分析失败: {error}", "error")
                break
            
            # 记录分析进度
            st.session_state.analysis_progress.append({
                "round": round_num,
                "questions": len(critique_result.get("questions_for_next_round", []))
            })
            
            # 提取分类问题并更新状态
            state["education_questions"] = critique_result.get("education_questions", [])
            state["industry_questions"] = critique_result.get("industry_questions", [])
            state["critique_and_questions"] = critique_result.get("questions_for_next_round", [])
            ui.display_agent_analysis("批判分析师", critique_result)
            
            # 智能判断是否继续（基于分类问题）
            has_education_questions = bool(state["education_questions"])
            has_industry_questions = bool(state["industry_questions"])
            
            if not has_education_questions and not has_industry_questions:
                ui.display_status(f"🎉 第 {round_num} 轮达成共识！批判分析师未发现进一步问题。", "success")
                state["is_consensus_reached"] = True
                break
            elif not should_continue_analysis(critique_result, round_num, effective_max_rounds):
                ui.display_status(f"📋 第 {round_num} 轮完成，基于分析质量评估，将结束讨论", "info")
                state["is_consensus_reached"] = True
                break
        
        # 最终量化分析
        ui.display_status("📊 正在进行最终量化匹配分析...")
        final_analysis, error = safe_execute_with_timeout(
            coordinator.critic_analyst.run, 120,  # 从90秒增加到120秒，因为涉及复杂的技能匹配分析
            state["education_report"], 
            state["industry_report"]
        )
        if error:
            ui.display_status(f"最终分析失败: {error}", "error")
            return None
        
        state["data_insight_report"] = final_analysis
        return state
        
    except Exception as e:
        ui.display_status(f"分析过程出现异常: {str(e)}", "error")
        print(f"Analysis error: {traceback.format_exc()}")
        return None

def main():
    # 主标题
    st.markdown('<h1 class="main-header">🎯 智岗匹配分析平台</h1>', unsafe_allow_html=True)
    
    # 介绍区域
    with st.container():
        st.markdown("""
        ### 🌟 欢迎使用专业-岗位匹配度分析系统
        
        本平台模拟一个由多领域专家组成的**圆桌会议**，通过多轮深度讨论为您提供：
        - 📊 量化匹配度分析
        - 🎯 核心技能差距识别  
        - 💡 职业发展建议
        - 📈 实时分析过程展示
        
        **✨ 智能定向质疑模式：**
        - 第一轮进行全面基础分析
        - 批判分析师生成分类问题，分别针对教育和行业
        - 教育分析师只处理教育相关问题，行业分析师只处理行业相关问题  
        - 避免无效质疑，提高分析精准度和效率
        """)
    
    # 侧边栏配置
    with st.sidebar:
        st.header("⚙️ 分析配置")
        
        st.subheader("👥 智能体团队")
        st.info("""
        **项目协调官** 🎩  
        会议主持人，协调整体流程
        
        **教育分析师** 📚  
        专业课程与技能专家
        
        **行业分析师** 🏢  
        岗位需求与市场专家
        
        **批判分析师** 🤔  
        质量把关与深度质疑
        
        **报告生成官** 📋  
        专业报告撰写专家
        """)
        
        st.subheader("🔄 分析模式")
        st.info("""
        **第一轮：基础分析**  
        全新搜索和分析专业与岗位
        
        **后续轮次：定向优化模式**  
        批判分析师生成分类问题：
        - 📚 教育专项问题 → 教育分析师
        - 🏢 行业专项问题 → 行业分析师
        - 🎯 精准优化，避免无关质疑
        """)
        
        st.subheader("🔧 分析参数")
        max_rounds = st.slider("期望讨论轮数", 2, 5, 3, help="实际轮数可能根据分析质量智能调整")
        show_detailed_log = st.checkbox("显示详细日志", value=False)
        
        st.info("""
        **⏱️ 超时设置：**
        - 基础分析：90秒/轮
        - 优化分析：120秒/轮  
        - 批判分析：90秒/轮
        - 最终分析：120秒/轮
        
        **🛡️ 智能保护：**
        - 单个领域问题超过6个将限制轮数
        - 总问题数超过10个将提前结束
        - 超时自动使用现有结果继续
        """)
        
        # 显示当前状态
        if st.session_state.analysis_state != 'idle':
            st.subheader("📊 分析状态")
            st.write(f"状态: {st.session_state.analysis_state}")
            if st.session_state.current_round > 0:
                st.write(f"当前轮次: {st.session_state.current_round}")
        
        # 重置按钮
        if st.button("🔄 重置分析", type="secondary"):
            st.session_state.analysis_state = 'idle'
            st.session_state.analysis_results = None
            st.session_state.coordinator = None
            st.session_state.current_round = 0
            st.session_state.analysis_progress = []
            st.rerun()
    
    # 输入区域
    col1, col2 = st.columns(2)
    with col1:
        major_input = st.text_input(
            "🎓 请输入专业名称", 
            "计算机科学",
            help="例如：计算机科学、电子工程、市场营销等",
            disabled=(st.session_state.analysis_state == 'running')
        )
    with col2:
        job_title_input = st.text_input(
            "💼 请输入目标岗位", 
            "人工智能算法工程师",
            help="例如：软件工程师、产品经理、数据分析师等",
            disabled=(st.session_state.analysis_state == 'running')
        )
    
    # 开始分析按钮
    start_button_disabled = (st.session_state.analysis_state in ['running', 'completed'])
    
    if st.button("🚀 开始深度分析", type="primary", use_container_width=True, disabled=start_button_disabled):
        if not OPENAI_API_KEY:
            st.error("❌ 错误：未找到 OPENAI_API_KEY。请检查您的 .env 文件。")
            st.stop()
        
        # 重置分析进度
        st.session_state.analysis_progress = []
        st.session_state.current_round = 0
        
        # 设置分析状态为运行中
        st.session_state.analysis_state = 'running'
        
        # 创建实时UI
        st.markdown("---")
        st.subheader("🔄 实时分析进程")
        
        ui = StableAnalysisUI()
        
        # 初始化协调官
        if not initialize_coordinator():
            st.session_state.analysis_state = 'error'
            st.stop()
        
        # 运行分析
        final_state = run_stable_analysis(
            st.session_state.coordinator, major_input, job_title_input, max_rounds, ui
        )
        
        if final_state:
            st.session_state.analysis_results = final_state
            st.session_state.analysis_state = 'completed'
            # 不再调用 st.rerun()，避免重复执行
            st.success("✅ 分析完成！请查看下方结果。")
        else:
            st.session_state.analysis_state = 'error'
            st.error("❌ 分析失败，请检查网络连接或重试")
    
    # 显示实时分析状态
    if st.session_state.analysis_state == 'running':
        st.info("⏳ 分析正在进行中，请等待...")
        st.markdown("*分析过程可能需要2-5分钟，请耐心等待系统处理。*")
    
    # 显示结果
    if st.session_state.analysis_state == 'completed' and st.session_state.analysis_results:
        st.markdown("---")
        st.subheader("📊 最终分析报告")
        
        final_state = st.session_state.analysis_results
        
        if final_state.get("data_insight_report"):
            report_generator = ReportGenerator()
            final_report = report_generator.run(final_state["data_insight_report"])
            st.markdown(final_report)
            
            # 显示量化分析
            analysis = final_state["data_insight_report"]
            if "match_score_percent" in analysis:
                score = analysis["match_score_percent"]
                st.metric(
                    label="🎯 总体匹配度",
                    value=f"{score}%",
                    delta=f"{'优秀' if score >= 80 else '良好' if score >= 60 else '需改进' if score >= 40 else '较大差距'}"
                )
                
                display_skills_analysis(analysis)
        
        # 显示分析统计
        st.subheader("📈 分析统计")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("讨论轮数", st.session_state.current_round)
        with col2:
            total_questions = sum(p["questions"] for p in st.session_state.analysis_progress)
            st.metric("总问题数", total_questions)
        with col3:
            st.metric("分析状态", "已完成" if final_state.get("is_consensus_reached") else "已终止")
        
        # 详细日志
        if show_detailed_log:
            with st.expander("📝 查看详细讨论日志"):
                st.json(final_state.get("discussion_log", []))
        
        # 重新分析按钮
        if st.button("🔄 重新分析", type="secondary", use_container_width=True):
            st.session_state.analysis_state = 'idle'
            st.session_state.analysis_results = None
            st.session_state.coordinator = None
            st.session_state.current_round = 0
            st.session_state.analysis_progress = []
            st.rerun()
        
        st.success("✅ 分析任务完成！")
    
    elif st.session_state.analysis_state == 'error':
        st.error("❌ 分析过程中出现错误，请重试。")

if __name__ == "__main__":
    main()
