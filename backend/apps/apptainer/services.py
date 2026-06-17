from django.conf import settings
from infrastructure.llm.deepseek_client import DeepSeekClient
from infrastructure.storage.local_storage import LocalStorage
from apps.chat.prompts import APPTAINER_GENERATE_PROMPT
from apps.chat.models import Message
from apps.common.storage import generate_storage_path
from .models import ApptainerDefinition
from .validators import validate_definition_content


class ApptainerService:
    def __init__(self):
        self.llm = DeepSeekClient()
        self.storage = LocalStorage()

    def persist_definition_file(self, definition: ApptainerDefinition) -> ApptainerDefinition:
        filename = f"{definition.name or 'definition'}.def"
        relative_path, _ = generate_storage_path("apptainer/definitions", filename)
        self.storage.write(relative_path, definition.content.encode("utf-8"))
        definition.storage_path = relative_path
        definition.save(update_fields=["storage_path", "updated_at"])
        return definition

    def create_definition(self, **kwargs) -> ApptainerDefinition:
        errors = validate_definition_content(kwargs.get("content", ""))
        if errors:
            raise ValueError("; ".join(errors))
        definition = ApptainerDefinition.objects.create(**kwargs)
        return self.persist_definition_file(definition)

    def _extract_definition_content(self, answer: str) -> str:
        """Extract the definition body from model output while rejecting prose-only answers."""
        lines = answer.replace("\r\n", "\n").split("\n")
        fenced_blocks: list[list[str]] = []
        current_block: list[str] | None = None

        for line in lines:
            if line.strip().startswith("```"):
                if current_block is None:
                    current_block = []
                else:
                    fenced_blocks.append(current_block)
                    current_block = None
                continue
            if current_block is not None:
                current_block.append(line)

        candidates = ["\n".join(block).strip() for block in fenced_blocks]
        candidates.append(answer.strip())

        for candidate in candidates:
            candidate_lines = candidate.split("\n")
            def_lines = []
            in_def = False
            for line in candidate_lines:
                if line.lstrip().startswith("Bootstrap:"):
                    in_def = True
                if in_def:
                    def_lines.append(line)
            content = "\n".join(def_lines).strip()
            if "Bootstrap:" in content and "From:" in content:
                return content

        return answer.strip()

    def _request_definition(self, messages: list[dict], requirement: str) -> str:
        response = self.llm.chat(messages, temperature=0.1, max_tokens=4000)
        answer = response["choices"][0]["message"].get("content", "")
        def_content = self._extract_definition_content(answer)
        errors = validate_definition_content(def_content)
        if not errors:
            return def_content

        retry_messages = messages + [
            {
                "role": "system",
                "content": (
                    "The previous answer was invalid because required sections were missing "
                    "or unsafe command text appeared in the output. "
                    + "\nReturn ONLY a valid Apptainer definition file. "
                    "The first non-empty line must be 'Bootstrap:'. Include 'From:'."
                ),
            },
            {"role": "user", "content": requirement},
        ]
        retry_response = self.llm.chat(retry_messages, temperature=0.0, max_tokens=4000)
        retry_answer = retry_response["choices"][0]["message"].get("content", "")
        return self._extract_definition_content(retry_answer)

    def generate_definition(
        self,
        project_id: int,
        conversation_id: int,
        requirement: str = "",
        use_knowledge: bool = True,
        created_by=None,
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

        def_content = self._request_definition(messages, requirement)

        # Generate a name from the first meaningful line
        name = requirement.strip()[:60] if requirement.strip() else "ai-generated"
        name = name.replace("\n", " ").strip()

        # Save definition
        definition = self.create_definition(
            project_id=project_id,
            conversation_id=conversation_id,
            name=name[:80],
            content=def_content,
            created_by=created_by,
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
