import logging
from docx import Document
from anonymizer.anonymizer import Anonymizer
from anonymizer.doc_handler import DocProcessor
import argparse

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DOCX Anonimleştirme Aracı")
    parser.add_argument("--input", required=True, help="Girdi DOCX dosyası")
    parser.add_argument("--output", required=True, help="Anonimleştirilmiş DOCX")
    parser.add_argument("--mapping", required=True, help="Mapping CSV dosyası")
    parser.add_argument("--config", required=True, help="Kurum ve unvan JSON config dosyası")
    args = parser.parse_args()

    try:
        doc = Document(args.input)
        anonymizer = Anonymizer(config_path=args.config)
        processor = DocProcessor(anonymizer)
        processor.anonymize_document(doc)
        doc.save(args.output)
        logging.info(f"Word dosyası başarıyla kaydedildi: {args.output}")
        anonymizer.save_mapping(args.mapping)
    except FileNotFoundError:
        logging.error(f"Girdi dosyası bulunamadı: {args.input}")
    except Exception as e:
        logging.error(f"Hata oluştu: {e}")
