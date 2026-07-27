import pytest
from pydantic import BaseModel, ValidationError

from opspilot.core.permissions import Permission
from opspilot.core.risk import RiskClass
from opspilot.core.tool import ToolDefinition


class Input(BaseModel):
    value: str


class Output(BaseModel):
    value: str


def test_tool_definition_is_typed() -> None:
    definition = ToolDefinition(
        name="example.echo",
        description="Echo a value.",
        input_model=Input,
        output_model=Output,
        risk=RiskClass.READ,
        permissions=frozenset({Permission.WORKSPACE_READ}),
    )
    assert definition.input_model is Input


def test_tool_name_requires_namespace() -> None:
    with pytest.raises(ValidationError):
        ToolDefinition(
            name="echo",
            description="Echo a value.",
            input_model=Input,
            output_model=Output,
            risk=RiskClass.READ,
        )
