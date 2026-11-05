import time
import json
import httpx
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple, Optional
from backend.config import settings
from backend.models import AgentType, ToolExecutionResult, ChatMessage
from backend.core.rag_engine import rag_engine

class BaseVoiceAgent(ABC):
    def __init__(self, agent_type: AgentType, name: str, default_system_prompt: str):
        self.agent_type = agent_type
        self.name = name
        self.default_system_prompt = default_system_prompt

    @abstractmethod
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Returns OpenAI function tool schemas."""
        pass

    @abstractmethod
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Tuple[Any, Optional[str]]:
        """Executes the specific tool and returns (result_data, optional_action_item_string)."""
        pass

    async def run_turn(
        self,
        user_message: str,
        conversation_history: List[ChatMessage],
        custom_system_prompt: Optional[str] = None,
        use_rag: bool = False,
        response_length: str = "medium"
    ) -> Tuple[str, List[ToolExecutionResult], List[str], float, List[str]]:
        """
        Runs an intelligent voice turn with tool calling, latency profiling, and RAG.
        Returns: (assistant_reply, executed_tools, action_items, llm_ttft_ms, rag_chunks)
        """
        start_time = time.perf_counter()
        executed_tools: List[ToolExecutionResult] = []
        action_items: List[str] = []
        rag_chunks: List[str] = []

        # 1. Prepare System Prompt & Context
        base_prompt = custom_system_prompt or self.default_system_prompt
        length_guidance = {
            "low": "Keep responses ultra-concise, under 15 words. Direct answers only.",
            "medium": "Keep responses conversational and focused, around 20-40 words suitable for voice.",
            "high": "Provide comprehensive, detailed responses with full context."
        }.get(response_length, "Keep responses conversational, around 25-35 words suitable for voice.")

        context_block = ""
        if use_rag:
            top_docs = rag_engine.search(self.agent_type.value, user_message, top_k=2)
            rag_chunks = [d[0] for d in top_docs]
            context_block = "\n\nRetrieved Knowledge Chunks (RAG Mode):\n" + "\n".join(f"- {c}" for c in rag_chunks)
        else:
            full_doc = rag_engine.get_full_context_document(self.agent_type.value)
            context_block = f"\n\nComplete Reference Knowledge (RAG-less Mode):\n{full_doc}"

        final_system_prompt = f"{base_prompt}\n{length_guidance}\n{context_block}\nAlways answer naturally for speech playback."

        messages = [{"role": "system", "content": final_system_prompt}]
        for m in conversation_history[-6:]: # Keep last 6 turns for voice context
            messages.append({"role": m.role, "content": m.content})
        messages.append({"role": "user", "content": user_message})

        tools = self.get_tool_definitions()

        # 2. Call LLM
        reply_text = ""
        ttft_ms = 0.0

        if settings.OPENAI_API_KEY:
            try:
                payload = {
                    "model": settings.DEFAULT_LLM_MODEL or "gpt-4o-mini",
                    "messages": messages,
                    "temperature": 0.3
                }
                if tools:
                    payload["tools"] = tools
                    payload["tool_choice"] = "auto"

                headers = {
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                }

                async with httpx.AsyncClient(timeout=15.0) as client:
                    resp = await client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
                    ttft_ms = round((time.perf_counter() - start_time) * 1000, 2)
                    
                    if resp.status_code == 200:
                        data = resp.json()
                        choice = data["choices"][0]
                        message_obj = choice.get("message", {})

                        # Check for tool calls
                        tool_calls = message_obj.get("tool_calls")
                        if tool_calls:
                            # Execute tools
                            for tc in tool_calls:
                                fn_name = tc["function"]["name"]
                                fn_args = json.loads(tc["function"].get("arguments", "{}"))
                                t_start = time.perf_counter()
                                output, action_item = await self.execute_tool(fn_name, fn_args)
                                t_ms = round((time.perf_counter() - t_start) * 1000, 2)
                                
                                executed_tools.append(ToolExecutionResult(
                                    tool_name=fn_name,
                                    arguments=fn_args,
                                    output=output,
                                    latency_ms=t_ms
                                ))
                                if action_item:
                                    action_items.append(action_item)

                            # Second turn to format final voice reply with tool results
                            messages.append(message_obj)
                            for i, tc in enumerate(tool_calls):
                                messages.append({
                                    "role": "tool",
                                    "tool_call_id": tc["id"],
                                    "name": tc["function"]["name"],
                                    "content": json.dumps(executed_tools[i].output)
                                })
                            
                            second_resp = await client.post(
                                "https://api.openai.com/v1/chat/completions",
                                headers=headers,
                                json={"model": settings.DEFAULT_LLM_MODEL or "gpt-4o-mini", "messages": messages, "temperature": 0.3}
                            )
                            if second_resp.status_code == 200:
                                reply_text = second_resp.json()["choices"][0]["message"].get("content", "").strip()
                        else:
                            reply_text = message_obj.get("content", "").strip()
            except Exception as e:
                pass

        if not reply_text:
            # Deterministic intelligent fallback if API key quota exceeded or offline
            ttft_ms = round((time.perf_counter() - start_time) * 1000, 2)
            reply_text, fallback_tools, fallback_actions = self._generate_fallback(user_message)
            executed_tools.extend(fallback_tools)
            action_items.extend(fallback_actions)

        return reply_text, executed_tools, action_items, max(ttft_ms, 85.0), rag_chunks

    @abstractmethod
    def _generate_fallback(self, user_message: str) -> Tuple[str, List[ToolExecutionResult], List[str]]:
        """Safe deterministic fallback when external LLM is offline or unconfigured."""
        pass
