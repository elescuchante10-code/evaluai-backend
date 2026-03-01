"""
DocumentParserAgent - Extrae texto de PDF, DOCX, TXT
"""
import io
from typing import Optional
from pathlib import Path

from agent_squad.agents import Agent
from agent_squad.types import ConversationMessage, ParticipantRole
from agent_squad.utils import Logger


try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


class DocumentParserAgent(Agent):
    """
    Agente especializado en extraer texto de documentos
    Soporta: PDF, DOCX, TXT
    """
    
    SUPPORTED_FORMATS = ['.pdf', '.docx', '.txt', '.doc']
    
    def __init__(self, options):
        super().__init__(options)
        Logger.info(f"DocumentParserAgent inicializado. Formatos: {self.SUPPORTED_FORMATS}")
    
    async def process_request(
        self,
        input_text: str,
        user_id: str,
        session_id: str,
        chat_history: list,
        additional_params: Optional[dict] = None
    ) -> ConversationMessage:
        """
        input_text: En este caso es el path del archivo o bytes
        additional_params debe contener 'filename' y opcionalmente 'file_bytes'
        """
        try:
            if not additional_params:
                return self._error_response("No se proporcionaron parámetros del archivo")
            
            filename = additional_params.get('filename', '')
            file_bytes = additional_params.get('file_bytes')
            
            if not filename:
                return self._error_response("Nombre de archivo no proporcionado")
            
            extension = Path(filename).suffix.lower()
            
            if extension not in self.SUPPORTED_FORMATS:
                return self._error_response(f"Formato no soportado: {extension}")
            
            # Extraer texto según formato
            if extension == '.pdf':
                text = await self._extract_pdf(file_bytes)
            elif extension in ['.docx', '.doc']:
                text = await self._extract_docx(file_bytes)
            elif extension == '.txt':
                text = await self._extract_txt(file_bytes)
            else:
                return self._error_response(f"Formato no implementado: {extension}")
            
            # Contar palabras
            word_count = len(text.split())
            
            return ConversationMessage(
                role=ParticipantRole.ASSISTANT.value,
                content=[{"text": text}],
                metadata={
                    "filename": filename,
                    "extension": extension,
                    "word_count": word_count,
                    "char_count": len(text),
                    "success": True
                }
            )
            
        except Exception as e:
            Logger.error(f"Error parseando documento: {str(e)}")
            return self._error_response(f"Error procesando archivo: {str(e)}")
    
    async def _extract_pdf(self, file_bytes: bytes) -> str:
        """Extrae texto de PDF"""
        if not PYPDF2_AVAILABLE:
            raise ImportError("PyPDF2 no está instalado. Instala: pip install PyPDF2")
        
        pdf_file = io.BytesIO(file_bytes)
        reader = PyPDF2.PdfReader(pdf_file)
        
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        
        return text.strip()
    
    async def _extract_docx(self, file_bytes: bytes) -> str:
        """Extrae texto de DOCX"""
        if not DOCX_AVAILABLE:
            raise ImportError("python-docx no está instalado. Instala: pip install python-docx")
        
        doc_file = io.BytesIO(file_bytes)
        doc = Document(doc_file)
        
        text = []
        for para in doc.paragraphs:
            if para.text.strip():
                text.append(para.text)
        
        return "\n".join(text)
    
    async def _extract_txt(self, file_bytes: bytes) -> str:
        """Extrae texto de TXT"""
        # Intentar diferentes encodings
        encodings = ['utf-8', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                return file_bytes.decode(encoding)
            except UnicodeDecodeError:
                continue
        
        # Si ninguno funciona, forzar latin-1 (no falla nunca)
        return file_bytes.decode('latin-1')
    
    def _error_response(self, message: str) -> ConversationMessage:
        """Genera respuesta de error"""
        return ConversationMessage(
            role=ParticipantRole.ASSISTANT.value,
            content=[{"text": ""}],
            metadata={
                "error": True,
                "error_message": message,
                "success": False
            }
        )
