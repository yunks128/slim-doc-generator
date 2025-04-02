"""
Tests for repository analyzer.
"""
import logging
import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from slim_doc_generator.analyzer.repo_analyzer import RepoAnalyzer


class TestRepoAnalyzer(unittest.TestCase):
    """Test cases for the RepoAnalyzer class."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.logger = logging.getLogger("test")
        
        # Create test files
        os.makedirs(os.path.join(self.test_dir, "src"))
        os.makedirs(os.path.join(self.test_dir, "docs"))
        os.makedirs(os.path.join(self.test_dir, "tests"))
        
        with open(os.path.join(self.test_dir, "README.md"), "w") as f:
            f.write("# Test Project\n\nThis is a test project.")
        
        with open(os.path.join(self.test_dir, "src", "main.py"), "w") as f:
            f.write("# Test Python file")
        
        self.analyzer = RepoAnalyzer(self.test_dir, self.logger)
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test analyzer initialization."""
        self.assertEqual(self.analyzer.repo_path, self.test_dir)
        self.assertEqual(self.analyzer.logger, self.logger)
        self.assertFalse(self.analyzer.is_git_repo)
    
    def test_analyze(self):
        """Test repository analysis."""
        result = self.analyzer.analyze()
        
        # Check basics
        self.assertEqual(result["project_name"], os.path.basename(self.test_dir))
        self.assertIn("files", result)
        self.assertIn("directories", result)
        
        # Check if directories were detected
        self.assertIn("src", result["directories"])
        self.assertIn("docs", result["directories"])
        self.assertIn("tests", result["directories"])
        
        # Check if files were detected
        self.assertIn("README.md", result["files"])
        self.assertIn("src/main.py", result["files"])
        
        # Check if README was detected as key file
        self.assertEqual(result["key_files"].get("readme"), "README.md")
        
        # Check if directories were categorized
        self.assertIn("src", result["src_dirs"])
        self.assertIn("docs", result["doc_dirs"])
        self.assertIn("tests", result["test_dirs"])
        
        # Check if languages were detected
        self.assertIn("Python", result["languages"])
    
    @patch("slim_doc_generator.analyzer.content_extractor.extract_from_package_json")
    def test_package_json_extraction(self, mock_extract):
        """Test package.json extraction."""
        # Create package.json
        with open(os.path.join(self.test_dir, "package.json"), "w") as f:
            f.write('{"name": "test-project", "description": "Test description"}')
        
        self.analyzer.analyze()
        
        # Check if extraction function was called
        mock_extract.assert_called_once()
    
    @patch("slim_doc_generator.analyzer.content_extractor.extract_from_setup_py")
    def test_setup_py_extraction(self, mock_extract):
        """Test setup.py extraction."""
        # Create setup.py
        with open(os.path.join(self.test_dir, "setup.py"), "w") as f:
            f.write('# Test setup.py')
        
        self.analyzer.analyze()
        
        # Check if extraction function was called
        mock_extract.assert_called_once()
    
    @patch("slim_doc_generator.analyzer.content_extractor.extract_git_info")
    def test_git_info_extraction(self, mock_extract):
        """Test git info extraction."""
        # Create .git directory to simulate git repo
        os.makedirs(os.path.join(self.test_dir, ".git"))
        
        # Reinitialize analyzer to detect git repo
        self.analyzer = RepoAnalyzer(self.test_dir, self.logger)
        self.analyzer.analyze()
        
        # Check if extraction function was called
        mock_extract.assert_called_once()


if __name__ == "__main__":
    unittest.main()