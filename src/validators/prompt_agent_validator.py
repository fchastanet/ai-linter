import re
from pathlib import Path
from typing import Any

from lib.log import Logger, LogLevel
from lib.parser import Parser
from validators.file_reference_validator import FileReferenceValidator


class PromptAgentValidator:
    """Validator for .github/prompts and .github/agents directories"""

    MAX_TOKEN_COUNT = 5000
    MAX_LINE_COUNT = 500

    def __init__(
        self,
        logger: Logger,
        parser: Parser,
        file_ref_validator: FileReferenceValidator,
        missing_agents_level: str = "WARNING",
    ):
        self.logger = logger
        self.parser = parser
        self.file_ref_validator = file_ref_validator
        self.missing_agents_level = (
            LogLevel.from_string(missing_agents_level)
            if missing_agents_level in ["ERROR", "WARNING", "INFO"]
            else LogLevel.WARNING
        )

    def extract_file_references(self, content: str) -> set[str]:
        """Extract file references from markdown content"""
        references = set()

        # Markdown links and images: [text](path) or ![alt](path)
        link_pattern = r"!?\[([^\]]*)\]\(([^)]+)\)"
        for match in re.finditer(link_pattern, content):
            ref = match.group(2)
            # Remove URL anchors and query strings
            ref = ref.split("#")[0].split("?")[0]
            if ref and not ref.startswith(("http://", "https://", "mailto:", "#")):
                references.add(ref)

        # HTML img/src tags: <img src="path">
        img_pattern = r'<img[^>]+src=["\']([^"\']+)["\']'
        for match in re.finditer(img_pattern, content):
            ref = match.group(1)
            if ref and not ref.startswith(("http://", "https://", "data:")):
                references.add(ref)

        # Attachment references: <attachment filePath="path">
        attachment_pattern = r'<attachment[^>]+filePath=["\']([^"\']+)["\']'
        for match in re.finditer(attachment_pattern, content):
            references.add(match.group(1))

        return references

    def validate_agents_md_exists(self, project_dir: str | Path) -> tuple[int, int]:
        """Check if AGENTS.md exists in the root directory"""
        project_dir = Path(project_dir)
        agents_md = project_dir / "AGENTS.md"

        if not agents_md.exists():
            self.logger.log(
                self.missing_agents_level,
                "agents-file-missing",
                "AGENTS.md file is missing in the root directory. "
                "Consider creating one to provide AI assistant guidance.",
                project_dir,
            )
            if self.missing_agents_level == LogLevel.ERROR:
                return 0, 1
            elif self.missing_agents_level == LogLevel.WARNING:
                return 1, 0

        return 0, 0

    def extract_tool_references(self, content: str) -> set[str]:
        """Extract tool references from content"""
        tools = set()

        # Look for tool references in various formats
        # - tool: tool_name
        # - allowed-tools: [tool1, tool2]
        # - uses tool_name
        tool_patterns = [
            r"tool:\s*([a-zA-Z0-9_-]+)",
            r"allowed-tools:\s*\[(.*?)\]",
            r"uses\s+([a-zA-Z0-9_-]+)",
            r"tool\s+`([a-zA-Z0-9_-]+)`",
        ]

        for pattern in tool_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                if "," in match.group(1):
                    # Handle comma-separated lists
                    for tool in match.group(1).split(","):
                        tool = tool.strip().strip("\"'")
                        if tool:
                            tools.add(tool)
                else:
                    tool = match.group(1).strip().strip("\"'")
                    if tool:
                        tools.add(tool)

        return tools

    def extract_skill_references(self, content: str) -> set[str]:
        """Extract skill references from content"""
        skills = set()

        # Look for skill references
        # - skill: skill_name
        # - uses skill skill_name
        # - SKILL.md references
        skill_patterns = [
            r"skill:\s*([a-zA-Z0-9_-]+)",
            r"uses\s+skill\s+([a-zA-Z0-9_-]+)",
            r"SKILL\.md.*?([a-zA-Z0-9_-]+)",
            r"skill\s+`([a-zA-Z0-9_-]+)`",
        ]

        for pattern in skill_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                skill = match.group(1).strip()
                if skill:
                    skills.add(skill)

        return skills

    def validate_prompt_or_agent_file(
        self, file_path: str | Path, project_dir: str | Path
    ) -> tuple[int, int, dict[str, Any]]:
        """
        Validate a single prompt or agent file
        Returns tuple of (warning_count, error_count, metadata_dict)
        """
        file_path = Path(file_path)
        project_dir = Path(project_dir)

        if not file_path.exists():
            return 0, 0, {}

        try:
            content = file_path.read_text()
        except Exception as e:
            self.logger.log(
                LogLevel.ERROR,
                "file-read-error",
                f"Failed to read file: {e}",
                file_path,
            )
            return 0, 1, {}

        warnings = 0
        errors = 0
        metadata: dict[str, Any] = {}

        # Check token count and line count
        lines = content.split("\n")
        line_count = len(lines)
        token_count = len(content.split())  # Simple token count approximation

        metadata["line_count"] = line_count
        metadata["token_count"] = token_count

        if line_count > self.MAX_LINE_COUNT:
            self.logger.log(
                LogLevel.WARNING,
                "prompt-content-too-long",
                f"Content has {line_count} lines (max: {self.MAX_LINE_COUNT}). "
                f"Consider splitting into multiple files.",
                file_path,
            )
            warnings += 1

        if token_count > self.MAX_TOKEN_COUNT:
            self.logger.log(
                LogLevel.WARNING,
                "prompt-token-count-exceeded",
                f"Content has approximately {token_count} tokens (max: {self.MAX_TOKEN_COUNT}). "
                f"Consider reducing content size.",
                file_path,
            )
            warnings += 1

        # Extract and validate references
        file_refs = self.extract_file_references(content)
        metadata["file_references"] = list(file_refs)

        for ref in file_refs:
            # Try to resolve the reference
            if ref.startswith("/"):
                ref_path = project_dir / ref.lstrip("/")
            else:
                ref_path = file_path.parent / ref

            if not ref_path.exists():
                self.logger.log(
                    LogLevel.ERROR,
                    "file-reference-not-found",
                    f"Referenced file not found: {ref}",
                    file_path,
                )
                errors += 1

        # Extract tools and skills
        tools = self.extract_tool_references(content)
        skills = self.extract_skill_references(content)

        metadata["tools"] = list(tools)
        metadata["skills"] = list(skills)

        if tools:
            self.logger.log(
                LogLevel.INFO,
                "tools-found",
                f"Found {len(tools)} tool references: {', '.join(sorted(tools))}",
                file_path,
            )

        if skills:
            self.logger.log(
                LogLevel.INFO,
                "skills-found",
                f"Found {len(skills)} skill references: {', '.join(sorted(skills))}",
                file_path,
            )

        return warnings, errors, metadata

    def validate_prompt_agent_directories(
        self, project_dir: str | Path, prompt_dirs: list[str], agent_dirs: list[str]
    ) -> tuple[int, int]:
        """
        Validate all files in prompt and agent directories
        Returns tuple of (warning_count, error_count)
        """
        project_dir = Path(project_dir)
        total_warnings = 0
        total_errors = 0

        # Validate AGENTS.md exists
        agents_warnings, agents_errors = self.validate_agents_md_exists(project_dir)
        total_warnings += agents_warnings
        total_errors += agents_errors

        # Check prompt directories
        for prompt_dir in prompt_dirs:
            prompt_path = project_dir / prompt_dir
            if prompt_path.exists() and prompt_path.is_dir():
                self.logger.log(
                    LogLevel.INFO,
                    "validating-prompt-dir",
                    f"Validating prompt directory: {prompt_dir}",
                    prompt_path,
                )

                for md_file in prompt_path.rglob("*.md"):
                    warnings, errors, metadata = self.validate_prompt_or_agent_file(md_file, project_dir)
                    total_warnings += warnings
                    total_errors += errors
            else:
                self.logger.log(
                    LogLevel.DEBUG,
                    "prompt-dir-not-found",
                    f"Prompt directory not found: {prompt_dir}",
                    project_dir,
                )

        # Check agent directories
        for agent_dir in agent_dirs:
            agent_path = project_dir / agent_dir
            if agent_path.exists() and agent_path.is_dir():
                self.logger.log(
                    LogLevel.INFO,
                    "validating-agent-dir",
                    f"Validating agent directory: {agent_dir}",
                    agent_path,
                )

                for md_file in agent_path.rglob("*.md"):
                    warnings, errors, metadata = self.validate_prompt_or_agent_file(md_file, project_dir)
                    total_warnings += warnings
                    total_errors += errors
            else:
                self.logger.log(
                    LogLevel.DEBUG,
                    "agent-dir-not-found",
                    f"Agent directory not found: {agent_dir}",
                    project_dir,
                )

        return total_warnings, total_errors
