"""
Base node classes for the analysis pipeline.
"""
from abc import ABC, abstractmethod

class Node(ABC):
    """
    Abstract base class for analysis nodes in the pipeline.
    """
    def __init__(self):
        self.cur_retry = 0
        self.max_retries = 3

    @abstractmethod
    def prep(self, shared):
        """
        Prepare data for execution.
        
        Args:
            shared: Dictionary containing shared data between pipeline nodes
            
        Returns:
            Prepared data for execution
        """
        pass
        
    @abstractmethod
    def exec(self, prep_res):
        """
        Execute the analysis.
        
        Args:
            prep_res: Prepared data from prep step
            
        Returns:
            Analysis results
        """
        pass
        
    @abstractmethod
    def post(self, shared, prep_res, exec_res):
        """
        Post-process the results and update shared data.
        
        Args:
            shared: Dictionary containing shared data between pipeline nodes
            prep_res: Prepared data from prep step
            exec_res: Results from execution step
            
        Returns:
            None
        """
        pass
        
    def retry(self, shared):
        """
        Handle retries when execution fails.
        
        Args:
            shared: Dictionary containing shared data between pipeline nodes
            
        Returns:
            Boolean indicating whether to retry
        """
        self.cur_retry += 1
        if self.cur_retry <= self.max_retries:
            return True
        return False