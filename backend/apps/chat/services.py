import time
from django.conf import settings
from infrastructure.llm.deepseek_client import DeepSeekClient
from .models import Conversation, Message, LLMCall
from .prompts import SYSTEM_PROMPT, RAG_CONTEXT_TEMPLATE


class ChatConfigError(Exception):
    pass


class ChatService:
    def __init__(self):
        self.llm = DeepSeekClient()

    def complete(self, project_id: int, conversation_id: int, message: str, use_knowledge: bool = True) -> dict:
        if not getattr(settings, "DEEPSEEK_API_KEY", "").strip():
            raise ChatConfigError("DEEPSEEK_API_KEY 未配置，请先在 /opt/ai-work-CICD/.env 中填写 DeepSeek API Key")

        conversation = Conversation.objects.get(id=conversation_id, project_id=project_id)

        # Save user message
        Message.objects.create(
            conversation=conversation, role="user", content=message
        )

        # Build context
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Add knowledge context
        references = []
        if use_knowledge:
            from apps.knowledge.search import search_chunks
            chunks = search_chunks(project_id, message, top_k=5)
            if chunks:
                context = "\n\n".join(
                    f"[Document: {c['document_title']}]\n{c['content']}" for c in chunks
                )
                messages.append({
                    "role": "system",
                    "content": RAG_CONTEXT_TEMPLATE.format(context=context),
                })
                references = chunks

        # Add conversation history (last 10)
        history = Message.objects.filter(conversation=conversation).order_by("-created_at")[:10]
        for msg in reversed(history):
            messages.append({"role": msg.role, "content": msg.content})

        # Call LLM
        start = time.time()
        response = self.llm.chat(messages)
        elapsed = int((time.time() - start) * 1000)

        answer = response["choices"][0]["message"]["content"]
        usage = response.get("usage", {})

        # Save assistant message
        Message.objects.create(
            conversation=conversation, role="assistant", content=answer
        )

        # Save LLM call log
        LLMCall.objects.create(
            project_id=project_id,
            conversation=conversation,
            provider="deepseek",
            model_name=settings.DEEPSEEK_MODEL,
            request_payload={"messages": messages},
            response_payload={"answer_length": len(answer)},
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            latency_ms=elapsed,
            status="success",
        )

        # Auto-title conversation on first exchange
        if Message.objects.filter(conversation=conversation).count() <= 2:
            conversation.title = message[:80] + ("..." if len(message) > 80 else "")
            conversation.save(update_fields=["title"])

        return {
            "answer": answer,
            "references": references,
        }
