"""
Development documentation generator.
"""
import logging
import os
import re
from typing import Dict, List, Optional


class DevelopmentGenerator:
    """
    Generates development documentation from repository information.
    """
    
    def __init__(self, repo_path: str, logger: logging.Logger):
        """
        Initialize the development generator.
        
        Args:
            repo_path: Path to the repository
            logger: Logger instance
        """
        self.repo_path = repo_path
        self.logger = logger
    
    def generate(self, repo_info: Dict) -> str:
        """
        Generate development documentation based on repository contents.
        
        Args:
            repo_info: Repository information dictionary
            
        Returns:
            Generated content as string
        """
        content = []
        content.append("# Development\n")
        content.append("This page provides information for developers working on this project.\n")
        
        # Check for development section in README or other documents
        dev_section = self._extract_development_section(repo_info)
        if dev_section:
            content.append(dev_section)
            return "\n".join(content)
        
        # If no development section found, generate based on repo structure
        self._add_project_structure(content, repo_info)
        self._add_development_workflow(content, repo_info)
        self._add_testing_info(content, repo_info)
        self._add_coding_standards(content, repo_info)
        
        return "\n".join(content)
    
    def _extract_development_section(self, repo_info: Dict) -> Optional[str]:
        """
        Extract development section from README or other documents.
        
        Args:
            repo_info: Repository information dictionary
            
        Returns:
            Extracted development section or None if not found
        """
        # First look for development.md or similar
        for doc_dir in repo_info.get("doc_dirs", []):
            dir_path = os.path.join(self.repo_path, doc_dir)
            if os.path.exists(dir_path):
                for file in os.listdir(dir_path):
                    if file.lower() in {"development.md", "developers.md", "dev-guide.md", "hacking.md"}:
                        try:
                            with open(os.path.join(dir_path, file), 'r', encoding='utf-8') as f:
                                content = f.read()
                                # Remove frontmatter if present
                                content = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)
                                return content
                        except Exception as e:
                            self.logger.warning(f"Error reading development documentation: {str(e)}")
        
        # Check for development section in README
        readme_path = repo_info.get("key_files", {}).get("readme")
        if readme_path:
            try:
                with open(os.path.join(self.repo_path, readme_path), 'r', encoding='utf-8') as f:
                    readme_content = f.read()
                
                # Look for development section
                section_names = ["Development", "Developing", "For Developers", "Hacking"]
                for section_name in section_names:
                    section = self._extract_section(readme_content, section_name)
                    if section:
                        return section
            
            except Exception as e:
                self.logger.warning(f"Error extracting development section from README: {str(e)}")
        
        return None
    
    def _add_project_structure(self, content: List[str], repo_info: Dict) -> None:
        """
        Add project structure information.
        
        Args:
            content: List to append content to
            repo_info: Repository information dictionary
        """
        content.append("\n## Project Structure\n")
        content.append("Below is an overview of the key directories and files in this project:\n")
        content.append("```")
        
        # Add directories first
        for dir_path in sorted(repo_info.get("directories", [])):
            # Only include top-level directories or key subdirectories
            if '/' not in dir_path or dir_path.split('/')[0] in {'src', 'docs', 'tests', 'examples'}:
                content.append(f"{dir_path}/")
        
        # Add key files
        key_files = [f for f in repo_info.get("files", []) if '/' not in f and f.startswith(('.', 'README', 'LICENSE'))]
        for file in sorted(key_files):
            content.append(file)
        
        content.append("```\n")
        
        # Add description of key directories
        if repo_info.get("src_dirs"):
            content.append("### Source Code\n")
            for dir_path in repo_info["src_dirs"]:
                content.append(f"- `{dir_path}/`: Contains the main source code")
                # Optionally add more details about what's in this directory
        
        if repo_info.get("test_dirs"):
            content.append("\n### Tests\n")
            for dir_path in repo_info["test_dirs"]:
                content.append(f"- `{dir_path}/`: Contains tests for the project")
    
    def _add_development_workflow(self, content: List[str], repo_info: Dict) -> None:
        """
        Add development workflow information.
        
        Args:
            content: List to append content to
            repo_info: Repository information dictionary
        """
        content.append("\n## Development Workflow\n")
        
        # Add setup instructions
        content.append("### Setup Development Environment\n")
        content.append("To set up your development environment, follow these steps:\n")
        content.append("```bash")
        content.append(f"# Clone the repository")
        content.append(f"git clone {repo_info.get('repo_url', '[REPO_URL]')}")
        content.append(f"cd {os.path.basename(repo_info['project_name'])}")
        content.append("")
        
        # Add specific setup instructions based on repository structure
        if "package.json" in repo_info.get("files", []):
            content.append("# Install dependencies")
            content.append("npm install")
        elif "requirements.txt" in repo_info.get("files", []):
            content.append("# Create a virtual environment")
            content.append("python -m venv venv")
            content.append("source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
            content.append("")
            content.append("# Install dependencies")
            content.append("pip install -r requirements.txt")
        elif "setup.py" in repo_info.get("files", []):
            content.append("# Create a virtual environment")
            content.append("python -m venv venv")
            content.append("source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
            content.append("")
            content.append("# Install in development mode")
            content.append("pip install -e .")
        
        content.append("```\n")
        
        # Add workflow instructions
        content.append("### Development Workflow\n")
        content.append("1. Create a new branch for your feature or bugfix")
        content.append("2. Make your changes")
        content.append("3. Write or update tests")
        content.append("4. Run the tests to ensure they pass")
        content.append("5. Submit a pull request\n")
        
        # Add git commands
        content.append("```bash")
        content.append("# Create a new branch")
        content.append("git checkout -b feature/your-feature-name")
        content.append("")
        content.append("# Make your changes...")
        content.append("")
        content.append("# Commit your changes")
        content.append("git add .")
        content.append('git commit -m "Add your feature"')
        content.append("")
        content.append("# Push your changes")
        content.append("git push origin feature/your-feature-name")
        content.append("```\n")
    
    def _add_testing_info(self, content: List[str], repo_info: Dict) -> None:
        """
        Add testing information.
        
        Args:
            content: List to append content to
            repo_info: Repository information dictionary
        """
        content.append("\n## Testing\n")
        
        # Look for test directories
        if not repo_info.get("test_dirs"):
            content.append("*No testing information available.*")
            return
        
        content.append("This project includes tests to ensure code quality and functionality. Here's how to run the tests:\n")
        
        # Determine test framework based on repository structure
        if "package.json" in repo_info.get("files", []):
            content.append("```bash")
            content.append("# Run tests")
            content.append("npm test")
            content.append("```\n")
            
            # Check package.json for more test commands
            package_json_path = os.path.join(self.repo_path, 'package.json')
            if os.path.exists(package_json_path):
                try:
                    import json
                    with open(package_json_path, 'r', encoding='utf-8') as f:
                        package_data = json.load(f)
                    
                    if 'scripts' in package_data:
                        test_scripts = {k: v for k, v in package_data['scripts'].items() if 'test' in k}
                        if len(test_scripts) > 1:
                            content.append("Additional test commands available:\n")
                            for script, command in test_scripts.items():
                                if script != 'test':
                                    content.append(f"```bash\n# {script}\nnpm run {script}\n```\n")
                
                except Exception as e:
                    self.logger.warning(f"Error reading package.json for test scripts: {str(e)}")
        
        elif any(f.startswith('pytest') for f in repo_info.get("files", [])):
            content.append("```bash")
            content.append("# Run tests with pytest")
            content.append("pytest")
            content.append("```\n")
            
            content.append("For more detailed test output:\n")
            content.append("```bash")
            content.append("pytest -v")
            content.append("```\n")
        
        elif any(f.endswith('_test.py') or f.endswith('test_.py') or f.startswith('test_') for f in repo_info.get("files", [])):
            content.append("```bash")
            content.append("# Run Python tests")
            content.append("python -m unittest discover")
            content.append("```\n")
        
        else:
            content.append("Refer to test directory documentation for instructions on running tests.")
    
    def _add_coding_standards(self, content: List[str], repo_info: Dict) -> None:
        """
        Add coding standards information.
        
        Args:
            content: List to append content to
            repo_info: Repository information dictionary
        """
        content.append("\n## Coding Standards\n")
        
        # Look for coding standards in repository
        has_eslint = any(f == '.eslintrc.js' or f == '.eslintrc' or f == '.eslintrc.json' for f in repo_info.get("files", []))
        has_prettier = any(f == '.prettierrc' or f == '.prettierrc.js' or f == '.prettierrc.json' for f in repo_info.get("files", []))
        has_flake8 = any(f == '.flake8' or f == 'setup.cfg' for f in repo_info.get("files", []))
        has_black = 'pyproject.toml' in repo_info.get("files", [])
        
        if has_eslint or has_prettier or has_flake8 or has_black:
            content.append("This project maintains consistent coding standards using the following tools:\n")
            
            if has_eslint:
                content.append("### ESLint\n")
                content.append("This project uses ESLint to enforce consistent code style in JavaScript files.\n")
                content.append("```bash")
                content.append("# Run ESLint")
                content.append("npm run lint")
                content.append("```\n")
            
            if has_prettier:
                content.append("### Prettier\n")
                content.append("Prettier is used to format code consistently.\n")
                content.append("```bash")
                content.append("# Format code with Prettier")
                content.append("npm run format")
                content.append("```\n")
            
            if has_flake8:
                content.append("### Flake8\n")
                content.append("Flake8 is used to check Python code style.\n")
                content.append("```bash")
                content.append("# Run Flake8")
                content.append("flake8")
                content.append("```\n")
            
            if has_black:
                content.append("### Black\n")
                content.append("Black is used to format Python code consistently.\n")
                content.append("```bash")
                content.append("# Format code with Black")
                content.append("black .")
                content.append("```\n")
        else:
            content.append("Refer to the repository's contribution guidelines for information on coding standards and style.")
    
    def _extract_section(self, content: str, section_name: str) -> Optional[str]:
        """
        Extract a specific section from content.
        
        Args:
            content: Content to extract section from
            section_name: Name of the section to extract
            
        Returns:
            Extracted section or None if section not found
        """
        # Pattern to match the section heading (both ## and ### levels)
        pattern = rf"^(##|###)\s+{section_name}.*?$"
        match = re.search(pattern, content, re.MULTILINE)
        
        if match:
            start_pos = match.start()
            heading_level = match.group(1)
            
            # Find the end of the section (next heading of same or higher level)
            end_pattern = rf"^{heading_level}(?:#)?\s+"
            end_match = re.search(end_pattern, content[start_pos+1:], re.MULTILINE)
            
            if end_match:
                end_pos = start_pos + 1 + end_match.start()
                return content[start_pos:end_pos].strip()
            else:
                # If no end section found, go until the end of file
                return content[start_pos:].strip()
        
        return None