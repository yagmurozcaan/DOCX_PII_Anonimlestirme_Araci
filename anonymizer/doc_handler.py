from docx import Document
from .anonymizer import Anonymizer

class DocProcessor:
    """
    DOCX belgelerini Anonymizer kullanarak işleyen sınıf.
    """
    def __init__(self, anonymizer: Anonymizer):
        self.anonymizer = anonymizer

    def anonymize_document(self, doc: Document) -> Document:
        for p in doc.paragraphs:
            p.text = self.anonymizer.anonymize_text(p.text)
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    cell.text = self.anonymizer.anonymize_text(cell.text)
        return doc
