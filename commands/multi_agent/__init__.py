# Copyright notice.

from .agent_pool import AddTaskCommand, ListTasksCommand, MonitorAgentsCommand, StartAgentsCommand, StatusCommand, StopAgentsCommand
from .batch_operations import AutoResolveCommand, BatchMergeCommand, PreventConflictsCommand
from .cli import multi_agent
from .code_review import QualityCheckCommand, ReviewApproveCommand, ReviewInitiateCommand, ReviewRejectCommand, ReviewStatusCommand, ReviewSummaryCommand
from .collaboration import BranchInfoCommand, CollaborateCommand, SendMessageCommand, ShareKnowledgeCommand
from .conflict_prediction import AnalyzeConflictPatternsCommand, PredictConflictsCommand, PredictionSummaryCommand
from .conflict_resolution import ConflictSummaryCommand, DetectConflictsCommand, ResolveConflictCommand
from .dependency_tracking import DependencyImpactCommand, DependencyPropagateCommand, DependencyStatusCommand, DependencyTrackCommand
from .semantic_analysis import AnalyzeSemanticConflictsCommand, FunctionDiffCommand, SemanticMergeCommand, SemanticSummaryCommand

# Copyright (c) 2024 Yesman Claude Project
# Licensed under the MIT License

"""Multi-agent system commands package.

This package contains modular multi-agent commands split from the original
monolithic multi_agent.py file for better maintainability and development.

Modules:
- agent_pool: Core agent pool management
- conflict_resolution: Conflict detection and resolution
- conflict_prediction: Conflict prediction and analysis
- semantic_analysis: AST-based semantic analysis and merging
- batch_operations: Batch operations and auto-resolution
- collaboration: Agent collaboration features
- dependency_tracking: Dependency management and tracking
- code_review: Code review system
- cli: Main CLI group registration
"""

# Import the main CLI group
# Import all command classes for easy access

__all__ = [
    "AddTaskCommand",
    "AnalyzeConflictPatternsCommand",
    # Semantic Analysis
    "AnalyzeSemanticConflictsCommand",
    "AutoResolveCommand",
    # Batch Operations
    "BatchMergeCommand",
    "BranchInfoCommand",
    # Collaboration
    "CollaborateCommand",
    "ConflictSummaryCommand",
    "DependencyImpactCommand",
    "DependencyPropagateCommand",
    "DependencyStatusCommand",
    # Dependency Tracking
    "DependencyTrackCommand",
    # Conflict Resolution
    "DetectConflictsCommand",
    "FunctionDiffCommand",
    "ListTasksCommand",
    "MonitorAgentsCommand",
    # Conflict Prediction
    "PredictConflictsCommand",
    "PredictionSummaryCommand",
    "PreventConflictsCommand",
    "QualityCheckCommand",
    "ResolveConflictCommand",
    "ReviewApproveCommand",
    # Code Review
    "ReviewInitiateCommand",
    "ReviewRejectCommand",
    "ReviewStatusCommand",
    "ReviewSummaryCommand",
    "SemanticMergeCommand",
    "SemanticSummaryCommand",
    "SendMessageCommand",
    "ShareKnowledgeCommand",
    # Agent Pool Management
    "StartAgentsCommand",
    "StatusCommand",
    "StopAgentsCommand",
    # Main CLI group
    "multi_agent",
]
