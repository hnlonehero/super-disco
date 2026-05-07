"""
交互式工单 Agent 主程序（简化版模拟）
"""
from agent import run_agent


def main():
    print("=== 智能工单路由 Agent 演示 ===")
    ticket_id = input("请输入工单ID：")
    user_input = input("请输入问题描述：")
    print(f"\n正在处理工单 {ticket_id} ...\n")
    result = run_agent(ticket_id, user_input)
    print("处理结果：")
    print(f"分类：{result['category']}")
    if result.get('missing_fields'):
        print("缺失信息反问：", result['messages'][-1]['content'] if result['messages'] else "无")
    else:
        print(f"已分配工程师：{result['assignee']}")
        if result['cmdb_info']:
            print("资产信息：", result['cmdb_info'])


if __name__ == "__main__":
    main()