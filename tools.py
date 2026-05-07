"""
模拟的工具函数，实际可替换为 RestAPI/DB 调用
"""
import random

# 模拟 CMDB 数据库
CMDB_MOCK = {
    "ASSET-001": {"hostname": "PC-John", "user": "张三", "dept": "研发部", "status": "正常"},
    "ASSET-002": {"hostname": "NB-Lisa", "user": "李四", "dept": "财务部", "status": "待报废"},
}

ENGINEERS = {
    "硬件": ["王工", "赵工"],
    "软件": ["刘工", "陈工", "周工"],
    "其他": ["马工"]
}


def query_cmdb(asset_id: str) -> dict:
    """查询 CMDB 资产信息"""
    return CMDB_MOCK.get(asset_id, {"error": "资产不存在"})


def assign_ticket_to_engineer(category: str) -> str:
    """根据工单类别，轮询或随机分配工程师"""
    pool = ENGINEERS.get(category, ENGINEERS["其他"])
    return random.choice(pool)


def get_ticket_category(user_input: str) -> str:
    """极简分类函数，实际由 LLM 完成"""
    return "硬件"  # 占位