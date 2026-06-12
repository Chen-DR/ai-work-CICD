from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from apps.common.response import success, error
from apps.audit.services import client_ip, log_action
from .models import KnowledgeDocument
from .serializers import KnowledgeDocumentSerializer, KnowledgeChunkSerializer, KnowledgeSearchSerializer
from .services import KnowledgeService
from .tasks import parse_knowledge_document_task


class KnowledgeDocumentViewSet(viewsets.ModelViewSet):
    queryset = KnowledgeDocument.objects.all()
    serializer_class = KnowledgeDocumentSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        qs = super().get_queryset()
        project_id = self.request.query_params.get("project_id")
        if project_id:
            qs = qs.filter(project_id=project_id)
        return qs

    def create(self, request, *args, **kwargs):
        file = request.FILES.get("file")
        if not file:
            return error(40001, "No file provided")

        project_id = request.data.get("project_id")
        if not project_id:
            return error(40001, "project_id is required")

        svc = KnowledgeService()
        if not svc.is_allowed_file(file.name):
            return error(80001, f"File type not supported: {file.name}")

        doc = svc.save_document(
            project_id=int(project_id),
            user_id=request.user.id,
            file=file,
        )
        parse_knowledge_document_task.delay(doc.id)
        log_action(
            request.user,
            "knowledge.upload",
            "knowledge_document",
            doc.id,
            project_id=doc.project_id,
            ip_address=client_ip(request),
            detail={"file_name": doc.file_name, "status": doc.status},
        )
        return success(KnowledgeDocumentSerializer(doc).data, status=201)

    @action(detail=True, methods=["post"])
    def parse(self, request, pk=None):
        doc = self.get_object()
        try:
            parse_knowledge_document_task.delay(doc.id)
            log_action(
                request.user,
                "knowledge.parse",
                "knowledge_document",
                doc.id,
                project_id=doc.project_id,
                ip_address=client_ip(request),
                detail={"file_name": doc.file_name},
            )
            return success({"status": "parsing"})
        except Exception as e:
            return error(50001, f"Parse failed: {str(e)}", status=500)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def search(request):
    ser = KnowledgeSearchSerializer(data=request.data)
    if not ser.is_valid():
        return error(40001, "Invalid parameters", ser.errors)

    svc = KnowledgeService()
    results = svc.search(**ser.validated_data)
    return success({"chunks": results})
