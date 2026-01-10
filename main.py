import logging
from docx import Document
from anonymizer.anonymizer import Anonymizer
from anonymizer.doc_handler import DocProcessor
import argparse

logging.basicConfig(
    filename="logs/anonymizer.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DOCX Anonimleştirme Aracı")
    parser.add_argument("--input", required=True, help="Girdi DOCX dosyası")
    parser.add_argument("--output", required=True, help="Anonimleştirilmiş DOCX")
    parser.add_argument("--mapping", required=True, help="Mapping CSV dosyası")
    parser.add_argument("--config", required=True, help="Kurum & Unvan JSON")
    args = parser.parse_args()

    try:
        logging.info("islem basladi")

        doc = Document(args.input)
        anonymizer = Anonymizer(config_path=args.config)

        processor = DocProcessor(anonymizer)
        processor.anonymize_document(doc)

        doc.save(args.output)
        anonymizer.save_mapping(args.mapping)

        logging.info(f"Basarili: {args.output}")

    except Exception as e:
        logging.error(f"Hata olustu: {e}")
        print(f"Hata: {e}")
