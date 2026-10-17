"""Parser contract: input files become a canonical Document."""
from abc import ABC, abstractmethod
from pathlib import Path
from ..models import Document, Topic


def create_topic(title, children=None):
    return Topic(title, list(children or []))


def create_document(title, children):
    return Document(Topic(title, list(children)))


class BaseParser(ABC):
    def __init__(self, file_path):
        self.file_path = Path(file_path)

    @abstractmethod
    def parse(self) -> Document:
        raise NotImplementedError

    def extract_title(self, content):
        return self.file_path.stem
