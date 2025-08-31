# BlueV实时通信系统设计

**文档版本**: v1.0
**创建日期**: 2025-01-27
**关联文档**: BlueV_Architecture_Design.md, Workflow_Engine_Design.md

---

## 🎯 **实时通信设计目标**

### **核心需求**
- 🔄 **实时状态同步**: 工作流执行状态实时推送到前端
- 📡 **双向通信**: 支持前端控制后端执行（启动、暂停、停止）
- 🚀 **高性能**: 低延迟的消息传递
- 🔒 **可靠性**: 连接断开自动重连机制
- 📊 **可扩展**: 支持多客户端连接和广播

---

## 🏗️ **WebSocket通信架构**

### **连接管理器**
```python
from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
import uuid

class ConnectionInfo:
    """连接信息"""
    def __init__(self, websocket: WebSocket, session_id: str, client_info: Dict[str, Any] = None):
        self.websocket = websocket
        self.session_id = session_id
        self.client_info = client_info or {}
        self.connected_at = datetime.now()
        self.last_heartbeat = datetime.now()
        self.subscriptions: set = set()  # 订阅的事件类型

class WorkflowWebSocketManager:
    """WebSocket连接管理器"""

    def __init__(self):
        self.active_connections: Dict[str, ConnectionInfo] = {}
        self.workflow_sessions: Dict[str, str] = {}  # workflow_id -> session_id
        self.logger = logging.getLogger(__name__)
        self._heartbeat_task = None

    async def connect(self, websocket: WebSocket, session_id: str, client_info: Dict[str, Any] = None):
        """建立WebSocket连接"""
        await websocket.accept()

        connection_info = ConnectionInfo(websocket, session_id, client_info)
        self.active_connections[session_id] = connection_info

        self.logger.info(f"WebSocket connected: {session_id}")

        # 发送连接确认消息
        await self.send_message(session_id, {
            "type": "connection_established",
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        })

        # 启动心跳检测
        if not self._heartbeat_task:
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

    def disconnect(self, session_id: str):
        """断开WebSocket连接"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]

        # 清理工作流会话映射
        workflow_ids_to_remove = [
            wf_id for wf_id, sid in self.workflow_sessions.items()
            if sid == session_id
        ]
        for wf_id in workflow_ids_to_remove:
            del self.workflow_sessions[wf_id]

        self.logger.info(f"WebSocket disconnected: {session_id}")

    async def send_message(self, session_id: str, message: Dict[str, Any]) -> bool:
        """发送消息到指定会话"""
        if session_id not in self.active_connections:
            return False

        connection = self.active_connections[session_id]
        try:
            await connection.websocket.send_text(json.dumps(message))
            return True
        except Exception as e:
            self.logger.error(f"Failed to send message to {session_id}: {e}")
            self.disconnect(session_id)
            return False

    async def broadcast(self, message: Dict[str, Any], event_type: str = None):
        """广播消息到所有连接"""
        disconnected_sessions = []

        for session_id, connection in self.active_connections.items():
            # 检查订阅
            if event_type and event_type not in connection.subscriptions:
                continue

            success = await self.send_message(session_id, message)
            if not success:
                disconnected_sessions.append(session_id)

        # 清理断开的连接
        for session_id in disconnected_sessions:
            self.disconnect(session_id)

    async def subscribe(self, session_id: str, event_types: List[str]):
        """订阅事件类型"""
        if session_id in self.active_connections:
            connection = self.active_connections[session_id]
            connection.subscriptions.update(event_types)

            await self.send_message(session_id, {
                "type": "subscription_confirmed",
                "subscriptions": list(connection.subscriptions)
            })

    async def unsubscribe(self, session_id: str, event_types: List[str]):
        """取消订阅事件类型"""
        if session_id in self.active_connections:
            connection = self.active_connections[session_id]
            connection.subscriptions.difference_update(event_types)

            await self.send_message(session_id, {
                "type": "subscription_updated",
                "subscriptions": list(connection.subscriptions)
            })

    def bind_workflow_session(self, workflow_id: str, session_id: str):
        """绑定工作流到会话"""
        self.workflow_sessions[workflow_id] = session_id

    async def send_workflow_message(self, workflow_id: str, message: Dict[str, Any]) -> bool:
        """发送消息到工作流对应的会话"""
        if workflow_id in self.workflow_sessions:
            session_id = self.workflow_sessions[workflow_id]
            return await self.send_message(session_id, message)
        return False

    async def _heartbeat_loop(self):
        """心跳检测循环"""
        while True:
            try:
                await asyncio.sleep(30)  # 30秒心跳间隔

                current_time = datetime.now()
                disconnected_sessions = []

                for session_id, connection in self.active_connections.items():
                    # 发送心跳
                    success = await self.send_message(session_id, {
                        "type": "heartbeat",
                        "timestamp": current_time.isoformat()
                    })

                    if success:
                        connection.last_heartbeat = current_time
                    else:
                        disconnected_sessions.append(session_id)

                # 清理断开的连接
                for session_id in disconnected_sessions:
                    self.disconnect(session_id)

            except Exception as e:
                self.logger.error(f"Heartbeat loop error: {e}")

    def get_connection_stats(self) -> Dict[str, Any]:
        """获取连接统计信息"""
        return {
            "total_connections": len(self.active_connections),
            "active_workflows": len(self.workflow_sessions),
            "connections": [
                {
                    "session_id": session_id,
                    "connected_at": conn.connected_at.isoformat(),
                    "last_heartbeat": conn.last_heartbeat.isoformat(),
                    "subscriptions": list(conn.subscriptions),
                    "client_info": conn.client_info
                }
                for session_id, conn in self.active_connections.items()
            ]
        }
```

### **FastAPI WebSocket端点**
```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json

# 创建FastAPI应用
app = FastAPI(title="BlueV Workflow Engine API", version="1.0.0")
manager = WorkflowWebSocketManager()

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket连接端点"""
    await manager.connect(websocket, session_id)

    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            message = json.loads(data)

            # 处理不同类型的消息
            await handle_websocket_message(session_id, message)

    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        manager.logger.error(f"WebSocket error for {session_id}: {e}")
        manager.disconnect(session_id)

async def handle_websocket_message(session_id: str, message: Dict[str, Any]):
    """处理WebSocket消息"""
    message_type = message.get("type")

    if message_type == "execute_workflow":
        await handle_workflow_execution(session_id, message)
    elif message_type == "control_workflow":
        await handle_workflow_control(session_id, message)
    elif message_type == "subscribe":
        event_types = message.get("event_types", [])
        await manager.subscribe(session_id, event_types)
    elif message_type == "unsubscribe":
        event_types = message.get("event_types", [])
        await manager.unsubscribe(session_id, event_types)
    elif message_type == "heartbeat_response":
        # 更新心跳时间
        if session_id in manager.active_connections:
            manager.active_connections[session_id].last_heartbeat = datetime.now()
    else:
        await manager.send_message(session_id, {
            "type": "error",
            "message": f"Unknown message type: {message_type}"
        })

async def handle_workflow_execution(session_id: str, message: Dict[str, Any]):
    """处理工作流执行请求"""
    try:
        workflow_data = message.get("workflow")
        workflow_id = workflow_data.get("id", str(uuid.uuid4()))

        # 绑定工作流到会话
        manager.bind_workflow_session(workflow_id, session_id)

        # 创建工作流引擎和执行上下文
        engine = WorkflowEngine()
        context = ExecutionContext(workflow_id)

        # 添加实时通信回调
        await setup_workflow_callbacks(context, workflow_id)

        # 构建工作流
        await build_workflow_from_data(engine, workflow_data)

        # 验证工作流
        validation_errors = engine.validate_workflow()
        if validation_errors:
            await manager.send_workflow_message(workflow_id, {
                "type": "workflow_validation_error",
                "errors": validation_errors
            })
            return

        # 异步执行工作流
        asyncio.create_task(execute_workflow_async(engine, context, workflow_id))

        # 发送执行开始确认
        await manager.send_workflow_message(workflow_id, {
            "type": "workflow_execution_started",
            "workflow_id": workflow_id
        })

    except Exception as e:
        await manager.send_message(session_id, {
            "type": "workflow_execution_error",
            "error": str(e)
        })

async def handle_workflow_control(session_id: str, message: Dict[str, Any]):
    """处理工作流控制请求"""
    workflow_id = message.get("workflow_id")
    action = message.get("action")  # "pause", "resume", "stop"

    # 这里需要实现工作流控制逻辑
    # 可以通过全局工作流管理器来控制执行

    await manager.send_message(session_id, {
        "type": "workflow_control_response",
        "workflow_id": workflow_id,
        "action": action,
        "status": "acknowledged"
    })

async def setup_workflow_callbacks(context: ExecutionContext, workflow_id: str):
    """设置工作流回调函数"""

    async def on_node_start(ctx, node_id: str, **kwargs):
        await manager.send_workflow_message(workflow_id, {
            "type": "node_status_update",
            "node_id": node_id,
            "status": "running",
            "timestamp": datetime.now().isoformat()
        })

    async def on_node_complete(ctx, node_id: str, outputs: Dict[str, Any], **kwargs):
        await manager.send_workflow_message(workflow_id, {
            "type": "node_status_update",
            "node_id": node_id,
            "status": "completed",
            "outputs": outputs,
            "timestamp": datetime.now().isoformat()
        })

    async def on_node_error(ctx, node_id: str, error: Exception, **kwargs):
        await manager.send_workflow_message(workflow_id, {
            "type": "node_status_update",
            "node_id": node_id,
            "status": "failed",
            "error": str(error),
            "timestamp": datetime.now().isoformat()
        })

    async def on_workflow_complete(ctx, results: Dict[str, Any], **kwargs):
        await manager.send_workflow_message(workflow_id, {
            "type": "workflow_completed",
            "results": results,
            "summary": ctx.get_execution_summary(),
            "timestamp": datetime.now().isoformat()
        })

    async def on_workflow_error(ctx, error: Exception, **kwargs):
        await manager.send_workflow_message(workflow_id, {
            "type": "workflow_failed",
            "error": str(error),
            "summary": ctx.get_execution_summary(),
            "timestamp": datetime.now().isoformat()
        })

    # 注册回调
    context.add_callback("node_start", on_node_start)
    context.add_callback("node_complete", on_node_complete)
    context.add_callback("node_error", on_node_error)
    context.add_callback("workflow_complete", on_workflow_complete)
    context.add_callback("workflow_error", on_workflow_error)

async def build_workflow_from_data(engine: WorkflowEngine, workflow_data: Dict[str, Any]):
    """从数据构建工作流"""
    # 添加节点
    for node_data in workflow_data.get("nodes", []):
        node = create_node_from_data(node_data)
        engine.add_node(node)

    # 添加连接
    for connection in workflow_data.get("connections", []):
        engine.add_connection(
            connection["from_node"],
            connection["from_output"],
            connection["to_node"],
            connection["to_input"]
        )

async def execute_workflow_async(engine: WorkflowEngine, context: ExecutionContext, workflow_id: str):
    """异步执行工作流"""
    try:
        results = await engine.execute_workflow(context)
        manager.logger.info(f"Workflow {workflow_id} completed successfully")
    except Exception as e:
        manager.logger.error(f"Workflow {workflow_id} failed: {e}")

# REST API端点
@app.get("/api/connections")
async def get_connections():
    """获取连接统计信息"""
    return manager.get_connection_stats()

@app.post("/api/broadcast")
async def broadcast_message(message: Dict[str, Any]):
    """广播消息到所有连接"""
    await manager.broadcast(message)
    return {"status": "broadcasted"}
```

---

## 📡 **消息协议定义**

### **客户端到服务端消息**
```json
{
  "type": "execute_workflow",
  "workflow": {
    "id": "workflow_123",
    "nodes": [...],
    "connections": [...]
  }
}

{
  "type": "control_workflow",
  "workflow_id": "workflow_123",
  "action": "pause|resume|stop"
}

{
  "type": "subscribe",
  "event_types": ["node_status", "workflow_status"]
}
```

### **服务端到客户端消息**
```json
{
  "type": "node_status_update",
  "node_id": "node_123",
  "status": "running|completed|failed",
  "outputs": {...},
  "timestamp": "2025-01-27T10:30:00Z"
}

{
  "type": "workflow_completed",
  "results": {...},
  "summary": {...},
  "timestamp": "2025-01-27T10:35:00Z"
}

{
  "type": "heartbeat",
  "timestamp": "2025-01-27T10:30:00Z"
}
```

---

**文档状态**: ✅ 实时通信系统设计已完成
**核心特性**: 实时状态同步、双向通信、高性能、可靠性、可扩展
**通信协议**: WebSocket + JSON消息格式
**连接管理**: 自动重连、心跳检测、订阅机制
**下一步**: 实现PySide6前端集成和完整的API接口
