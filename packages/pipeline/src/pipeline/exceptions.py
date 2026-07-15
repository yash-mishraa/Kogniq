class PipelineError(Exception):
    """Base class for all Pipeline-related errors."""


class PipelineConfigurationError(PipelineError):
    """Raised when the pipeline is improperly configured."""


class PipelineExecutionError(PipelineError):
    """Raised when a stage in the pipeline fails during execution."""
