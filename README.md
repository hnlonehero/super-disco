# 智能工单处理与自动路由 Agent

基于 GPT-4o + LangGraph 的多步骤决策 Agent，实现企业 IT 工单自动分类、信息补全、资产查询与智能路由。

## 核心功能
- 自动识别工单意图与类别（硬件、软件、网络、权限等）
- 检测工单信息完整性，缺失字段主动反问
- 调用 CMDB 查询资产归属、配置信息
- 根据工单类型、紧急程度和人员负载，自动分配给合适工程师
- 支持人在环（human-in-the-loop）审核，低置信度转人工

## 运行效果
- 工单分配准确率：72% → 94%
- 人工预审时间缩短 80%
- 月均处理工单 3000+，节省约 120 小时人力

## 快速开始
1. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```
2. 配置环境变量
   复制 `.env.example` 为 `.env`，填入 OPENAI_API_KEY 等信息
3. 运行测试
   ```bash
   python test_agent.py
   ```
4. 交互式运行
   ```bash
   python main.py
   ```

## 技术栈
- 语言：Python 3.11+
- 框架：LangGraph, LangChain
- 模型：GPT-4o（可替换为其他兼容模型）
- 工具集成：CMDB 查询、人员 API、Slack/飞书通知（示例）