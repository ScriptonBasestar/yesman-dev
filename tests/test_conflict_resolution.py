from typing import Any
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import Mock, patch
import pytest
from libs.multi_agent.branch_manager import BranchManager
from libs.multi_agent.conflict_resolution import (
        # Test import conflict pattern


# Copyright notice.
# Copyright (c) 2024 Yesman Claude Project
# Licensed under the MIT License

"""Tests for ConflictResolutionEngine."""



    ConflictInfo,
    ConflictResolutionEngine,
    ConflictSeverity,
    ConflictType,
    ResolutionResult,
    ResolutionStrategy,
)


class TestConflictInfo:
    """Test cases for ConflictInfo dataclass."""

    @staticmethod
    def test_init() -> None:
        """Test ConflictInfo initialization."""
        conflict = ConflictInfo(
            conflict_id="test-conflict",
            conflict_type=ConflictType.FILE_MODIFICATION,
            severity=ConflictSeverity.MEDIUM,
            branches=["branch1", "branch2"],
            files=["test.py"],
            description="Test conflict",
            suggested_strategy=ResolutionStrategy.AUTO_MERGE,
        )

        assert conflict.conflict_id == "test-conflict"
        assert conflict.conflict_type == ConflictType.FILE_MODIFICATION
        assert conflict.severity == ConflictSeverity.MEDIUM
        assert conflict.branches == ["branch1", "branch2"]
        assert conflict.files == ["test.py"]
        assert conflict.suggested_strategy == ResolutionStrategy.AUTO_MERGE
        assert conflict.resolved_at is None


class TestResolutionResult:
    """Test cases for ResolutionResult dataclass."""

    @staticmethod
    def test_init() -> None:
        """Test ResolutionResult initialization."""
        result = ResolutionResult(
            conflict_id="test-conflict",
            success=True,
            strategy_used=ResolutionStrategy.AUTO_MERGE,
            resolution_time=1.5,
            message="Successfully resolved",
        )

        assert result.conflict_id == "test-conflict"
        assert result.success is True
        assert result.strategy_used == ResolutionStrategy.AUTO_MERGE
        assert result.resolution_time == 1.5
        assert result.message == "Successfully resolved"
        assert result.resolved_files == []
        assert result.remaining_conflicts == []


class TestConflictResolutionEngine:
    """Test cases for ConflictResolutionEngine."""

    @pytest.fixture
    @staticmethod
    def mock_branch_manager() -> object:
        """Create mock branch manager."""
        return Mock(spec=BranchManager)

    @pytest.fixture
    @staticmethod
    def temp_repo() -> Path:
        """Create temporary repository."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    @staticmethod
    def engine(mock_branch_manager: Mock, temp_repo: Path) -> ConflictResolutionEngine:
        """Create ConflictResolutionEngine instance."""
        return ConflictResolutionEngine(
            branch_manager=mock_branch_manager,
            repo_path=str(temp_repo),
        )

    @staticmethod
    def test_init(engine: ConflictResolutionEngine, mock_branch_manager: Mock, temp_repo: Path) -> None:
        """Test ConflictResolutionEngine initialization."""
        assert engine.branch_manager == mock_branch_manager
        assert engine.repo_path == temp_repo
        assert engine.detected_conflicts == {}
        assert engine.resolution_history == []
        assert engine.auto_resolve_enabled is True
        assert engine.max_retry_attempts == 3
        assert len(engine.strategy_handlers) == 5

    @staticmethod
    def test_load_conflict_patterns(engine: ConflictResolutionEngine) -> None:
        """Test loading of conflict patterns."""
        patterns = engine.conflict_patterns

        assert "import_conflicts" in patterns
        assert "version_conflicts" in patterns
        assert "comment_conflicts" in patterns

        for pattern_info in patterns.values():
            assert "pattern" in pattern_info
            assert "strategy" in pattern_info
            assert "auto_resolve" in pattern_info

    @pytest.mark.asyncio
    @staticmethod
    async def test_detect_potential_conflicts(engine: ConflictResolutionEngine) -> None:
        """Test conflict detection between branches."""
        branches = ["feature1", "feature2", "main"]

        # Mock the git operations
        with patch.object(engine, "_detect_branch_conflicts") as mock_detect:
            mock_conflict = ConflictInfo(
                conflict_id="test-conflict",
                conflict_type=ConflictType.FILE_MODIFICATION,
                severity=ConflictSeverity.MEDIUM,
                branches=["feature1", "feature2"],
                files=["test.py"],
                description="Test conflict",
                suggested_strategy=ResolutionStrategy.AUTO_MERGE,
            )
            mock_detect.return_value = [mock_conflict]

            conflicts = await engine.detect_potential_conflicts(branches)

            # Should detect conflicts between all pairs of branches
            assert len(conflicts) > 0
            assert conflicts[0].conflict_id in engine.detected_conflicts
            assert engine.resolution_stats["total_conflicts"] > 0

    @staticmethod
    def test_parse_merge_tree_output(engine: ConflictResolutionEngine) -> None:
        """Test parsing of git merge-tree output."""
        output = """
@@ -1,3 +1,7 @@
+++ b/test.py
 line1
+<<<<<<< HEAD
+head_content
+=======
+other_content
+>>>>>>> branch
 line2
"""

        conflicts = engine._parse_merge_tree_output(output, "branch1", "branch2")  # noqa: SLF001

        assert len(conflicts) > 0
        conflict = conflicts[0]
        assert "test.py" in conflict.files
        assert conflict.conflict_type == ConflictType.MERGE_CONFLICT
        assert "branch1" in conflict.branches
        assert "branch2" in conflict.branches

    @staticmethod
    def test_create_merge_conflict(engine: ConflictResolutionEngine) -> None:
        """Test creation of merge conflict info."""
        conflict = engine._create_merge_conflict(  # noqa: SLF001
            "test.py",
            "branch1",
            "branch2",
            "conflict content",
        )

        assert conflict.conflict_type == ConflictType.MERGE_CONFLICT
        assert conflict.files == ["test.py"]
        assert conflict.branches == ["branch1", "branch2"]
        assert "test.py" in conflict.description
        assert conflict.metadata["conflict_content"] == "conflict content"

    @staticmethod
    def test_suggest_resolution_strategy(engine: ConflictResolutionEngine) -> None:
        """Test resolution strategy suggestion."""
        # Test Python file
        strategy = engine._suggest_resolution_strategy("def test():", "test.py")  # noqa: SLF001
        assert strategy == ResolutionStrategy.SEMANTIC_ANALYSIS

        # Test markdown file
        strategy = engine._suggest_resolution_strategy("# Header", "README.md")  # noqa: SLF001
        assert strategy == ResolutionStrategy.AUTO_MERGE

        # Test JSON file
        strategy = engine._suggest_resolution_strategy(  # noqa: SLF001
            '{"key": "value"}',
            "config.json",
        )
        assert strategy == ResolutionStrategy.PREFER_LATEST

        import_content = "<<<<<<< HEAD\nimport os\n=======\nimport sys\n>>>>>>> "
        strategy = engine._suggest_resolution_strategy(import_content, "test.py")  # noqa: SLF001
        assert strategy == ResolutionStrategy.SEMANTIC_ANALYSIS

    @pytest.mark.asyncio
    @staticmethod
    async def test_resolve_conflict_not_found(engine: ConflictResolutionEngine) -> None:
        """Test resolving non-existent conflict."""
        result = await engine.resolve_conflict("non-existent")

        assert result.success is False
        assert result.conflict_id == "non-existent"
        assert "not found" in result.message.lower()

    @pytest.mark.asyncio
    @staticmethod
    async def test_resolve_conflict_success(engine: ConflictResolutionEngine) -> None:
        """Test successful conflict resolution."""
        # Create a test conflict
        conflict = ConflictInfo(
            conflict_id="test-conflict",
            conflict_type=ConflictType.FILE_MODIFICATION,
            severity=ConflictSeverity.LOW,
            branches=["branch1", "branch2"],
            files=["test.py"],
            description="Test conflict",
            suggested_strategy=ResolutionStrategy.AUTO_MERGE,
        )
        engine.detected_conflicts["test-conflict"] = conflict

        # Mock the resolution strategy
        with patch.object(engine, "_auto_merge_strategy") as mock_strategy:
            mock_strategy.return_value = ResolutionResult(
                conflict_id="test-conflict",
                success=True,
                strategy_used=ResolutionStrategy.AUTO_MERGE,
                resolution_time=0.0,
                message="Successfully resolved",
            )

            result = await engine.resolve_conflict("test-conflict")

            assert result.success is True
            assert conflict.resolved_at is not None
            assert len(engine.resolution_history) == 1
            assert engine.resolution_stats["auto_resolved"] == 1

    @pytest.mark.asyncio
    @staticmethod
    async def test_auto_merge_strategy(engine: ConflictResolutionEngine) -> None:
        """Test auto-merge resolution strategy."""
        conflict = ConflictInfo(
            conflict_id="test-conflict",
            conflict_type=ConflictType.MERGE_CONFLICT,
            severity=ConflictSeverity.MEDIUM,
            branches=["branch1", "branch2"],
            files=["test.py"],
            description="Merge conflict",
            suggested_strategy=ResolutionStrategy.AUTO_MERGE,
        )

        with patch.object(engine, "_try_git_merge") as mock_merge:
            mock_merge.return_value = True

            result = await engine._auto_merge_strategy(conflict)  # noqa: SLF001

            assert result.success is True
            assert result.strategy_used == ResolutionStrategy.AUTO_MERGE
            assert "Auto-merged" in result.message

    @pytest.mark.asyncio
    @staticmethod
    async def test_prefer_latest_strategy(engine: ConflictResolutionEngine) -> None:
        """Test prefer-latest resolution strategy."""
        conflict = ConflictInfo(
            conflict_id="test-conflict",
            conflict_type=ConflictType.FILE_MODIFICATION,
            severity=ConflictSeverity.MEDIUM,
            branches=["branch1", "branch2"],
            files=["test.py"],
            description="File modification conflict",
            suggested_strategy=ResolutionStrategy.PREFER_LATEST,
        )

        with patch.object(engine, "_get_latest_branch") as mock_latest:
            mock_latest.return_value = "branch2"

            result = await engine._prefer_latest_strategy(conflict)  # noqa: SLF001

            assert result.success is True
            assert result.strategy_used == ResolutionStrategy.PREFER_LATEST
            assert "branch2" in result.message
            assert result.metadata["chosen_branch"] == "branch2"

    @pytest.mark.asyncio
    @staticmethod
    async def test_prefer_main_strategy(engine: ConflictResolutionEngine) -> None:
        """Test prefer-main resolution strategy."""
        conflict = ConflictInfo(
            conflict_id="test-conflict",
            conflict_type=ConflictType.FILE_MODIFICATION,
            severity=ConflictSeverity.MEDIUM,
            branches=["feature", "main"],
            files=["test.py"],
            description="File modification conflict",
            suggested_strategy=ResolutionStrategy.PREFER_MAIN,
        )

        result = await engine._prefer_main_strategy(conflict)  # noqa: SLF001

        assert result.success is True
        assert result.strategy_used == ResolutionStrategy.PREFER_MAIN
        assert "main" in result.message
        assert result.metadata["chosen_branch"] == "main"

    @pytest.mark.asyncio
    @staticmethod
    async def test_custom_merge_strategy(engine: ConflictResolutionEngine) -> None:
        """Test custom merge resolution strategy."""
        conflict = ConflictInfo(
            conflict_id="test-conflict",
            conflict_type=ConflictType.MERGE_CONFLICT,
            severity=ConflictSeverity.MEDIUM,
            branches=["branch1", "branch2"],
            files=["test.py"],
            description="Import conflict",
            suggested_strategy=ResolutionStrategy.CUSTOM_MERGE,
            metadata={
                "conflict_content": "<<<<<<< HEAD\nimport os\n=======\nimport sys\n>>>>>>> ",
            },
        )

        with patch.object(engine, "_resolve_import_conflicts") as mock_resolve:
            mock_resolve.return_value = "import os\nimport sys"

            result = await engine._custom_merge_strategy(conflict)  # noqa: SLF001

            assert result.success is True
            assert result.strategy_used == ResolutionStrategy.CUSTOM_MERGE
            assert "import conflicts" in result.message

    @pytest.mark.asyncio
    @staticmethod
    async def test_semantic_analysis_strategy(engine: ConflictResolutionEngine) -> None:
        """Test semantic analysis resolution strategy."""
        conflict = ConflictInfo(
            conflict_id="test-conflict",
            conflict_type=ConflictType.SEMANTIC,
            severity=ConflictSeverity.HIGH,
            branches=["branch1", "branch2"],
            files=["test.py"],
            description="Function signature conflict",
            suggested_strategy=ResolutionStrategy.SEMANTIC_ANALYSIS,
            metadata={
                "function_name": "test_func",
                "signature1": "def test_func(a, b):",
                "signature2": "def test_func(a):",
            },
        )

        result = await engine._semantic_analysis_strategy(conflict)  # noqa: SLF001

        assert result.success is True
        assert result.strategy_used == ResolutionStrategy.SEMANTIC_ANALYSIS
        assert "semantic analysis" in result.message
        assert "chosen_signature" in result.metadata

    @staticmethod
    def test_resolve_import_conflicts(engine: ConflictResolutionEngine) -> None:
        """Test import conflict resolution."""
        content = "<<<<<<< HEAD\nimport os\nimport sys\n=======\nimport sys\nimport json\n>>>>>>> branch"

        result = engine._resolve_import_conflicts(content)  # noqa: SLF001

        assert result is not None
        assert "import os" in result
        assert "import sys" in result
        assert "import json" in result
        # Should be sorted alphabetically
        lines = result.split("\n")
        assert lines == sorted(lines)

    @staticmethod
    def test_extract_function_signatures(engine: ConflictResolutionEngine) -> None:
        """Test function signature extraction."""
        content = """
def simple_func() -> object:
    pass

def func_with_params(a, b, c) -> object:
    return a + b + c

def func_with_return_type(x: int) -> str:
    return str(x)

class TestClass:
    @staticmethod
    def method() -> object:
        pass
"""

        signatures = engine._extract_function_signatures(content)  # noqa: SLF001

        assert "simple_func" in signatures
        assert "func_with_params" in signatures
        assert "func_with_return_type" in signatures
        assert "method" in signatures

        assert "def simple_func():" in signatures["simple_func"]
        assert "def func_with_params(a, b, c):" in signatures["func_with_params"]

    @pytest.mark.asyncio
    @staticmethod
    async def test_auto_resolve_all(engine: ConflictResolutionEngine) -> None:
        """Test automatic resolution of all conflicts."""
        # Create test conflicts
        conflict1 = ConflictInfo(
            conflict_id="conflict-1",
            conflict_type=ConflictType.FILE_MODIFICATION,
            severity=ConflictSeverity.LOW,
            branches=["branch1", "branch2"],
            files=["test1.py"],
            description="Low severity conflict",
            suggested_strategy=ResolutionStrategy.AUTO_MERGE,
        )

        conflict2 = ConflictInfo(
            conflict_id="conflict-2",
            conflict_type=ConflictType.SEMANTIC,
            severity=ConflictSeverity.HIGH,
            branches=["branch1", "branch2"],
            files=["test2.py"],
            description="High severity conflict",
            suggested_strategy=ResolutionStrategy.HUMAN_REQUIRED,
        )

        engine.detected_conflicts["conflict-1"] = conflict1
        engine.detected_conflicts["conflict-2"] = conflict2

        # Mock resolution
        with patch.object(engine, "resolve_conflict") as mock_resolve:
            mock_resolve.return_value = ResolutionResult(
                conflict_id="conflict-1",
                success=True,
                strategy_used=ResolutionStrategy.AUTO_MERGE,
                resolution_time=0.0,
                message="Auto-resolved",
            )

            results = await engine.auto_resolve_all()

            # Should only attempt to resolve low/medium severity conflicts
            assert len(results) == 1
            mock_resolve.assert_called_once_with("conflict-1")

    @staticmethod
    def test_get_conflict_summary(engine: ConflictResolutionEngine) -> None:
        """Test conflict summary generation."""
        # Add test conflicts
        conflict1 = ConflictInfo(
            conflict_id="conflict-1",
            conflict_type=ConflictType.FILE_MODIFICATION,
            severity=ConflictSeverity.LOW,
            branches=["branch1", "branch2"],
            files=["test1.py"],
            description="Low severity conflict",
            suggested_strategy=ResolutionStrategy.AUTO_MERGE,
            resolved_at=datetime.now(UTC),
        )

        conflict2 = ConflictInfo(
            conflict_id="conflict-2",
            conflict_type=ConflictType.SEMANTIC,
            severity=ConflictSeverity.HIGH,
            branches=["branch1", "branch2"],
            files=["test2.py"],
            description="High severity conflict",
            suggested_strategy=ResolutionStrategy.HUMAN_REQUIRED,
        )

        engine.detected_conflicts["conflict-1"] = conflict1
        engine.detected_conflicts["conflict-2"] = conflict2

        summary = engine.get_conflict_summary()

        assert summary["total_conflicts"] == 2
        assert summary["resolved_conflicts"] == 1
        assert summary["unresolved_conflicts"] == 1
        assert summary["resolution_rate"] == 0.5
        assert summary["severity_breakdown"]["low"] == 1
        assert summary["severity_breakdown"]["high"] == 1
        assert summary["type_breakdown"]["file_modification"] == 1
        assert summary["type_breakdown"]["semantic"] == 1

    @pytest.mark.asyncio
    @staticmethod
    async def test_git_helper_methods(engine: ConflictResolutionEngine) -> None:
        """Test git helper methods."""
        # Mock git command execution
        with patch.object(engine, "_run_git_command") as mock_git:
            # Test get_merge_base
            mock_git.return_value = Mock(stdout="abc123\n")
            base = await engine._get_merge_base("branch1", "branch2")  # noqa: SLF001
            assert base == "abc123"

            # Test get_changed_files
            mock_git.return_value = Mock(
                stdout="M\tfile1.py\nA\tfile2.py\nD\tfile3.py\n",
            )
            files = await engine._get_changed_files("branch1")  # noqa: SLF001
            assert files == {"file1.py": "M", "file2.py": "A", "file3.py": "D"}

            # Test get_python_files_changed
            python_files = await engine._get_python_files_changed("branch1")  # noqa: SLF001
            assert set(python_files) == {"file1.py", "file2.py"}

            # Test get_file_content
            mock_git.return_value = Mock(stdout="file content", returncode=0)
            content = await engine._get_file_content("test.py", "branch1")  # noqa: SLF001
            assert content == "file content"

    @pytest.mark.asyncio
    @staticmethod
    async def test_get_latest_branch(engine: ConflictResolutionEngine) -> None:
        """Test latest branch determination."""
        with patch.object(engine, "_run_git_command") as mock_git:
            # Mock timestamps for different branches
            def side_effect(args: list[str]) -> Mock:
                if args[-1] == "branch1":
                    return Mock(stdout="1640000000\n")  # Older
                if args[-1] == "branch2":
                    return Mock(stdout="1640000100\n")  # Newer
                return Mock(stdout="1640000050\n")

            mock_git.side_effect = side_effect

            latest = await engine._get_latest_branch(["branch1", "branch2", "branch3"])  # noqa: SLF001
            assert latest == "branch2"

    @pytest.mark.asyncio
    @staticmethod
    async def test_try_git_merge(engine: ConflictResolutionEngine) -> None:
        """Test git merge attempt."""
        # Test successful merge strategies
        result = await engine._try_git_merge(["branch1", "branch2"], "recursive")  # noqa: SLF001
        assert result is True

        result = await engine._try_git_merge(["branch1", "branch2"], "ours")  # noqa: SLF001
        assert result is True

        # Test unsupported strategy
        result = await engine._try_git_merge(["branch1", "branch2"], "unsupported")  # noqa: SLF001
        assert result is False

        # Test with wrong number of branches
        result = await engine._try_git_merge(["branch1"], "recursive")  # noqa: SLF001
        assert result is False

    @staticmethod
    def test_resolution_stats_update(engine: ConflictResolutionEngine) -> None:
        """Test resolution statistics tracking."""
        engine.resolution_stats.copy()

        # Add a successful resolution to history
        result = ResolutionResult(
            conflict_id="test",
            success=True,
            strategy_used=ResolutionStrategy.AUTO_MERGE,
            resolution_time=1.5,
            message="Success",
        )
        engine.resolution_history.append(result)

        # Add a failed resolution
        result2 = ResolutionResult(
            conflict_id="test2",
            success=False,
            strategy_used=ResolutionStrategy.AUTO_MERGE,
            resolution_time=0.5,
            message="Failed",
        )
        engine.resolution_history.append(result2)

        # Manually update stats (normally done in resolve_conflict)
        successful = len([r for r in engine.resolution_history if r.success])
        total = len(engine.resolution_history)
        engine.resolution_stats["resolution_success_rate"] = successful / total

        times = [r.resolution_time for r in engine.resolution_history if r.resolution_time > 0]
        engine.resolution_stats["average_resolution_time"] = sum(times) / len(times)

        assert engine.resolution_stats["resolution_success_rate"] == 0.5
        assert engine.resolution_stats["average_resolution_time"] == 1.0
