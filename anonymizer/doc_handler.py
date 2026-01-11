from docx import Document
from anonymizer.anonymizer import Anonymizer

class DocProcessor:
    """
    DOCX belgelerini Anonymizer kullanarak işleyen sınıf.
    Stil korunur ve tüm placeholder'lar oluşturulur.
    """
    def __init__(self, anonymizer: Anonymizer):
        self.anonymizer = anonymizer

    def anonymize_paragraph(self, paragraph):
        full_text = paragraph.text
        if not full_text.strip():
            return

        anonymized_text = self.anonymizer.anonymize_text(full_text)

        for run in paragraph.runs:
            run.text = ""

        if paragraph.runs:
            paragraph.runs[0].text = anonymized_text
        else:
            paragraph.add_run(anonymized_text)

    def anonymize_document(self, doc: Document) -> Document:
        for p in doc.paragraphs:
            self.anonymize_paragraph(p)

        # Tablolar
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for p in cell.paragraphs:
                        self.anonymize_paragraph(p)

        return doc
