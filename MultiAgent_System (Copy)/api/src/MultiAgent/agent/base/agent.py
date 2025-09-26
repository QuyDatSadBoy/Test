# # src/agents/base/agent.py
# from __future__ import annotations
# import uuid
# from datetime import datetime, timezone
# from typing import Any, Dict, List, Optional

# import sys
# import os 
# root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
# sys.path.insert(0, root_path)

# from crewai import Agent as CrewAgent, Task as CrewTask, Crew

# from shared.schemas import (
#     AgentType,
#     TaskStatus,
#     AgentTaskCreate,
#     AgentTaskResponse,
#     OrchestrationPlan,
#     OrchestrationStep,
# )


# class AgentBase:
#     """
#     Base class cho tất cả agents trong hệ thống.
#     Chuẩn hóa:
#     - Nhận AgentTaskCreate
#     - Build OrchestrationPlan
#     - Thực thi CrewAI (agents, tasks)
#     - Trả về AgentTaskResponse
#     """

#     def __init__(self, agent_type: AgentType, role: str, goal: str, backstory: str):
#         self.agent_type = agent_type
#         self._crew_agent = CrewAgent(
#             role=role,
#             goal=goal,
#             backstory=backstory,
#             verbose=False,
#         )

#     # ----- Override trong agent con -----
#     def build_plan(self, task: AgentTaskCreate) -> OrchestrationPlan:
#         """Xây dựng OrchestrationPlan (override ở agent con)."""
#         raise NotImplementedError

#     def build_tasks(self, plan: OrchestrationPlan, task: AgentTaskCreate) -> List[CrewTask]:
#         """Xây dựng danh sách CrewTask từ OrchestrationPlan (override ở agent con)."""
#         raise NotImplementedError

#     # ----- Common run -----
#     def run(self, task: AgentTaskCreate) -> AgentTaskResponse:
#         start = datetime.now(timezone.utc)
#         task_id = uuid.uuid4()

#         if task.agent_type != self.agent_type:
#             return self._fail_resp(task_id, task, start, f"{self.agent_type} chỉ xử lý agent_type={self.agent_type}")

#         try:
#             plan = self.build_plan(task)
#             crew_tasks = self.build_tasks(plan, task)

#             crew = Crew(
#                 agents=[self._crew_agent],
#                 tasks=crew_tasks,
#                 process="sequential",
#                 verbose=False,
#             )
#             result = crew.kickoff()

#             completed = datetime.now(timezone.utc)
#             return AgentTaskResponse(
#                 id=task_id,
#                 agent_type=self.agent_type,
#                 input_data=task.input_data,
#                 priority=task.priority,
#                 status=TaskStatus.COMPLETED,
#                 output_data=result if isinstance(result, dict) else {"result": str(result)},
#                 created_at=start,
#                 completed_at=completed,
#             )

#         except Exception as ex:
#             return self._fail_resp(task_id, task, start, str(ex))

#     # ----- Helper -----
#     def _fail_resp(self, task_id, base: AgentTaskCreate, created_at: datetime, msg: str) -> AgentTaskResponse:
#         return AgentTaskResponse(
#             id=task_id,
#             agent_type=base.agent_type,
#             input_data=base.input_data,
#             priority=base.priority,
#             status=TaskStatus.FAILED,
#             output_data=None,
#             error_message=msg,
#             created_at=created_at,
#             completed_at=datetime.now(timezone.utc),
#         )
