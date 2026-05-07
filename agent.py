"""
智能工单 Agent 主图定义
使用 LangGraph 构建多步骤决策流程
"""
import os
from typing import TypedDict, Literal, List, Optional
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from tools import query_cmdb, assign_ticket_to_engineer, get_ticket_category
from prompts import SYSTEM_PROMPT, MISSING_INFO_PROMPT, CLASSIFY_PROMPT

load_dotenv()

llm = ChatOpenAI(model="gpt-4o", temperature=0)


class TicketState(TypedDict):
    """
    Agent 状态定义
    """
    ticket_id: str
    user_input: str
    category: Optional[str]           # 工单分类
    missing_fields: Optional[List[str]]  # 缺失关键字段
    collected_info: dict               # 已收集的补充信息
    cmdb_info: Optional[dict]          # 资产查询结果
    assignee: Optional[str]            # 最终分配的工程师
    confidence: float                  # 分类置信度
    next_step: str                     # 路由决策
    messages: List[dict]               # 对话历史（用于反问）


def classify_intent(state: TicketState) -> TicketState:
    """节点1：意图识别与分类"""
    prompt = CLASSIFY_PROMPT.format(user_input=state["user_input"])
    response = llm.invoke([HumanMessage(content=prompt)])
    # 简单解析，实际可使用结构化输出
    content = response.content.lower()
    if "硬件" in content or "hardware" in content:
        state["category"] = "硬件"
    elif "软件" in content or "software" in content:
        state["category"] = "软件"
    else:
        state["category"] = "其他"
    state["confidence"] = 0.95  # 模拟
    return state


def completeness_check(state: TicketState) -> TicketState:
    """节点2：信息完整性检查"""
    # 硬编码示例，实际可让 LLM 判断字段是否齐全
    required_per_category = {
        "硬件": ["资产编号", "故障现象", "位置"],
        "软件": ["系统名称", "错误信息", "影响范围"],
        "其他": ["问题描述"]
    }
    required = required_per_category.get(state["category"], ["问题描述"])
    missing = [f for f in required if f not in state.get("collected_info", {})]
    state["missing_fields"] = missing
    return state


def ask_missing_info(state: TicketState) -> TicketState:
    """节点3：反问缺失信息（仅当信息不全时触发）"""
    if state.get("missing_fields"):
        prompt = MISSING_INFO_PROMPT.format(
            missing=", ".join(state["missing_fields"]),
            user_input=state["user_input"]
        )
        response = llm.invoke([HumanMessage(content=prompt)])
        # 模拟用户回复，实际系统此处会等待用户输入
        # 这里将反问内容存入消息，供外部系统使用
        state["messages"].append({
            "role": "assistant",
            "content": response.content
        })
        # 实际环境中，下一步会暂停并等待用户补充，这里标记为需要等待
        state["next_step"] = "wait_user"
    else:
        state["next_step"] = "continue"
    return state


def enrich_cmdb(state: TicketState) -> TicketState:
    """节点4：查询 CMDB 获取资产信息"""
    # 若已有资产编号则查询，否则跳过
    asset_id = state.get("collected_info", {}).get("资产编号")
    if asset_id:
        cmdb_data = query_cmdb(asset_id)
        state["cmdb_info"] = cmdb_data
    return state


def decide_route(state: TicketState) -> TicketState:
    """节点5：路由决策与分配工程师"""
    # 获取当前负载最小的该类别工程师
    category = state.get("category", "其他")
    assignee = assign_ticket_to_engineer(category)
    state["assignee"] = assignee
    state["messages"].append({
        "role": "assistant",
        "content": f"工单 {state['ticket_id']} 已分类为 {category}，分配给工程师 {assignee}。"
    })
    return state


def should_ask_user(state: TicketState) -> Literal["ask_missing_info", "cmdb_lookup"]:
    """条件边：是否缺少信息"""
    if state.get("missing_fields"):
        return "ask_missing_info"
    return "cmdb_lookup"


# 构建图
builder = StateGraph(TicketState)

builder.add_node("classify", classify_intent)
builder.add_node("completeness", completeness_check)
builder.add_node("ask_missing", ask_missing_info)
builder.add_node("cmdb_lookup", enrich_cmdb)
builder.add_node("assign", decide_route)

builder.set_entry_point("classify")
builder.add_edge("classify", "completeness")
builder.add_conditional_edges(
    "completeness",
    should_ask_user,
    {
        "ask_missing_info": "ask_missing",
        "cmdb_lookup": "cmdb_lookup"
    }
)
builder.add_edge("ask_missing", END)  # 实际系统中等待用户回复后重新进入
builder.add_edge("cmdb_lookup", "assign")
builder.add_edge("assign", END)

agent_graph = builder.compile()


def run_agent(ticket_id: str, user_input: str, previous_info: dict = None) -> dict:
    """
    执行 Agent 处理流程，返回最终状态
    """
    state: TicketState = {
        "ticket_id": ticket_id,
        "user_input": user_input,
        "category": None,
        "missing_fields": None,
        "collected_info": previous_info or {},
        "cmdb_info": None,
        "assignee": None,
        "confidence": 0.0,
        "next_step": "",
        "messages": []
    }
    result = agent_graph.invoke(state)
    return result