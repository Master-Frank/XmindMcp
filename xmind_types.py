from typing import TypedDict, Literal, List, Dict, Any, Optional


class Stats(TypedDict, total=False):
    total_nodes: int
    max_depth: int
    titles_count: int
    leaf_nodes: int
    branch_count: int


class ErrorResponse(TypedDict, total=False):
    status: Literal["error"]
    message: str
    error_code: Optional[str]


class ReadXmindData(TypedDict, total=False):
    format: Literal["xmind"]
    source_format: str
    structure: Dict[str, Any]


class ReadXmindSuccess(TypedDict, total=False):
    status: Literal["success"]
    message: str
    data: ReadXmindData
    stats: Stats


ReadXmindResult = ReadXmindSuccess | ErrorResponse


class TranslateTitlesData(TypedDict, total=False):
    source_file: str
    output_file: str


class TranslateTitlesSuccess(TypedDict, total=False):
    status: Literal["success"]
    message: str
    data: TranslateTitlesData


TranslateTitlesResult = TranslateTitlesSuccess | ErrorResponse


class CreateMindMapData(TypedDict, total=False):
    filename: str
    title: str
    topics_count: int
    output_path: Optional[str]
    absolute_path: Optional[str]
    file_size: Optional[int]


class CreateMindMapSuccess(TypedDict, total=False):
    status: Literal["success"]
    message: str
    data: CreateMindMapData


CreateMindMapResult = CreateMindMapSuccess | ErrorResponse


class AnalyzeData(TypedDict, total=False):
    filename: str
    structure_analysis: Dict[str, Any]


class AnalyzeSuccess(TypedDict, total=False):
    status: Literal["success"]
    message: str
    data: AnalyzeData
    stats: Stats


AnalyzeResult = AnalyzeSuccess | ErrorResponse


class ConvertData(TypedDict, total=False):
    source_file: str
    output_file: str
    filename: Optional[str]


class ConvertSuccess(TypedDict, total=False):
    status: Literal["success"]
    message: str
    data: ConvertData


ConvertResult = ConvertSuccess | ErrorResponse


class XmindFileEntry(TypedDict, total=False):
    name: str
    path: str
    relative_path: str
    size: int
    modified: float


class ListFilesData(TypedDict, total=False):
    directory: str
    recursive: bool
    pattern: Optional[str]
    max_depth: Optional[int]
    file_count: int
    files: List[XmindFileEntry]


class ListFilesSuccess(TypedDict, total=False):
    status: Literal["success"]
    message: str
    data: ListFilesData


ListFilesResult = ListFilesSuccess | ErrorResponse