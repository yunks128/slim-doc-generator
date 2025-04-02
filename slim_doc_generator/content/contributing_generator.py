"""
Contributing documentation generator.
"""
import logging
import os
import re
from typing import Dict, List, Optional


class ContributingGenerator:
    """
    Generates contributing documentation from repository information.
    """
    
    def __init__(self, repo_path: str, logger: logging.Logger):
        """
        Initialize the contributing generator.
        
        Args:
            repo_path: Path to the repository
            logger: Logger instance
        """
        self.repo_path = repo_path
        self.logger = logger
    
    def generate(self, repo_info: Dict) -> str:
        """
        Generate contributing documentation based on repository content.
        
        Args:
            repo_info: Repository information dictionary
            
        Returns:
            Generated content as string
        """
        content = []
        content.append("# Contributing\n")
        content.append("This page provides guidelines for contributing to this project.\n")
        
        # Check for existing CONTRIBUTING.md file
        contributing_path = repo_info.get("key_files", {}).get("contributing")
        if contributing_path:
            contributing_content = self._extract_from_contributing(os.path.join(self.repo_path, contributing_path))
            if contributing_content:
                return contributing_content
        
        # Check for contributing section in README
        readme_path = repo_info.get("key_files", {}).get("readme")
        if readme_path:
            contributing_section = self._extract_contributing_from_readme(os.path.join(self.repo_path, readme_path))
            if contributing_section:
                content.append(contributing_section)
                return "\n".join(content)
        
        # If no contributing information found, generate default content
        self._generate_default_contributing(content, repo_info)
        
        return "\n".join(content)
    
    def _extract_from_contributing(self, file_path: str) -> Optional[str]:
        """
        Extract content from CONTRIBUTING.md file.
        
        Args:
            file_path: Path to CONTRIBUTING.md
            
        Returns:
            Extracted content or None if extraction failed
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Remove heading if it's just "Contributing" to avoid duplication
                content = re.sub(r'^#\s+Contributing\s*\n', '', content)
                
                return "# Contributing\n\n" + content
        
        except Exception as e:
            self.logger.warning(f"Error extracting content from CONTRIBUTING.md: {str(e)}")
            return None
    
    def _extract_contributing_from_readme(self, file_path: str) -> Optional[str]:
        """
        Extract contributing section from README.md.
        
        Args:
            file_path: Path to README.md
            
        Returns:
            Extracted contributing section or None if not found
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                readme_content = f.read()
            
            # Look for contributing section
            section_names = ["Contributing", "Contribution", "How to Contribute"]
            for section_name in section_names:
                pattern = rf"^##\s+{section_name}.*?$"
                match = re.search(pattern, readme_content, re.MULTILINE)
                
                if match:
                    start_pos = match.start()
                    
                    # Find the end of the section
                    next_heading = re.search(r"^##\s+", readme_content[start_pos+1:], re.MULTILINE)
                    if next_heading:
                        end_pos = start_pos + 1 + next_heading.start()
                        section = readme_content[start_pos:end_pos].strip()
                    else:
                        section = readme_content[start_pos:].strip()
                    
                    # Remove the heading to avoid duplication
                    section = re.sub(rf"^##\s+{section_name}.*?\n", '', section)
                    
                    return section
        
        except Exception as e:
            self.logger.warning(f"Error extracting contributing section from README: {str(e)}")
        
        return None
    
    def _generate_default_contributing(self, content: List[str], repo_info: Dict) -> None:
        """
        Generate default contributing guidelines.
        
        Args:
            content: List to append content to
            repo_info: Repository information dictionary
        """
        project_name = repo_info['project_name']
        repo_url = repo_info.get('repo_url', f"[REPO_URL]/{project_name}")
        
        content.append("\nThank you for considering contributing to this project! Here's how you can help:\n")
        
        # Add sections
        self._add_code_of_conduct_section(content, repo_info)
        self._add_getting_started_section(content, repo_info)
        self._add_contribution_workflow_section(content, repo_info, repo_url)
        self._add_reporting_bugs_section(content, repo_info)
        self._add_feature_requests_section(content, repo_info)
        self._add_coding_standards_section(content, repo_info)
        self._add_pull_request_section(content, repo_info)
        
        # Add contact information
        content.append("\n## Contact\n")
        content.append(f"If you have any questions or need assistance, please open an issue on the [repository]({repo_url}/issues).\n")
    
    def _add_code_of_conduct_section(self, content: List[str], repo_info: Dict) -> None:
        """
        Add code of conduct section to contributing guidelines.
        
        Args:
            content: List to append content to
            repo_info: Repository information dictionary
        """
        content.append("\n## Code of Conduct\n")
        
        # Check if repository has a code of conduct file
        code_of_conduct_path = repo_info.get("key_files", {}).get("code_of_conduct")
        if code_of_conduct_path:
            content.append(f"Please note that this project has a Code of Conduct. By participating in this project, you agree to abide by its terms. See [CODE_OF_CONDUCT.md]({code_of_conduct_path}) for details.\n")
        else:
            content.append("We expect all contributors to be respectful and considerate of others. We aim to foster an inclusive and welcoming community where everyone feels comfortable participating.\n")
    
    def _add_getting_started_section(self, content: List[str], repo_info: Dict) -> None:
        """
        Add getting started section to contributing guidelines.
        
        Args:
            content: List to append content to
            repo_info: Repository information dictionary
        """
        content.append("\n## Getting Started\n")
        content.append("To get started contributing to the project:\n")
        content.append("1. Fork the repository")
        content.append("2. Clone your fork locally")
        content.append("3. Set up your development environment")
        content.append("4. Create a new branch for your work")
        content.append("5. Make your changes")
        content.append("6. Test your changes")
        content.append("7. Submit a pull request\n")
        
        content.append("See the [Development](development.md) section for more details on setting up your environment.\n")
    
    def _add_contribution_workflow_section(self, content: List[str], repo_info: Dict, repo_url: str) -> None:
        """
        Add contribution workflow section to contributing guidelines.
        
        Args:
            content: List to append content to
            repo_info: Repository information dictionary
            repo_url: Repository URL
        """
        content.append("\n## Contribution Workflow\n")
        content.append("Here's the typical workflow for making a contribution to this project:\n")
        
        content.append("1. **Find an issue to work on**: Browse the [issue tracker](" + repo_url + "/issues) to find an issue that interests you, or create a new one to propose a change or report a bug.")
        content.append("2. **Discuss your approach**: For larger changes, it's best to discuss your approach in the issue before you start working on it.")
        content.append("3. **Fork and clone the repository**: Create your own fork of the repository and clone it locally.")
        content.append("4. **Create a branch**: Create a new branch for your work with a descriptive name.")
        content.append("5. **Make your changes**: Implement the changes you want to make. Be sure to follow the coding standards and write appropriate tests.")
        content.append("6. **Test your changes**: Run the tests to make sure your changes don't break existing functionality.")
        content.append("7. **Commit your changes**: Commit your changes with a clear and descriptive commit message.")
        content.append("8. **Push your changes**: Push your branch to your fork on GitHub.")
        content.append("9. **Submit a pull request**: Create a pull request from your branch to the main repository.")
        content.append("10. **Address review feedback**: Respond to any feedback and make changes as needed.")
        content.append("11. **Celebrate**: Once your pull request is merged, celebrate your contribution!\n")
    
    def _add_reporting_bugs_section(self, content: List[str], repo_info: Dict) -> None:
        """
        Add reporting bugs section to contributing guidelines.
        
        Args:
            content: List to append content to
            repo_info: Repository information dictionary
        """
        content.append("\n## Reporting Bugs\n")
        content.append("If you find a bug, please report it by opening an issue. When reporting a bug, please include:\n")
        content.append("- A clear and descriptive title")
        content.append("- Steps to reproduce the issue")
        content.append("- Expected behavior")
        content.append("- Actual behavior")
        content.append("- Environment details (OS, browser, version, etc.)")
        content.append("- Any relevant screenshots or logs\n")
    
    def _add_feature_requests_section(self, content: List[str], repo_info: Dict) -> None:
        """
        Add feature requests section to contributing guidelines.
        
        Args:
            content: List to append content to
            repo_info: Repository information dictionary
        """
        content.append("\n## Feature Requests\n")
        content.append("We welcome feature requests and suggestions for improvement. To submit a feature request:\n")
        content.append("1. Check if the feature has already been requested or implemented")
        content.append("2. Open an issue describing the feature you'd like to see")
        content.append("3. Explain why the feature would be valuable")
        content.append("4. Consider contributing the feature yourself\n")
    
    def _add_coding_standards_section(self, content: List[str], repo_info: Dict) -> None:
        """
        Add coding standards section to contributing guidelines.
        
        Args:
            content: List to append content to
            repo_info: Repository information dictionary
        """
        content.append("\n## Coding Standards\n")
        
        # Check for linting/formatting tools
        has_eslint = any(f == '.eslintrc.js' or f == '.eslintrc' or f == '.eslintrc.json' for f in repo_info.get("files", []))
        has_prettier = any(f == '.prettierrc' or f == '.prettierrc.js' or f == '.prettierrc.json' for f in repo_info.get("files", []))
        has_flake8 = any(f == '.flake8' or f == 'setup.cfg' for f in repo_info.get("files", []))
        has_black = 'pyproject.toml' in repo_info.get("files", [])
        
        if has_eslint or has_prettier or has_flake8 or has_black:
            content.append("This project follows specific coding standards that are enforced through automated tools. Please ensure your code adheres to these standards before submitting a pull request.\n")
            
            if has_eslint:
                content.append("- **ESLint**: JavaScript code should pass ESLint checks")
            
            if has_prettier:
                content.append("- **Prettier**: Code should be formatted using Prettier")
            
            if has_flake8:
                content.append("- **Flake8**: Python code should pass Flake8 checks")
            
            if has_black:
                content.append("- **Black**: Python code should be formatted using Black")
            
            content.append("\nYou can check your code against these standards by running the appropriate commands (see the [Development](development.md) section for details).\n")
        else:
            content.append("When contributing code, please follow these general guidelines:\n")
            content.append("- Write clear, readable, and maintainable code")
            content.append("- Include appropriate comments and documentation")
            content.append("- Follow the existing code style and patterns")
            content.append("- Write tests for your code when applicable\n")
    
    def _add_pull_request_section(self, content: List[str], repo_info: Dict) -> None:
        """
        Add pull request section to contributing guidelines.
        
        Args:
            content: List to append content to
            repo_info: Repository information dictionary
        """
        content.append("\n## Pull Requests\n")
        content.append("When submitting a pull request, please:\n")
        content.append("1. Create a clear and descriptive pull request title")
        content.append("2. Provide a detailed description of the changes")
        content.append("3. Link to any related issues")
        content.append("4. Ensure all tests pass")
        content.append("5. Include screenshots or examples if applicable")
        content.append("6. Keep pull requests focused on a single concern")
        content.append("7. Be responsive to feedback and be willing to make changes\n")
        
        # Check for pull request template
        if ".github/PULL_REQUEST_TEMPLATE.md" in repo_info.get("files", []):
            content.append("A pull request template will be provided when you create a pull request. Please fill it out completely.\n")