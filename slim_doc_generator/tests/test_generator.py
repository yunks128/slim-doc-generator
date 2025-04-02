"""
Tests for the main generator class.
"""
import logging
import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from slim_doc_generator.generator import SlimDocGenerator


class TestSlimDocGenerator(unittest.TestCase):
    """Test cases for the SlimDocGenerator class."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_repo = tempfile.mkdtemp()
        self.output_dir = tempfile.mkdtemp()
        
        # Create test files in the test repo
        with open(os.path.join(self.test_repo, "README.md"), "w") as f:
            f.write("# Test Project\n\nThis is a test project.")
        
        os.makedirs(os.path.join(self.test_repo, "src"))
        with open(os.path.join(self.test_repo, "src", "main.py"), "w") as f:
            f.write("# Test Python file")
        
        self.generator = SlimDocGenerator(
            target_repo_path=self.test_repo,
            output_dir=self.output_dir,
            template_repo="https://github.com/NASA-AMMOS/slim-docsite-template.git"
        )
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_repo)
        shutil.rmtree(self.output_dir)
    
    def test_initialization(self):
        """Test generator initialization."""
        self.assertEqual(self.generator.target_repo_path, self.test_repo)
        self.assertEqual(self.generator.output_dir, self.output_dir)
        self.assertEqual(self.generator.template_repo, "https://github.com/NASA-AMMOS/slim-docsite-template.git")
        self.assertIsNone(self.generator.use_ai)
        self.assertIsNotNone(self.generator.analyzer)
        self.assertIsNotNone(self.generator.template_manager)
        self.assertIsNotNone(self.generator.config_updater)
        self.assertIsNotNone(self.generator.content_generators)
    
    @patch("slim_doc_generator.template.template_manager.TemplateManager.clone_template")
    @patch("slim_doc_generator.analyzer.repo_analyzer.RepoAnalyzer.analyze")
    @patch("slim_doc_generator.template.config_updater.ConfigUpdater.update_config")
    @patch("slim_doc_generator.template.config_updater.ConfigUpdater.update_sidebars")
    def test_generate(self, mock_update_sidebars, mock_update_config, mock_analyze, mock_clone):
        """Test the generate method."""
        # Set up mocks
        mock_clone.return_value = True
        mock_analyze.return_value = {
            "project_name": "Test Project",
            "description": "This is a test project.",
            "files": ["README.md", "src/main.py"],
            "directories": ["src"],
            "key_files": {"readme": "README.md"},
            "src_dirs": ["src"],
            "doc_dirs": [],
            "test_dirs": [],
            "languages": ["Python"]
        }
        mock_update_config.return_value = True
        mock_update_sidebars.return_value = True
        
        # Create patches for content generators
        patches = []
        for section in ["overview", "installation", "api", "development", "contributing"]:
            generator_path = f"slim_doc_generator.content.{section}_generator.{section.capitalize()}Generator.generate"
            patch_obj = patch(generator_path)
            mock_obj = patch_obj.start()
            mock_obj.return_value = f"# Test {section.capitalize()} Content"
            patches.append((patch_obj, mock_obj))
        
        # Run generate method
        result = self.generator.generate()
        
        # Check result
        self.assertTrue(result)
        
        # Verify mocks were called
        mock_clone.assert_called_once()
        mock_analyze.assert_called_once()
        mock_update_config.assert_called_once()
        mock_update_sidebars.assert_called_once()
        
        # Verify content generators were called
        for _, mock_obj in patches:
            mock_obj.assert_called_once()
        
        # Check if docs directory was created
        docs_dir = os.path.join(self.output_dir, "docs")
        self.assertTrue(os.path.exists(docs_dir))
        
        # Stop patches
        for patch_obj, _ in patches:
            patch_obj.stop()
    
    @patch("slim_doc_generator.utils.helpers.run_command")
    def test_install_dependencies(self, mock_run):
        """Test the install_dependencies method."""
        mock_run.return_value = True
        
        result = self.generator.install_dependencies()
        
        self.assertTrue(result)
        mock_run.assert_called_once_with(["npm", "install"], self.output_dir, self.generator.logger)
    
    @patch("slim_doc_generator.utils.helpers.run_command")
    def test_start_server(self, mock_run):
        """Test the start_server method."""
        mock_run.return_value = True
        
        result = self.generator.start_server()
        
        self.assertTrue(result)
        mock_run.assert_called_once_with(["npm", "start"], self.output_dir, self.generator.logger)


if __name__ == "__main__":
    unittest.main()