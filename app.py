import streamlit as st
from agents import ProjectCoordinator

def main():
    st.set_page_config(page_title="智岗匹配分析平台", page_icon="🤖")
    st.title("🤖 智岗匹配多智能体分析平台")

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

    major = st.text_input("请输入您想分析的专业", "计算机科学")
    job = st.text_input("请输入您想分析的目标岗位", "人工智能算法工程师")

    if st.button("开始分析"):
        with st.spinner("分析任务已启动，智能体团队正在工作中...请稍候..."):
            coordinator = ProjectCoordinator()
            result = coordinator.run(major=major, job=job)
            st.success("分析完成！")
            st.markdown("---")
            st.markdown(result)

if __name__ == "__main__":
    main()
