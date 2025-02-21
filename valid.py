# valid the results of flow by compare it to the results of direct query
# run with `uv run valid.py`
import psycopg2
import json
import textwrap
from contextlib import closing
from psycopg2.extras import DictCursor

# 数据库连接配置
with open('db_conn_cfg.json') as f:
    DB_CONFIG = json.load(f)

def parse_sql_blocks(sql_content):
    """解析SQL文件为验证块"""
    blocks = []
    current_block = {'flow': [], 'direct': []}
    current_type = None
    in_flow = False
    in_direct = False
    
    for line in sql_content.split(';'):
        line = line.strip()
        if not line:
            continue
            
        if 'Flow result' in line:
            current_block['flow'] = [line + ';']
            in_flow = True
            in_direct = False
        elif 'Direct query result' in line:
            current_block['direct'] = [line + ';']
            in_flow = False
            in_direct = True
        elif in_flow:
            current_block['flow'].append(line + ';')
        elif in_direct:
            current_block['direct'].append(line + ';')
        elif '-- validate' in line:
            if current_block['flow'] and current_block['direct']:
                blocks.append({
                    'flow': '\n'.join(current_block['flow']),
                    'direct': '\n'.join(current_block['direct'])
                })
            current_block = {'flow': [], 'direct': []}
            in_flow = False
            in_direct = False
    
    if current_block['flow'] and current_block['direct']:
        blocks.append({
            'flow': '\n'.join(current_block['flow']),
            'direct': '\n'.join(current_block['direct'])
        })
    return blocks

def execute_query(conn, sql_lines):
    """执行SQL并返回结果集（列名+数据）"""
    full_sql = ' '.join(sql_lines)
    with conn.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute(full_sql)
        columns = [desc[0] for desc in cursor.description]
        return columns, cursor.fetchall()

def compare_results(flow_result, direct_result):
    """对比两个结果集"""
    flow_cols, flow_data = flow_result
    direct_cols, direct_data = direct_result
    
    # 列名对比
    col_diff = set(flow_cols).symmetric_difference(direct_cols)
    if col_diff:
        return False, f"列名不一致：{col_diff}"
    
    # 数据行对比
    if len(flow_data) != len(direct_data):
        return False, f"行数不同（Flow:{len(flow_data)} vs Direct:{len(direct_data)}）"
    
    diffs = []
    for i, (f_row, d_row) in enumerate(zip(flow_data, direct_data)):
        if dict(f_row) != dict(d_row):
            diffs.append(f"第{i+1}行差异:\nFlow: {f_row}\nDirect: {d_row}")
    
    return len(diffs) == 0, '\n'.join(diffs)

def main():
    conn_config = DB_CONFIG.copy()
    conn = psycopg2.connect(**conn_config)
    conn.autocommit = True
    
    with closing(conn) as conn:
        with open('valid.sql') as f:
            sql_blocks = parse_sql_blocks(f.read())
        
        for idx, block in enumerate(sql_blocks, 1):
            print(f"\n\033[1m验证块 #{idx}\033[0m")
            
            try:
                # 执行Flow查询
                flow_result = execute_query(conn, block['flow'])
                # 执行Direct查询 
                direct_result = execute_query(conn, block['direct'])
                
                # 结果对比
                is_match, diff_msg = compare_results(flow_result, direct_result)
                
                if is_match:
                    print(textwrap.dedent(f"""
                    \033[32m✓ 验证通过\033[0m
                    列数：{len(flow_result[0])}
                    行数：{len(flow_result[1])}
                    """))
                else:
                    print(textwrap.dedent(f"""
                    \033[31m✗ 验证失败\033[0m
                    {diff_msg}
                    """))
                    
            except Exception as e:
                print(f"\033[31m执行错误：{str(e)}\033[0m")
                conn.rollback()
            else:
                conn.commit()

if __name__ == "__main__":
    main()
