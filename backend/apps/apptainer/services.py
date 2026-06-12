from django.conf import settings
from infrastructure.llm.deepseek_client import DeepSeekClient
from apps.chat.prompts import APPTAINER_GENERATE_PROMPT
from apps.chat.models import Message
from .models import ApptainerDefinition


class ApptainerService:
    def __init__(self):
        self.llm = DeepSeekClient()

    def generate_definition(
        self,
        project_id: int,
        conversation_id: int,
        requirement: str = "",
        use_knowledge: bool = True,
    ) -> ApptainerDefinition:
        messages = [{"role": "system", "content": APPTAINER_GENERATE_PROMPT}]

        # Build requirement from conversation if not explicitly provided
        if not requirement.strip() and conversation_id:
            msgs = Message.objects.filter(conversation_id=conversation_id).order_by("created_at")
            conversation_lines = []
            for m in msgs:
                prefix = "用户" if m.role == "user" else "AI"
                conversation_lines.append(f"[{prefix}]: {m.content}")
            requirement = "\n".join(conversation_lines)
        elif not requirement.strip():
            requirement = "Generate a basic Ubuntu 22.04 Apptainer definition"

        # Add knowledge context
        if use_knowledge:
            from apps.knowledge.search import search_chunks
            chunks = search_chunks(project_id, requirement, top_k=3)
            if chunks:
                context = "\n\n".join(
                    f"[{c['document_title']}]\n{c['content']}" for c in chunks
                )
                messages.append({"role": "system", "content": f"Reference content:\n{context}"})

        messages.append({"role": "user", "content": requirement})

        response = self.llm.chat(messages)
        answer = response["choices"][0]["message"]["content"]

        # Extract definition (content before first explanation)
        lines = answer.split("\n")
        def_lines = []
        in_def = False
        for line in lines:
            if line.startswith("Bootstrap:"):
                in_def = True
            if in_def:
                if line.startswith("```") and def_lines:
                    break
                def_lines.append(line)

        def_content = "\n".join(def_lines) or answer

        # Generate a name from the first meaningful line
        name = requirement.strip()[:60] if requirement.strip() else "ai-generated"
        name = name.replace("\n", " ").strip()

        # Save definition
        definition = ApptainerDefinition.objects.create(
            project_id=project_id,
            conversation_id=conversation_id,
            name=name[:80],
            content=def_content,
            created_by=None,
        )
        return definition

    def validate_definition(self, content: str) -> list[str]:
        errors = []
        if "Bootstrap:" not in content:
            errors.append("Missing Bootstrap:")
        if "From:" not in content:
            errors.append("Missing From:")
        from apps.common.constants import DANGEROUS_DEF_PATTERNS
        for d in DANGEROUS_DEF_PATTERNS:
            if d in content.lower():
                errors.append(f"Contains dangerous pattern: {d}")
        return errors
