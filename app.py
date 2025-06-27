import streamlit as st
from dotenv import load_dotenv
import os

from agents.report_generator import ReportGenerator
from agents.project_coordinator import ProjectCoordinator

# 加载环境变量
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --- Streamlit 前端界面 ---
st.title("智岗匹配-专业岗位匹配度分析智能体")

st.markdown("""
欢迎使用"智岗匹配"分析平台！本平台模拟一个由多领域专家组成的委员会，
为您提供专业、数据驱动的专业-岗位匹配度分析报告。
""")

# 在侧边栏添加一些说明
st.sidebar.header("关于")
st.sidebar.info(
    "这是一个基于多智能体系统（MAS）的演示项目，"
    "旨在模拟不同领域的专家如何协同工作，完成复杂的分析任务。"
)

major_input = st.text_input("请输入专业名称 (例如: 计算机科学)", "计算机科学")
job_title_input = st.text_input("请输入岗位名称 (例如: 人工智能算法工程师)", "人工智能算法工程师")

if st.button("开始分析", type="primary"):
    if not OPENAI_API_KEY:
        st.error("错误：未找到 OPENAI_API_KEY。请检查您的 .env 文件。")
        st.stop()

    with st.spinner("AI智能体团队正在为您举行圆桌讨论，请稍候..."):
        # 1. 初始化"会议主持人"
        coordinator = ProjectCoordinator(openai_api_key=OPENAI_API_KEY)
        
        # 2. 启动讨论
        final_state = coordinator.run_analysis_discussion(major_input, job_title_input)
        
        # 3. 讨论结束后，生成报告
        st.info("讨论已达成共识，正在生成最终分析报告...")
        report_generator = ReportGenerator()
        # 注意：我们将最终的data_insight_report传递给报告生成官
        final_report_markdown = report_generator.run(final_state.get("data_insight_report", {}))
        
        st.markdown(final_report_markdown)

        # (可选) 展示完整的会议讨论日志
        with st.expander("查看详细的圆桌会议讨论日志"):
            st.json(final_state.get("discussion_log", []))
            
        st.success("--- 分析任务完成 ---")
