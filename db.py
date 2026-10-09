import sqlite3
import datetime

DB_PATH = 'customers.db'

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    """初始化数据库，创建表"""
    conn = get_connection()
    c = conn.cursor()
    
    # customers表
    c.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            birth_date TEXT,
            birth_hour TEXT,
            gender TEXT,
            decision_type TEXT,
            decision_desc TEXT,
            background TEXT,
            status TEXT DEFAULT '待排盘',
            created_at TEXT
        )
    ''')
    
    # analysis表
    c.execute('''
        CREATE TABLE IF NOT EXISTS analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            system_state TEXT,
            core_contradiction TEXT,
            opportunities TEXT,
            risks TEXT,
            path_1_name TEXT,
            path_1_prob TEXT,
            path_1_risk TEXT,
            path_1_analysis TEXT,
            path_2_name TEXT,
            path_2_prob TEXT,
            path_2_risk TEXT,
            path_2_analysis TEXT,
            path_3_name TEXT,
            path_3_prob TEXT,
            path_3_risk TEXT,
            path_3_analysis TEXT,
            final_advice_short TEXT,
            final_advice_medium TEXT,
            final_advice_long TEXT,
            key_warning TEXT,
            analyst_name TEXT,
            updated_at TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_all_customers():
    """获取所有客户（分析师用）"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM customers ORDER BY created_at DESC')
    rows = c.fetchall()
    conn.close()
    return rows

def get_customer_by_id(customer_id):
    """通过ID获取客户"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM customers WHERE id = ?', (customer_id,))
    row = c.fetchone()
    conn.close()
    return row

def get_customer_by_phone(phone):
    """通过手机号获取客户（客户自助查询用）"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM customers WHERE phone = ? ORDER BY created_at DESC LIMIT 1', (phone,))
    row = c.fetchone()
    conn.close()
    return row

def find_existing_customer(phone):
    """通过手机号查找是否存在客户记录（去重用）"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM customers WHERE phone = ? ORDER BY created_at DESC LIMIT 1', (phone,))
    row = c.fetchone()
    conn.close()
    return row

def get_analysis_by_customer(customer_id):
    """获取客户的分析数据"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM analysis WHERE customer_id = ?', (customer_id,))
    row = c.fetchone()
    conn.close()
    return row

def save_analysis(data):
    """保存或更新分析结论"""
    conn = get_connection()
    c = conn.cursor()
    
    existing = get_analysis_by_customer(data['customer_id'])
    
    if existing:
        c.execute('''
            UPDATE analysis SET
                system_state=?, core_contradiction=?, opportunities=?, risks=?,
                path_1_name=?, path_1_prob=?, path_1_risk=?, path_1_analysis=?,
                path_2_name=?, path_2_prob=?, path_2_risk=?, path_2_analysis=?,
                path_3_name=?, path_3_prob=?, path_3_risk=?, path_3_analysis=?,
                final_advice_short=?, final_advice_medium=?, final_advice_long=?,
                key_warning=?, analyst_name=?, updated_at=?
            WHERE customer_id=?
        ''', (
            data['system_state'], data['core_contradiction'],
            data['opportunities'], data['risks'],
            data['path_1_name'], data['path_1_prob'], data['path_1_risk'], data['path_1_analysis'],
            data['path_2_name'], data['path_2_prob'], data['path_2_risk'], data['path_2_analysis'],
            data['path_3_name'], data['path_3_prob'], data['path_3_risk'], data['path_3_analysis'],
            data['final_advice_short'], data['final_advice_medium'], data['final_advice_long'],
            data['key_warning'], data['analyst_name'], str(datetime.datetime.now()),
            data['customer_id']
        ))
    else:
        c.execute('''
            INSERT INTO analysis (
                customer_id, system_state, core_contradiction, opportunities, risks,
                path_1_name, path_1_prob, path_1_risk, path_1_analysis,
                path_2_name, path_2_prob, path_2_risk, path_2_analysis,
                path_3_name, path_3_prob, path_3_risk, path_3_analysis,
                final_advice_short, final_advice_medium, final_advice_long,
                key_warning, analyst_name, updated_at
            ) VALUES (?,?,?,?,?, ?,?,?,?, ?,?,?,?, ?,?,?,?, ?,?,?, ?,?,?)
        ''', (
            data['customer_id'], data['system_state'], data['core_contradiction'],
            data['opportunities'], data['risks'],
            data['path_1_name'], data['path_1_prob'], data['path_1_risk'], data['path_1_analysis'],
            data['path_2_name'], data['path_2_prob'], data['path_2_risk'], data['path_2_analysis'],
            data['path_3_name'], data['path_3_prob'], data['path_3_risk'], data['path_3_analysis'],
            data['final_advice_short'], data['final_advice_medium'], data['final_advice_long'],
            data['key_warning'], data['analyst_name'], str(datetime.datetime.now())
        ))
    
    c.execute('UPDATE customers SET status = "已完成" WHERE id = ?', (data['customer_id'],))
    conn.commit()
    conn.close()

def delete_customer(customer_id):
    """删除客户及其关联的分析数据"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM analysis WHERE customer_id = ?', (customer_id,))
    c.execute('DELETE FROM customers WHERE id = ?', (customer_id,))
    conn.commit()
    conn.close()

def update_customer_by_phone(phone, data):
    """客户通过手机号更新自己的信息（仅限待排盘状态）"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        UPDATE customers SET
            name=?, birth_date=?, birth_hour=?, gender=?,
            decision_type=?, decision_desc=?, background=?
        WHERE phone=? AND status='待排盘'
    ''', (data['name'], data['birth_date'], data['birth_hour'], data['gender'],
          data['decision_type'], data['decision_desc'], data['background'], phone))
    conn.commit()
    conn.close()