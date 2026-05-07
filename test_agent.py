"""
测试工单 Agent 基本流程
"""
from agent import run_agent

def test_complete_ticket():
    """测试信息完整的硬件工单"""
    state = run_agent(
        ticket_id="TK-1001",
        user_input="我的电脑蓝屏，需要紧急修理",
        previous_info={"资产编号": "ASSET-001", "故障现象": "频繁蓝屏", "位置": "3楼东区"}
    )
    assert state["category"] == "硬件"
    assert state["missing_fields"] is None or len(state["missing_fields"]) == 0
    assert state["assignee"] is not None
    assert "王工" in state["assignee"] or "赵工" in state["assignee"]
    print("✓ 完整工单测试通过")

def test_incomplete_ticket():
    """测试信息不全的工单，应触发反问"""
    state = run_agent(
        ticket_id="TK-1002",
        user_input="无法连接公司WiFi"
    )
    assert state["category"] == "其他"  # 可能分类为网络，这里简化
    assert len(state["missing_fields"]) > 0
    assert "wait_user" == state["next_step"]
    print("✓ 信息不全反问测试通过")

if __name__ == "__main__":
    test_complete_ticket()
    test_incomplete_ticket()
    print("所有测试通过！")