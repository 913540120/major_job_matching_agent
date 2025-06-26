import streamlit as st

def main():
    st.set_page_config(page_title="智岗匹配分析平台", page_icon="🤖")
    st.title("🤖 智岗匹配多智能体分析平台")

    st.markdown("""
    欢迎使用"智岗匹配"分析平台！本平台模拟一个由多领域专家组成的委员会，
    为您提供专业、数据驱动的专业-岗位匹配度分析报告。
    """)

    major = st.text_input("请输入您想分析的专业", "例如：计算机科学")
    job = st.text_input("请输入您想分析的目标岗位", "例如：人工智能算法工程师")

    if st.button("开始分析"):
        st.info("分析任务已启动，请稍候...")
        # TODO: 在此调用项目协调官来启动分析流程
        # result = coordinator.run(major=major, job=job)
        # st.success("分析完成！")
        # st.write(result)

if __name__ == "__main__":
    main()
