"""Type definitions and validation for template specifications using Pydantic."""

from typing import Optional, List
from pathlib import Path
from pydantic import BaseModel, Field, model_validator


ROOT = Path(__file__).resolve().parents[1]
BLOCKS_DIR = ROOT / "src" / "blocks"


class TemplateSpec(BaseModel):
    """Template specification with validation."""
    id: str = Field(..., min_length=1,
                    description="Unique template identifier")
    size: str = Field(..., min_length=1,
                      description="Template size (small, medium, large)")
    language: str = Field(..., min_length=1,
                          description="Programming language (r, python, etc.)")
    setup: str = Field(..., min_length=1, description="Setup command to run")
    run: str = Field(..., min_length=1, description="Main command to run")
    blocks: List[str] = Field(..., min_length=1,
                              description="List of blocks to compose")
    test: Optional[str] = Field(
        None, description="Optional test command to run")

    @model_validator(mode="after")
    def validate_blocks(self) -> "TemplateSpec":
        """Ensure blocks are unique and exist in the filesystem."""
        # Check for duplicates
        if len(self.blocks) != len(set(self.blocks)):
            duplicates = [b for b in self.blocks if self.blocks.count(b) > 1]
            raise ValueError(
                f"Duplicate blocks in template '{self.id}': "
                f"{', '.join(set(duplicates))}"
            )

        # Check that each block exists
        for block in self.blocks:
            block_path = BLOCKS_DIR / block
            if not block_path.exists():
                raise ValueError(
                    f"Block '{block}' in template '{self.id}' does not exist at "
                    f"{block_path.relative_to(ROOT)}"
                )

        return self


class Manifest(BaseModel):
    """Template manifest structure with validation."""
    release: str = Field(..., min_length=1,
                         description="RECAP image release version")
    templates: List[TemplateSpec] = Field(...,
                                          min_length=1, description="List of templates")

    @model_validator(mode="after")
    def validate_template_ids_unique(self) -> "Manifest":
        """Ensure all template IDs are unique."""
        ids = [t.id for t in self.templates]
        if len(ids) != len(set(ids)):
            duplicates = [id for id in ids if ids.count(id) > 1]
            raise ValueError(
                f"Duplicate template IDs: {', '.join(set(duplicates))}")
        return self
