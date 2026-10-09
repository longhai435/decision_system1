import streamlit as st
import datetime
import calendar
from db import (
    init_db, get_all_customers, get_customer_by_id, 
    get_analysis_by_customer, save_analysis, delete_customer,
    find_existing_customer, get_customer_by_phone, update_customer_by_phone
)
from report_generator import generate_report

st.set_page_config(page_title="人生决策辅助系统", layout="wide")

# ---- 自定义CSS：为所有输入框添加可见边框 ----
st.markdown("""
<style>
    /* ========== 单行文本框 ========== */
    .stTextInput input,
    div[data-baseweb="input"] input {
        border: 1px solid #cccccc !important;
        border-radius: 6px !important;
        background-color: #ffffff !important;
    }
    
    /* ========== 多行文本框 ========== */
    .stTextArea textarea,
    div[data-baseweb="textarea"] textarea {
        border: 1px solid #cccccc !important;
        border-radius: 6px !important;
        background-color: #ffffff !important;
    }
    
    /* ========== 数字输入框 ========== */
    .stNumberInput input,
    div[data-baseweb="input"] input[type="number"] {
        border: 1px solid #cccccc !important;
        border-radius: 6px !important;
        background-color: #ffffff !important;
    }
    /* 数字输入的加减按钮 */
    .stNumberInput button {
        border: 1px solid #cccccc !important;
        background-color: #f5f5f5 !important;
    }
    
    /* ========== 下拉框 ========== */
    .stSelectbox div[data-baseweb="select"] > div,
    div[data-baseweb="select"] > div {
        border: 1px solid #cccccc !important;
        border-radius: 6px !important;
        background-color: #ffffff !important;
    }
    
    /* ========== 日期输入框 ========== */
    .stDateInput input,
    div[data-baseweb="input"] input[type="text"] {
        border: 1px solid #cccccc !important;
        border-radius: 6px !important;
        background-color: #ffffff !important;
    }
    
    /* ========== 时间输入框 ========== */
    .stTimeInput input {
        border: 1px solid #cccccc !important;
        border-radius: 6px !important;
        background-color: #ffffff !important;
    }
    
    /* ========== 单选按钮组（radio） ========== */
    .stRadio > div {
        border: 1px solid #cccccc !important;
        border-radius: 6px !important;
        padding: 8px 12px !important;
        background-color: #ffffff !important;
    }
    
    /* ========== 多选按钮组 ========== */
    .stMultiSelect div[data-baseweb="select"] > div {
        border: 1px solid #cccccc !important;
        border-radius: 6px !important;
        background-color: #ffffff !important;
    }
    
    /* ========== 滑块 ========== */
    .stSlider {
        border: 1px solid #cccccc !important;
        border-radius: 6px !important;
        padding: 10px !important;
    }
    
    /* ========== 复选框 ========== */
    .stCheckbox {
        border: 1px solid #cccccc !important;
        border-radius: 6px !important;
        padding: 6px 10px !important;
        background-color: #ffffff !important;
    }
    
    /* ========== 表单容器内的所有输入元素 ========== */
    [data-testid="stForm"] input,
    [data-testid="stForm"] textarea {
        border: 1px solid #cccccc !important;
        border-radius: 6px !important;
        background-color: #ffffff !important;
    }
    
    /* ========== 聚焦状态：高亮 ========== */
    .stTextInput input:focus,
    .stTextArea textarea:focus,
    .stNumberInput input:focus,
    .stDateInput input:focus,
    .stTimeInput input:focus,
    div[data-baseweb="input"] input:focus,
    div[data-baseweb="textarea"] textarea:focus {
        border-color: #ff4b4b !important;
        box-shadow: 0 0 0 2px rgba(255, 75, 75, 0.2) !important;
        outline: none !important;
    }
    
    .stSelectbox div[data-baseweb="select"] > div:focus-within,
    div[data-baseweb="select"] > div:focus-within {
        border-color: #ff4b4b !important;
        box-shadow: 0 0 0 2px rgba(255, 75, 75, 0.2) !important;
    }
    
    /* ========== 输入框悬停状态 ========== */
    .stTextInput input:hover,
    .stTextArea textarea:hover,
    .stNumberInput input:hover {
        border-color: #999999 !important;
    }
    
    /* ========== 表单提交按钮增强 ========== */
    [data-testid="stForm"] button[kind="secondaryFormSubmit"],
    [data-testid="stForm"] button[kind="primaryFormSubmit"] {
        border: 1px solid #cccccc !important;
        border-radius: 6px !important;
    }
</style>
""", unsafe_allow_html=True)



init_db()

# 初始化 session_state
if 'page' not in st.session_state:
    st.session_state['page'] = "📝 信息采集"
if 'edit_customer_id' not in st.session_state:
    st.session_state['edit_customer_id'] = None
if 'is_submitting' not in st.session_state:
    st.session_state['is_submitting'] = False
if 'confirm_delete' not in st.session_state:
    st.session_state['confirm_delete'] = None
if 'my_phone' not in st.session_state:
    st.session_state['my_phone'] = ""

# 侧边栏导航（用 key 绑定 session_state，避免需要点击两次）
st.sidebar.title("📊 决策辅助系统")
page = st.sidebar.radio(
    "导航",
    ["📝 信息采集", "👤 我的信息", "🔍 客户列表", "✏️ 分析录入", "📄 报告生成"],
    key="page"
)


# ============================================================
# 页面1：信息采集
# ============================================================
if page == "📝 信息采集":
    st.title("📝 客户信息采集")
    st.caption("请填写以下信息，提交后分析师将为您进行深度决策分析")
    
    with st.form("client_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("称呼 *", placeholder="如：张先生", key="form_name")
            phone = st.text_input("手机号 *", placeholder="用于查询和接收报告", key="form_phone")
        with col2:
            birth_hour = st.selectbox("出生时辰", 
                ["早子时(24-1)", "丑时(1-3)", "寅时(3-5)", "卯时(5-7)", 
                 "辰时(7-9)", "巳时(9-11)", "午时(11-13)", "未时(13-15)",
                 "申时(15-17)", "酉时(17-19)", "戌时(19-21)", "亥时(21-23)", "晚子时(23-24)","不确定"],
                key="form_hour")
            gender = st.radio("性别", ["男", "女"], horizontal=True, key="form_gender")
        
        # ---- 出生日期：年/月/日三个下拉框 ----
        st.markdown("**出生日期（公历）**")
        col_year, col_month, col_day = st.columns(3)
        with col_year:
            year_options = list(range(datetime.date.today().year, 1929, -1))
            default_year_index = year_options.index(1990) if 1990 in year_options else 0
            selected_year = st.selectbox("年份 *", year_options, index=default_year_index, key="form_year")
        with col_month:
            selected_month = st.selectbox("月份 *", list(range(1, 13)), key="form_month")
        with col_day:
            days_in_month = calendar.monthrange(selected_year, selected_month)[1]
            day_options = list(range(1, days_in_month + 1))
            selected_day = st.selectbox("日期 *", day_options, key="form_day")
        
        birth_date = datetime.date(selected_year, selected_month, selected_day)
        
        decision_type = st.selectbox("决策类型", 
            ["职业发展", "创业投资", "人际关系", "健康养生", "其他"],
            key="form_type")
        
        decision_desc = st.text_input("核心决策问题 *", placeholder="如：是否接受XX公司的Offer？", key="form_desc")
        background = st.text_area("问题背景", placeholder="请详细描述您目前的情况、困惑和期望...", key="form_bg")
        
        submitted = st.form_submit_button(
            "提交信息" if not st.session_state['is_submitting'] else "提交中...",
            disabled=st.session_state['is_submitting']
        )
        
        if submitted:
            # 防重复提交
            if st.session_state['is_submitting']:
                st.warning("⏳ 正在提交中，请勿重复操作")
                st.stop()
            
            # 必填校验
            if not name or not phone or not decision_desc:
                st.error("请填写称呼、手机号和核心决策问题")
                st.stop()
            
            # ---- 去重检查 ----
            existing = find_existing_customer(phone)
            
            if existing:
                status = existing[9]
                if status == "待排盘":
                    st.error(f"⚠️ 手机号 {phone} 已提交过咨询（提交时间：{existing[10]}），请勿重复提交")
                    st.info("如需修改信息，请前往「👤 我的信息」页面，输入手机号查询后修改")
                    st.stop()
                elif status == "分析中":
                    st.warning("⏳ 您提交的咨询正在分析中，请耐心等待")
                    st.stop()
                elif status == "已完成":
                    st.info("✅ 您提交的咨询已完成分析，请前往「👤 我的信息」页面查看")
                    st.stop()
                else:
                    pass
            
            # ---- 提交数据 ----
            st.session_state['is_submitting'] = True
            
            from db import get_connection
            conn = get_connection()
            c = conn.cursor()
            c.execute('''
                INSERT INTO customers 
                (name, phone, birth_date, birth_hour, gender, decision_type, decision_desc, background, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, phone, str(birth_date), birth_hour, gender, decision_type, 
                  decision_desc, background, str(datetime.datetime.now())))
            
            customer_id = c.lastrowid
            conn.commit()
            conn.close()
            
            st.session_state['is_submitting'] = False
            
            st.success("✅ 信息已提交！")
            st.info(f"📌 您的记录ID是：**{customer_id}**，手机号 **{phone}** 用于后续查询")
            
            with st.expander("📋 下一步做什么？", expanded=True):
                st.write("1. 分析师将根据您提供的信息进行排盘分析")
                st.write("2. 分析完成后，您将收到报告")
                st.write("3. 您可以随时在「👤 我的信息」页面查看进度")
            
            st.balloons()


# ============================================================
# 页面2：我的信息（客户自助查询）
# ============================================================
elif page == "👤 我的信息":
    st.title("👤 我的信息")
    st.caption("输入您提交时填写的手机号，查询您的决策咨询记录")
    
    phone = st.text_input("请输入手机号", value=st.session_state.get('my_phone', ''))
    
    if phone:
        customer = get_customer_by_phone(phone)
        if customer:
            st.success(f"✅ 找到您的记录（ID: {customer[0]}）")
            
            with st.container(border=True):
                st.subheader("📋 您提交的信息")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**姓名**：{customer[1]}")
                    st.write(f"**手机号**：{customer[2]}")
                    st.write(f"**出生日期**：{customer[3]}")
                with col2:
                    st.write(f"**出生时辰**：{customer[4]}")
                    st.write(f"**性别**：{customer[5]}")
                    st.write(f"**状态**：{customer[9]}")
                
                st.write(f"**决策类型**：{customer[6]}")
                st.write(f"**核心决策问题**：{customer[7]}")
                if customer[8]:
                    st.write(f"**问题背景**：{customer[8]}")
                st.caption(f"📅 提交时间：{customer[10]}")
            
            status = customer[9]
            
            if status == "待排盘":
                st.info("📝 您的信息尚未开始分析，可以修改或撤回")
                
                with st.expander("✏️ 修改信息", expanded=False):
                    with st.form("edit_form"):
                        col1, col2 = st.columns(2)
                        with col1:
                            new_name = st.text_input("称呼", value=customer[1])
                        with col2:
                            hour_options = ["早子时(24-1)", "丑时(1-3)", "寅时(3-5)", "卯时(5-7)", 
                                            "辰时(7-9)", "巳时(9-11)", "午时(11-13)", "未时(13-15)",
                                            "申时(15-17)", "酉时(17-19)", "戌时(19-21)", "亥时(21-23)","晚子时(23-24)", "不确定"]
                            try:
                                hour_index = hour_options.index(customer[4]) if customer[4] in hour_options else 12
                            except:
                                hour_index = 12
                            new_hour = st.selectbox("出生时辰", hour_options, index=hour_index)
                            new_gender = st.radio("性别", ["男", "女"], index=0 if customer[5] == "男" else 1, horizontal=True)
                        
                        # ---- 出生日期：年/月/日三个下拉框 ----
                        st.markdown("**出生日期（公历）**")
                        existing_date = datetime.datetime.strptime(customer[3], '%Y-%m-%d').date()
                        col_year, col_month, col_day = st.columns(3)
                        with col_year:
                            year_options = list(range(datetime.date.today().year, 1929, -1))
                            default_year_index = year_options.index(existing_date.year) if existing_date.year in year_options else 0
                            new_year = st.selectbox("年份", year_options, index=default_year_index, key="edit_year")
                        with col_month:
                            new_month = st.selectbox("月份", list(range(1, 13)), index=existing_date.month - 1, key="edit_month")
                        with col_day:
                            days_in_month = calendar.monthrange(new_year, new_month)[1]
                            day_options = list(range(1, days_in_month + 1))
                            default_day_index = existing_date.day - 1 if existing_date.day <= days_in_month else 0
                            new_day = st.selectbox("日期", day_options, index=default_day_index, key="edit_day")
                        
                        new_birth = datetime.date(new_year, new_month, new_day)
                        
                        new_type = st.selectbox("决策类型", 
                            ["职业发展", "创业投资", "人际关系", "健康养生", "其他"],
                            index=["职业发展", "创业投资", "人际关系", "健康养生", "其他"].index(customer[6]) if customer[6] in ["职业发展", "创业投资", "人际关系", "健康养生", "其他"] else 0
                        )
                        new_desc = st.text_input("核心决策问题", value=customer[7])
                        new_bg = st.text_area("问题背景", value=customer[8] if customer[8] else "")
                        
                        if st.form_submit_button("💾 保存修改"):
                            update_data = {
                                'name': new_name,
                                'birth_date': str(new_birth),
                                'birth_hour': new_hour,
                                'gender': new_gender,
                                'decision_type': new_type,
                                'decision_desc': new_desc,
                                'background': new_bg
                            }
                            update_customer_by_phone(phone, update_data)
                            st.success("✅ 信息已更新！")
                            st.rerun()
                
                if st.button("🗑️ 撤回提交", type="primary"):
                    st.warning("⚠️ 确认撤回吗？此操作不可恢复！")
                    if st.button("✅ 确认撤回"):
                        delete_customer(customer[0])
                        st.success("✅ 已撤回")
                        st.rerun()
            
            elif status == "分析中":
                st.info("⏳ 您的信息正在分析中，请耐心等待")
            
            elif status == "已完成":
                st.info("✅ 您的咨询已完成分析")
                analysis = get_analysis_by_customer(customer[0])
                if analysis:
                    with st.expander("📄 查看报告摘要", expanded=False):
                        st.write(f"**系统状态**：{analysis[2]}")
                        st.write(f"**核心矛盾**：{analysis[3]}")
                        st.write(f"**短期建议**：{analysis[18]}")
                        st.write(f"**关键风险**：{analysis[21]}")
        else:
            st.warning("未找到该手机号的记录，请确认是否正确")
    else:
        st.info("请输入手机号查询")


# ============================================================
# 页面3：客户列表（分析师专用）
# ============================================================
elif page == "🔍 客户列表":
    st.title("🔍 客户列表")
    
    if st.button("🔄 刷新列表"):
        st.rerun()
    
    customers = get_all_customers()
    if customers:
        st.caption(f"共 {len(customers)} 条记录")
        
        for c in customers:
            with st.expander(f"📋 #{c[0]} | {c[1]} | {c[2]} | {c[7][:30]}{'...' if len(c[7]) > 30 else ''} | 状态：{c[9]}", expanded=False):
                col_info, col_action = st.columns([4, 1])
                
                with col_info:
                    st.markdown("**📌 基本信息**")
                    col1, col2, col3, col4, col5 = st.columns(5)
                    with col1:
                        st.write(f"**ID**：{c[0]}")
                    with col2:
                        st.write(f"**姓名**：{c[1]}")
                    with col3:
                        st.write(f"**手机号**：{c[2]}")
                    with col4:
                        st.write(f"**性别**：{c[5]}")
                    with col5:
                        st.write(f"**状态**：{c[9]}")
                    
                    st.markdown("**📅 出生信息（排盘用）**")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**出生日期**：{c[3]}")
                    with col2:
                        st.write(f"**出生时辰**：{c[4]}")
                    
                    st.markdown("**💼 决策信息**")
                    st.write(f"**决策类型**：{c[6]}")
                    st.write(f"**核心问题**：{c[7]}")
                    if c[8]:
                        st.write(f"**问题背景**：{c[8]}")
                    
                    st.caption(f"📅 提交时间：{c[10]}")
                
                with col_action:
                    st.write("")
                    st.write("")
                    if st.button("✏️ 修改分析", key=f"edit_detail_{c[0]}"):
                        st.session_state['edit_customer_id'] = c[0]
                        st.session_state['page'] = "✏️ 分析录入"
                        st.rerun()
                    if st.button("🗑️ 删除", key=f"del_detail_{c[0]}"):
                        st.session_state['confirm_delete'] = c[0]
                        st.rerun()
            
            st.divider()
        
        # 删除确认
        if st.session_state['confirm_delete']:
            del_id = st.session_state['confirm_delete']
            customer = get_customer_by_id(del_id)
            if customer:
                st.warning(f"⚠️ 确认删除客户「{customer[1]}」及其所有分析数据吗？此操作不可恢复！")
                col_yes, col_no = st.columns(2)
                with col_yes:
                    if st.button("✅ 确认删除"):
                        delete_customer(del_id)
                        st.success(f"✅ 客户「{customer[1]}」已删除")
                        st.session_state['confirm_delete'] = None
                        st.rerun()
                with col_no:
                    if st.button("❌ 取消"):
                        st.session_state['confirm_delete'] = None
                        st.rerun()
    else:
        st.info("📭 暂无客户记录")


# ============================================================
# 页面4：分析录入
# ============================================================
elif page == "✏️ 分析录入":
    st.title("✏️ 命盘分析录入")
    st.caption("💡 操作流程：在排盘软件中排盘 → 分析 → 将结论填入下方表单")
    
    default_id = st.session_state.get('edit_customer_id', 1)
    customer_id = st.number_input("客户ID", min_value=1, step=1, value=default_id)
    
    if customer_id:
        customer = get_customer_by_id(customer_id)
        if customer:
            st.info(f"👤 {customer[1]} | 手机号：{customer[2]} | 决策问题：{customer[7]}")
            
            existing_analysis = get_analysis_by_customer(customer_id)
            if existing_analysis:
                st.info("📋 该客户已有分析数据，修改后将覆盖")
            
            # 默认值
            default_state = "待评估"
            default_contradiction = ""
            default_opportunities = ""
            default_risks = ""
            default_p1n = default_p1p = default_p1a = ""
            default_p1r = "中"
            default_p2n = default_p2p = default_p2a = ""
            default_p2r = "中"
            default_p3n = default_p3p = default_p3a = ""
            default_p3r = "中"
            default_short = default_medium = default_long = default_warning = ""
            default_analyst = "你的名字"
            
            if existing_analysis:
                default_state = existing_analysis[2] or "待评估"
                default_contradiction = existing_analysis[3] or ""
                default_opportunities = existing_analysis[4] or ""
                default_risks = existing_analysis[5] or ""
                default_p1n = existing_analysis[6] or ""
                default_p1p = existing_analysis[7] or ""
                default_p1r = existing_analysis[8] or "中"
                default_p1a = existing_analysis[9] or ""
                default_p2n = existing_analysis[10] or ""
                default_p2p = existing_analysis[11] or ""
                default_p2r = existing_analysis[12] or "中"
                default_p2a = existing_analysis[13] or ""
                default_p3n = existing_analysis[14] or ""
                default_p3p = existing_analysis[15] or ""
                default_p3r = existing_analysis[16] or "中"
                default_p3a = existing_analysis[17] or ""
                default_short = existing_analysis[18] or ""
                default_medium = existing_analysis[19] or ""
                default_long = existing_analysis[20] or ""
                default_warning = existing_analysis[21] or ""
                default_analyst = existing_analysis[22] or "你的名字"
            
            with st.form("analysis_form"):
                st.subheader("📊 系统状态")
                col1, col2 = st.columns(2)
                with col1:
                    system_state = st.selectbox("当前系统状态", 
                        ["扩张期", "收缩期", "转型期", "卡滞期", "待评估"],
                        index=["扩张期", "收缩期", "转型期", "卡滞期", "待评估"].index(default_state),
                        key="system_state")
                    core_contradiction = st.text_area("核心矛盾", value=default_contradiction, key="core_contradiction")
                with col2:
                    opportunities = st.text_area("机会点（2-3个）", value=default_opportunities, key="opportunities")
                    risks = st.text_area("风险点（2-3个）", value=default_risks, key="risks")
                
                st.subheader("🗺️ 决策路径推演")
                st.caption("基于命盘+卦象，推演3条可能路径")
                
                # 路径一
                col1, col2, col3 = st.columns(3)
                with col1:
                    path_1_name = st.text_input("路径一名称", value=default_p1n, key="path_1_name")
                with col2:
                    path_1_prob = st.text_input("概率", value=default_p1p, key="path_1_prob")
                with col3:
                    path_1_risk = st.selectbox("风险等级", ["高", "中", "低"], 
                        index=["高", "中", "低"].index(default_p1r), key="path_1_risk")
                path_1_analysis = st.text_area("路径一分析", value=default_p1a, key="path_1_analysis")
                
                # 路径二
                col1, col2, col3 = st.columns(3)
                with col1:
                    path_2_name = st.text_input("路径二名称", value=default_p2n, key="path_2_name")
                with col2:
                    path_2_prob = st.text_input("概率", value=default_p2p, key="path_2_prob")
                with col3:
                    path_2_risk = st.selectbox("风险等级", ["高", "中", "低"], 
                        index=["高", "中", "低"].index(default_p2r), key="path_2_risk")
                path_2_analysis = st.text_area("路径二分析", value=default_p2a, key="path_2_analysis")
                
                # 路径三
                col1, col2, col3 = st.columns(3)
                with col1:
                    path_3_name = st.text_input("路径三名称", value=default_p3n, key="path_3_name")
                with col2:
                    path_3_prob = st.text_input("概率", value=default_p3p, key="path_3_prob")
                with col3:
                    path_3_risk = st.selectbox("风险等级", ["高", "中", "低"], 
                        index=["高", "中", "低"].index(default_p3r), key="path_3_risk")
                path_3_analysis = st.text_area("路径三分析", value=default_p3a, key="path_3_analysis")
                
                st.subheader("📋 执行建议")
                final_advice_short = st.text_area("短期建议（1个月）", value=default_short, key="advice_short")
                final_advice_medium = st.text_area("中期建议（3个月）", value=default_medium, key="advice_medium")
                final_advice_long = st.text_area("长期建议（1年）", value=default_long, key="advice_long")
                key_warning = st.text_area("⚠️ 最重要的风险提示", value=default_warning, key="key_warning")
                analyst_name = st.text_input("分析师签名", value=default_analyst, key="analyst_name")
                
                submitted = st.form_submit_button("💾 保存分析")
                
                if submitted:
                    data = {
                        'customer_id': customer_id,
                        'system_state': system_state,
                        'core_contradiction': core_contradiction,
                        'opportunities': opportunities,
                        'risks': risks,
                        'path_1_name': path_1_name,
                        'path_1_prob': path_1_prob,
                        'path_1_risk': path_1_risk,
                        'path_1_analysis': path_1_analysis,
                        'path_2_name': path_2_name,
                        'path_2_prob': path_2_prob,
                        'path_2_risk': path_2_risk,
                        'path_2_analysis': path_2_analysis,
                        'path_3_name': path_3_name,
                        'path_3_prob': path_3_prob,
                        'path_3_risk': path_3_risk,
                        'path_3_analysis': path_3_analysis,
                        'final_advice_short': final_advice_short,
                        'final_advice_medium': final_advice_medium,
                        'final_advice_long': final_advice_long,
                        'key_warning': key_warning,
                        'analyst_name': analyst_name
                    }
                    save_analysis(data)
                    st.success("✅ 分析已保存！请前往「报告生成」页面生成报告。")
        else:
            st.warning("未找到该客户，请确认ID")


# ============================================================
# 页面5：报告生成
# ============================================================
elif page == "📄 报告生成":
    st.title("📄 报告生成")
    
    customer_id = st.number_input("输入客户ID生成报告", min_value=1, step=1)
    
    if customer_id:
        customer = get_customer_by_id(customer_id)
        if customer:
            analysis = get_analysis_by_customer(customer_id)
            if analysis:
                st.success(f"✅ 客户「{customer[1]}」（{customer[2]}）的分析已完成")
                
                with st.expander("📋 查看分析内容预览"):
                    st.write(f"**系统状态**：{analysis[2]}")
                    st.write(f"**核心矛盾**：{analysis[3]}")
                    st.write(f"**路径一**：{analysis[6]}（{analysis[7]}，风险{analysis[8]}）")
                    st.write(f"**路径二**：{analysis[10]}（{analysis[11]}，风险{analysis[12]}）")
                    st.write(f"**路径三**：{analysis[14]}（{analysis[15]}，风险{analysis[16]}）")
                
                if st.button("📥 生成并下载报告"):
                    report_path = generate_report(customer_id, customer, analysis)
                    with open(report_path, "rb") as f:
                        st.download_button(
                            label="📥 点击下载报告",
                            data=f,
                            file_name=report_path.split('/')[-1],
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                    st.success(f"✅ 报告已生成：{report_path}")
            else:
                st.warning("该客户尚未完成分析录入，请先到「分析录入」页面填写")
        else:
            st.warning("未找到该客户，请确认ID")