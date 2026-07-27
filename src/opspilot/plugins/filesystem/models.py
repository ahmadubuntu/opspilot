from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ReadFileInput(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    path: str = Field(min_length=1)


class ReadFileOutput(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    content: str


class ListDirectoryInput(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    path: str = "."


class DirectoryEntryOutput(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    name: str
    is_directory: bool


class ListDirectoryOutput(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    entries: list[DirectoryEntryOutput]
