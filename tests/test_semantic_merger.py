# Copyright notice.

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock
import pytest
from libs.multi_agent.branch_manager import BranchManager
from libs.multi_agent.conflict_resolution import (
from libs.multi_agent.semantic_analyzer import (
from libs.multi_agent.semantic_merger import (
import os
import os
from typing import List, Any

# Copyright (c) 2024 Yesman Claude Project
# Licensed under the MIT License

"""Tests for SemanticMerger automatic conflict resolution."""



    ConflictResolutionEngine,
    ConflictSeverity,
)
    FunctionSignature,
    SemanticAnalyzer,
    SemanticConflict,
    SemanticConflictType,
    SemanticContext,
)
    ConflictResolutionRule,
    MergeResolution,
    MergeResult,
    MergeStrategy,
    SemanticMerger,
)


class TestMergeResult:
    """Test cases for MergeResult."""

    @staticmethod
    def test_init() -> None:
        """Test MergeResult initialization."""
        result = MergeResult(
            merge_id="test-merge",
            file_path="test.py",
            resolution=MergeResolution.AUTO_RESOLVED,
            strategy_used=MergeStrategy.INTELLIGENT_MERGE,
            merged_content="merged code",
            conflicts_resolved=["conflict-1", "conflict-2"],
            merge_confidence=0.85,
        )

        assert result.merge_id == "test-merge"
        assert result.file_path == "test.py"
        assert result.resolution == MergeResolution.AUTO_RESOLVED
        assert result.strategy_used == MergeStrategy.INTELLIGENT_MERGE
        assert result.merged_content == "merged code"
        assert result.conflicts_resolved == ["conflict-1", "conflict-2"]
        assert result.merge_confidence == 0.85
        assert result.semantic_integrity is True
        assert result.unresolved_conflicts == []


class TestConflictResolutionRule:
    """Test cases for ConflictResolutionRule."""

    @staticmethod
    def test_init() -> None:
        """Test ConflictResolutionRule initialization."""
        rule = ConflictResolutionRule(
            rule_id="test-rule",
            pattern="import.*",
            conflict_types=[SemanticConflictType.IMPORT_SEMANTIC_CONFLICT],
            resolution_strategy=MergeStrategy.SEMANTIC_UNION,
            confidence_threshold=0.8,
            description="Test rule",
        )

        assert rule.rule_id == "test-rule"
        assert rule.pattern == "import.*"
        assert rule.conflict_types == [SemanticConflictType.IMPORT_SEMANTIC_CONFLICT]
        assert rule.resolution_strategy == MergeStrategy.SEMANTIC_UNION
        assert rule.confidence_threshold == 0.8
        assert rule.description == "Test rule"
        assert rule.enabled is True


class TestSemanticMerger:
    """Test cases for SemanticMerger."""

    @pytest.fixture
    @staticmethod
    def mock_semantic_analyzer() -> Mock:
        """Create mock semantic analyzer."""
        analyzer = Mock(spec=SemanticAnalyzer)
        analyzer._extract_semantic_context = Mock()  # noqa: SLF001
        analyzer._analyze_file_semantic_conflicts = AsyncMock(return_value=[])  # noqa: SLF001
        analyzer._get_file_content = AsyncMock()  # noqa: SLF001
        return analyzer

    @pytest.fixture
    @staticmethod
    def mock_conflict_engine() -> Mock:
        """Create mock conflict resolution engine."""
        return Mock(spec=ConflictResolutionEngine)

    @pytest.fixture
    @staticmethod
    def mock_branch_manager() -> Mock:
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
    def merger(
        self,
        mock_semantic_analyzer: Mock,
        mock_conflict_engine: Mock,
        mock_branch_manager: Mock,
        temp_repo: Path,
    ) -> SemanticMerger:
        """Create SemanticMerger instance."""
        return SemanticMerger(
            semantic_analyzer=mock_semantic_analyzer,
            conflict_engine=mock_conflict_engine,
            branch_manager=mock_branch_manager,
            repo_path=str(temp_repo),
        )

    @staticmethod
    def test_init(
        self,
        merger: SemanticMerger,
        mock_semantic_analyzer: Mock,
        mock_conflict_engine: Mock,
        mock_branch_manager: Mock,
        temp_repo: Path,
    ) -> None:
        """Test SemanticMerger initialization."""
        assert merger.semantic_analyzer == mock_semantic_analyzer
        assert merger.conflict_engine == mock_conflict_engine
        assert merger.branch_manager == mock_branch_manager
        assert merger.repo_path == temp_repo
        assert merger.merge_results == {}
        assert merger.merge_history == []
        assert merger.default_strategy == MergeStrategy.INTELLIGENT_MERGE
        assert merger.preserve_comments is True
        assert merger.preserve_docstrings is True
        assert merger.enable_ast_validation is True
        assert len(merger.resolution_rules) > 0

    @staticmethod
    def test_initialize_resolution_rules(merger: SemanticMerger) -> None:
        """Test default resolution rules initialization."""
        rules = merger._initialize_resolution_rules()  # noqa: SLF001

        assert len(rules) > 0
        assert all(isinstance(rule, ConflictResolutionRule) for rule in rules)

        # Check specific rules
        import_rule = next((r for r in rules if r.rule_id == "import_order"), None)
        assert import_rule is not None
        assert SemanticConflictType.IMPORT_SEMANTIC_CONFLICT in import_rule.conflict_types
        assert import_rule.resolution_strategy == MergeStrategy.SEMANTIC_UNION

    @staticmethod
    def test_validate_ast_integrity(merger: SemanticMerger) -> None:
        """Test AST integrity validation."""
        valid_code = """
def test_function() -> object:
    return True

class TestClass:
    @staticmethod
    def method() -> object:
        pass
"""
        invalid_code = """
def test_function(
    return True  # Missing closing parenthesis
"""

        assert merger._validate_ast_integrity(valid_code) is True  # noqa: SLF001
        assert merger._validate_ast_integrity(invalid_code) is False  # noqa: SLF001

    @staticmethod
    def test_calculate_diff_stats(merger: SemanticMerger) -> None:
        """Test diff statistics calculation."""
        content1 = "line1\nline2\nline3"
        content2 = "line1\nline2_modified\nline3\nline4"
        merged = "line1\nline2_modified\nline3\nline4\nline5"

        stats = merger._calculate_diff_stats(content1, content2, merged)  # noqa: SLF001

        assert stats["lines_original1"] == 3
        assert stats["lines_original2"] == 4
        assert stats["lines_merged"] == 5
        assert stats["lines_added"] == 2  # 5 - 3
        assert stats["lines_removed"] == 0

    @staticmethod
    def test_select_optimal_strategy(merger: SemanticMerger) -> None:
        """Test optimal strategy selection."""
        # Function signature conflicts
        conflicts1 = [
            SemanticConflict(
                conflict_id="test-1",
                conflict_type=SemanticConflictType.FUNCTION_SIGNATURE_CHANGE,
                severity=ConflictSeverity.MEDIUM,
                symbol_name="test_func",
                file_path="test.py",
                branch1="branch1",
                branch2="branch2",
                description="Function signature conflict",
            ),
        ]

        strategy1 = merger._select_optimal_strategy(conflicts1)  # noqa: SLF001
        assert strategy1 == MergeStrategy.FUNCTION_LEVEL_MERGE

        # Import conflicts
        conflicts2 = [
            SemanticConflict(
                conflict_id="test-2",
                conflict_type=SemanticConflictType.IMPORT_SEMANTIC_CONFLICT,
                severity=ConflictSeverity.LOW,
                symbol_name="import_name",
                file_path="test.py",
                branch1="branch1",
                branch2="branch2",
                description="Import conflict",
            ),
        ]

        strategy2 = merger._select_optimal_strategy(conflicts2)  # noqa: SLF001
        assert strategy2 == MergeStrategy.SEMANTIC_UNION

        # Class interface conflicts
        conflicts3 = [
            SemanticConflict(
                conflict_id="test-3",
                conflict_type=SemanticConflictType.CLASS_INTERFACE_CHANGE,
                severity=ConflictSeverity.HIGH,
                symbol_name="TestClass",
                file_path="test.py",
                branch1="branch1",
                branch2="branch2",
                description="Class interface conflict",
            ),
        ]

        strategy3 = merger._select_optimal_strategy(conflicts3)  # noqa: SLF001
        assert strategy3 == MergeStrategy.AST_BASED_MERGE

    @staticmethod
    def test_prefer_branch_merge(merger: SemanticMerger) -> None:
        """Test prefer branch merge strategy."""
        conflicts = [
            SemanticConflict(
                conflict_id="test-conflict",
                conflict_type=SemanticConflictType.FUNCTION_SIGNATURE_CHANGE,
                severity=ConflictSeverity.MEDIUM,
                symbol_name="test_func",
                file_path="test.py",
                branch1="branch1",
                branch2="branch2",
                description="Test conflict",
            ),
        ]

        content = "def test_function():\n    return True"

        # Test prefer first
        result1 = merger._prefer_branch_merge(  # noqa: SLF001
            "merge-1",
            "test.py",
            content,
            conflicts,
            "first",
        )
        assert result1.resolution == MergeResolution.AUTO_RESOLVED
        assert result1.strategy_used == MergeStrategy.PREFER_FIRST
        assert result1.merged_content == content
        assert result1.merge_confidence == 1.0
        assert result1.conflicts_resolved == ["test-conflict"]

        # Test prefer second
        result2 = merger._prefer_branch_merge(  # noqa: SLF001
            "merge-2",
            "test.py",
            content,
            conflicts,
            "second",
        )
        assert result2.strategy_used == MergeStrategy.PREFER_SECOND

    @staticmethod
    def test_conflict_resolved_by_merge(merger: SemanticMerger) -> None:
        """Test conflict resolution detection."""
        conflict = SemanticConflict(
            conflict_id="test-conflict",
            conflict_type=SemanticConflictType.FUNCTION_SIGNATURE_CHANGE,
            severity=ConflictSeverity.MEDIUM,
            symbol_name="test_func",
            file_path="test.py",
            branch1="branch1",
            branch2="branch2",
            description="Test conflict",
        )

        # Successful merge
        successful_result = MergeResult(
            merge_id="merge-1",
            file_path="test.py",
            resolution=MergeResolution.AUTO_RESOLVED,
            strategy_used=MergeStrategy.INTELLIGENT_MERGE,
            semantic_integrity=True,
        )

        assert merger._conflict_resolved_by_merge(conflict, successful_result) is True  # noqa: SLF001

        # Failed merge
        failed_result = MergeResult(
            merge_id="merge-2",
            file_path="test.py",
            resolution=MergeResolution.MERGE_FAILED,
            strategy_used=MergeStrategy.INTELLIGENT_MERGE,
            semantic_integrity=False,
        )

        assert merger._conflict_resolved_by_merge(conflict, failed_result) is False  # noqa: SLF001

    @staticmethod
    def test_update_merge_stats(merger: SemanticMerger) -> None:
        """Test merge statistics updates."""
        # Initial stats
        assert merger.merge_stats["total_merges"] == 0
        assert merger.merge_stats["successful_merges"] == 0
        assert merger.merge_stats["auto_resolved"] == 0

        # Successful auto-resolved merge
        successful_result = MergeResult(
            merge_id="merge-1",
            file_path="test.py",
            resolution=MergeResolution.AUTO_RESOLVED,
            strategy_used=MergeStrategy.INTELLIGENT_MERGE,
            merge_confidence=0.8,
            semantic_integrity=True,
        )

        merger._update_merge_stats(successful_result)  # noqa: SLF001

        assert merger.merge_stats["total_merges"] == 1
        assert merger.merge_stats["successful_merges"] == 1
        assert merger.merge_stats["auto_resolved"] == 1
        assert merger.merge_stats["semantic_integrity_maintained"] == 1
        assert merger.merge_stats["average_confidence"] == 0.8

        # Partial resolution merge
        partial_result = MergeResult(
            merge_id="merge-2",
            file_path="test2.py",
            resolution=MergeResolution.PARTIAL_RESOLUTION,
            strategy_used=MergeStrategy.FUNCTION_LEVEL_MERGE,
            merge_confidence=0.6,
            semantic_integrity=True,
        )

        merger._update_merge_stats(partial_result)  # noqa: SLF001

        assert merger.merge_stats["total_merges"] == 2
        assert merger.merge_stats["successful_merges"] == 2
        assert merger.merge_stats["auto_resolved"] == 1  # Still 1
        assert merger.merge_stats["average_confidence"] == 0.7  # (0.8 + 0.6) / 2

    @staticmethod
    def test_extract_functions_with_content(merger: SemanticMerger) -> None:
        """Test function content extraction."""
        code = """

def function1() -> object:
    return "first"

def function2(x, y) -> object:
    return x + y

class TestClass:
    @staticmethod
    def method() -> object:
        pass
"""

        functions = merger._extract_functions_with_content(code)  # noqa: SLF001

        assert "function1" in functions
        assert "function2" in functions
        assert "method" in functions  # Class methods are also extracted

        # Check that function content contains the definition
        assert "def function1():" in functions["function1"]
        assert "def function2(x, y):" in functions["function2"]

    @staticmethod
    def test_extract_non_function_content(merger: SemanticMerger) -> None:
        """Test non-function content extraction."""
        code = """

CONSTANT = "value"
variable = 42

def function1() -> object:
    return "first"

def function2() -> object:
    return "second"
"""

        non_func_content = merger._extract_non_function_content(code)  # noqa: SLF001

        assert "import os" in non_func_content
        assert "from typing import List" in non_func_content
        assert "CONSTANT = " in non_func_content
        assert "variable = 42" in non_func_content
        assert "def function1():" not in non_func_content

    @staticmethod
    def test_find_function_conflict(merger: SemanticMerger) -> None:
        """Test finding function-specific conflicts."""
        conflicts = [
            SemanticConflict(
                conflict_id="import-conflict",
                conflict_type=SemanticConflictType.IMPORT_SEMANTIC_CONFLICT,
                severity=ConflictSeverity.LOW,
                symbol_name="import_name",
                file_path="test.py",
                branch1="branch1",
                branch2="branch2",
                description="Import conflict",
            ),
            SemanticConflict(
                conflict_id="function-conflict",
                conflict_type=SemanticConflictType.FUNCTION_SIGNATURE_CHANGE,
                severity=ConflictSeverity.MEDIUM,
                symbol_name="target_function",
                file_path="test.py",
                branch1="branch1",
                branch2="branch2",
                description="Function conflict",
            ),
        ]

        # Find existing function conflict
        found_conflict = merger._find_function_conflict("target_function", conflicts)  # noqa: SLF001
        assert found_conflict is not None
        assert found_conflict.conflict_id == "function-conflict"

        # Try to find non-existing function conflict
        not_found = merger._find_function_conflict("other_function", conflicts)  # noqa: SLF001
        assert not_found is None

    @staticmethod
    def test_merge_function_definitions(merger: SemanticMerger) -> None:
        """Test merging function definitions."""
        func1 = "def test_func(x):\n    return x"
        func2 = "def test_func(x, y=None):\n    return x + (y or 0)"

        conflict = SemanticConflict(
            conflict_id="test-conflict",
            conflict_type=SemanticConflictType.FUNCTION_SIGNATURE_CHANGE,
            severity=ConflictSeverity.MEDIUM,
            symbol_name="test_func",
            file_path="test.py",
            branch1="branch1",
            branch2="branch2",
            description="Function signature conflict",
        )

        result = merger._merge_function_definitions(func1, func2, conflict)  # noqa: SLF001

        assert result["resolved"] is True
        assert result["confidence"] > 0
        assert "content" in result

    @pytest.mark.asyncio
    @staticmethod
    async def test_resolve_individual_conflict(merger: SemanticMerger) -> None:
        """Test individual conflict resolution."""
        # Create semantic contexts
        context1 = SemanticContext(file_path="test.py")
        context1.functions["test_func"] = FunctionSignature(
            name="test_func",
            args=["x"],
            return_type="int",
        )

        context2 = SemanticContext(file_path="test.py")
        context2.functions["test_func"] = FunctionSignature(
            name="test_func",
            args=["x", "y"],
            return_type="int",
        )

        # Function signature conflict
        conflict = SemanticConflict(
            conflict_id="func-conflict",
            conflict_type=SemanticConflictType.FUNCTION_SIGNATURE_CHANGE,
            severity=ConflictSeverity.MEDIUM,
            symbol_name="test_func",
            file_path="test.py",
            branch1="branch1",
            branch2="branch2",
            description="Function signature conflict",
        )

        content1 = "def test_func(x): return x"
        content2 = "def test_func(x, y): return x + y"

        result = await merger._resolve_individual_conflict(  # noqa: SLF001
            conflict,
            content1,
            content2,
            context1,
            context2,
        )

        assert "resolved" in result
        assert "confidence" in result
        assert "strategy" in result

    @pytest.mark.asyncio
    @staticmethod
    async def test_perform_semantic_merge_success(merger: SemanticMerger) -> None:
        """Test successful semantic merge."""
        # Mock file contents
        content1 = "def test_func(x):\n    return x"
        content2 = "def test_func(x, y=0):\n    return x + y"

        merger.semantic_analyzer._get_file_content.side_effect = [content1, content2]  # noqa: SLF001
        merger.semantic_analyzer._analyze_file_semantic_conflicts.return_value = []  # noqa: SLF001

        result = await merger.perform_semantic_merge(
            "test.py",
            "branch1",
            "branch2",
            strategy=MergeStrategy.PREFER_SECOND,
        )

        assert result.file_path == "test.py"
        assert result.strategy_used == MergeStrategy.PREFER_SECOND
        assert result.resolution == MergeResolution.AUTO_RESOLVED
        assert result.merge_confidence == 1.0
        assert result.semantic_integrity is True

    @pytest.mark.asyncio
    @staticmethod
    async def test_perform_semantic_merge_missing_content(merger: SemanticMerger) -> None:
        """Test semantic merge with missing file content."""
        merger.semantic_analyzer._get_file_content.side_effect = [None, "content2"]  # noqa: SLF001

        result = await merger.perform_semantic_merge("test.py", "branch1", "branch2")

        assert result.resolution == MergeResolution.MERGE_FAILED
        assert result.merge_confidence == 0.0
        assert result.semantic_integrity is False
        assert "error" in result.metadata

    @pytest.mark.asyncio
    @staticmethod
    async def test_batch_merge_files(merger: SemanticMerger) -> None:
        """Test batch merging of multiple files."""
        file_paths = ["file1.py", "file2.py", "file3.py"]

        # Mock successful merges
        async def mock_perform_merge(file_path: str, branch1: str, branch2: str, target_branch: str = None) -> MergeResult:
            return MergeResult(
                merge_id=f"merge_{file_path}",
                file_path=file_path,
                resolution=MergeResolution.AUTO_RESOLVED,
                strategy_used=MergeStrategy.INTELLIGENT_MERGE,
                merge_confidence=0.8,
            )

        merger.perform_semantic_merge = mock_perform_merge

        results = await merger.batch_merge_files(file_paths, "branch1", "branch2")

        assert len(results) == 3
        assert all(result.resolution == MergeResolution.AUTO_RESOLVED for result in results)
        assert all(result.merge_confidence == 0.8 for result in results)

    @pytest.mark.asyncio
    @staticmethod
    async def test_auto_resolve_conflicts(merger: SemanticMerger) -> None:
        """Test automatic conflict resolution."""
        conflicts = [
            SemanticConflict(
                conflict_id="conflict-1",
                conflict_type=SemanticConflictType.FUNCTION_SIGNATURE_CHANGE,
                severity=ConflictSeverity.MEDIUM,
                symbol_name="func1",
                file_path="file1.py",
                branch1="branch1",
                branch2="branch2",
                description="Function conflict",
            ),
            SemanticConflict(
                conflict_id="conflict-2",
                conflict_type=SemanticConflictType.IMPORT_SEMANTIC_CONFLICT,
                severity=ConflictSeverity.LOW,
                symbol_name="import_name",
                file_path="file1.py",
                branch1="branch1",
                branch2="branch2",
                description="Import conflict",
            ),
        ]

        # Mock merge operation
        async def mock_perform_merge(file_path: str, branch1: str, branch2: str, strategy: MergeStrategy = None) -> MergeResult:
            return MergeResult(
                merge_id=f"merge_{file_path}",
                file_path=file_path,
                resolution=MergeResolution.AUTO_RESOLVED,
                strategy_used=strategy or MergeStrategy.INTELLIGENT_MERGE,
                conflicts_resolved=["conflict-1", "conflict-2"],
                merge_confidence=0.8,
            )

        merger.perform_semantic_merge = mock_perform_merge

        results = await merger.auto_resolve_conflicts(conflicts)

        assert len(results) == 1  # One file
        assert results[0].file_path == "file1.py"
        assert "conflict-1" in results[0].conflicts_resolved
        assert "conflict-2" in results[0].conflicts_resolved

    @staticmethod
    def test_get_merge_summary(merger: SemanticMerger) -> None:
        """Test merge summary generation."""
        # Add some test data
        merger.merge_stats["total_merges"] = 10
        merger.merge_stats["successful_merges"] = 8
        merger.merge_stats["auto_resolved"] = 6
        merger.merge_stats["semantic_integrity_maintained"] = 9
        merger.merge_stats["average_confidence"] = 0.75

        # Add some merge history
        merger.merge_history = [
            MergeResult(
                merge_id="merge-1",
                file_path="test1.py",
                resolution=MergeResolution.AUTO_RESOLVED,
                strategy_used=MergeStrategy.INTELLIGENT_MERGE,
                merge_confidence=0.8,
            ),
            MergeResult(
                merge_id="merge-2",
                file_path="test2.py",
                resolution=MergeResolution.PARTIAL_RESOLUTION,
                strategy_used=MergeStrategy.FUNCTION_LEVEL_MERGE,
                merge_confidence=0.7,
            ),
        ]

        summary = merger.get_merge_summary()

        assert summary["total_merges"] == 10
        assert summary["success_rate"] == 0.8  # 8/10
        assert summary["auto_resolution_rate"] == 0.6  # 6/10
        assert summary["semantic_integrity_rate"] == 0.9  # 9/10
        assert summary["average_confidence"] == 0.75
        assert len(summary["recent_merges"]) == 2

        # Check recent merge data
        recent_merge = summary["recent_merges"][0]
        assert recent_merge["merge_id"] == "merge-1"
        assert recent_merge["file_path"] == "test1.py"
        assert recent_merge["resolution"] == "auto_resolved"
        assert recent_merge["confidence"] == 0.8
        assert recent_merge["strategy"] == "intelligent_merge"
