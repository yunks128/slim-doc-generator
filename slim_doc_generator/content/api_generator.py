"""
API documentation generator.
"""
import logging
import os
import re
from typing import Dict, List, Optional, Tuple


class ApiGenerator:
    """
    Generates API documentation from repository source code.
    """
    
    def __init__(self, repo_path: str, logger: logging.Logger):
        """
        Initialize the API generator.
        
        Args:
            repo_path: Path to the repository
            logger: Logger instance
        """
        self.repo_path = repo_path
        self.logger = logger
    
    def generate(self, repo_info: Dict) -> str:
        """
        Generate API documentation based on source code.
        
        Args:
            repo_info: Repository information dictionary
            
        Returns:
            Generated content as string
        """
        content = []
        content.append("# API Reference\n")
        content.append("This page provides documentation for the API of this project.\n")
        
        # First, check for existing API documentation
        api_docs = self._find_api_documentation(repo_info)
        if api_docs:
            content.append(api_docs)
            return "\n".join(content)
        
        # If no existing API docs found, generate from source
        api_content = self._generate_from_source(repo_info)
        if api_content:
            content.append(api_content)
        else:
            content.append("\n*No API documentation is available at this time.*\n")
            content.append("\nConsider adding API documentation to your project by:\n")
            content.append("- Adding a dedicated API.md file in your docs directory")
            content.append("- Using docstrings in your code")
            content.append("- Implementing API documentation tools like Swagger, JSDoc, or Sphinx")
        
        return "\n".join(content)
    
    def _find_api_documentation(self, repo_info: Dict) -> Optional[str]:
        """
        Look for existing API documentation in the repository.
        
        Args:
            repo_info: Repository information dictionary
            
        Returns:
            Extracted API documentation or None if not found
        """
        # Check for API documentation in doc directories
        for doc_dir in repo_info.get("doc_dirs", []):
            dir_path = os.path.join(self.repo_path, doc_dir)
            if os.path.exists(dir_path):
                for file in os.listdir(dir_path):
                    if file.lower() in {"api.md", "api-reference.md", "api-docs.md", "reference.md"}:
                        try:
                            with open(os.path.join(dir_path, file), 'r', encoding='utf-8') as f:
                                api_content = f.read()
                                # Remove frontmatter if present
                                api_content = re.sub(r'^---\n.*?\n---\n', '', api_content, flags=re.DOTALL)
                                return api_content
                        except Exception as e:
                            self.logger.warning(f"Error reading API documentation: {str(e)}")
        
        # Check for API section in README
        readme_path = repo_info.get("key_files", {}).get("readme")
        if readme_path:
            try:
                with open(os.path.join(self.repo_path, readme_path), 'r', encoding='utf-8') as f:
                    readme_content = f.read()
                
                # Look for API section
                api_section = self._extract_section(readme_content, "API", "")
                if api_section:
                    return api_section
            
            except Exception as e:
                self.logger.warning(f"Error extracting API section from README: {str(e)}")
        
        return None
    
    def _generate_from_source(self, repo_info: Dict) -> str:
        """
        Generate API documentation from source code.
        
        Args:
            repo_info: Repository information dictionary
            
        Returns:
            Generated API documentation
        """
        content = []
        
        # Look for modules, classes, and functions in source directories
        for src_dir in repo_info.get("src_dirs", []):
            dir_path = os.path.join(self.repo_path, src_dir)
            
            if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
                continue
            
            # Find source files
            source_files = []
            for root, _, files in os.walk(dir_path):
                for file in files:
                    _, ext = os.path.splitext(file)
                    if ext in {'.py', '.js', '.ts', '.jsx', '.tsx', '.java'}:
                        rel_path = os.path.relpath(os.path.join(root, file), self.repo_path)
                        source_files.append(rel_path)
            
            if not source_files:
                continue
                
            content.append(f"\n## {os.path.basename(src_dir).capitalize()} Module\n")
            
            # Include up to 10 files to avoid overwhelming the API reference
            for i, file_path in enumerate(sorted(source_files)[:10]):
                filename = os.path.basename(file_path)
                content.append(f"\n### {filename}\n")
                content.append(f"Path: `{file_path}`\n")
                
                # Extract classes and functions
                classes, functions = self._extract_code_elements(os.path.join(self.repo_path, file_path))
                
                if classes:
                    content.append("**Classes:**\n")
                    for cls_name, cls_desc in classes:
                        content.append(f"- `{cls_name}`" + (f": {cls_desc}" if cls_desc else ""))
                
                if functions:
                    content.append("\n**Functions:**\n")
                    for func_name, func_desc in functions:
                        content.append(f"- `{func_name}()`" + (f": {func_desc}" if func_desc else ""))
            
            # If there are more files, indicate that
            if len(source_files) > 10:
                content.append(f"\n*...and {len(source_files) - 10} more files*\n")
        
        return "\n".join(content)
    
    def _extract_code_elements(self, file_path: str) -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]]]:
        """
        Extract classes and functions from a source file.
        
        Args:
            file_path: Path to the source file
            
        Returns:
            Tuple of (classes, functions) where each is a list of (name, description) tuples
        """
        classes = []
        functions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            
            file_ext = os.path.splitext(file_path)[1]
            
            # Process based on file type
            if file_ext == '.py':
                classes, functions = self._extract_python_elements(file_content)
            elif file_ext in {'.js', '.ts', '.jsx', '.tsx'}:
                classes, functions = self._extract_javascript_elements(file_content)
            elif file_ext == '.java':
                classes, functions = self._extract_java_elements(file_content)
        
        except Exception as e:
            self.logger.warning(f"Error extracting code elements from {file_path}: {str(e)}")
        
        return classes, functions
    
    def _extract_python_elements(self, content: str) -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]]]:
        """
        Extract classes and functions from Python code.
        
        Args:
            content: Python code content
            
        Returns:
            Tuple of (classes, functions) where each is a list of (name, description) tuples
        """
        classes = []
        functions = []
        
        # Extract classes
        class_matches = re.finditer(r'class\s+(\w+)(?:\(.*?\))?:\s*(?:"""(.*?)""")?', content, re.DOTALL)
        for match in class_matches:
            class_name = match.group(1)
            class_desc = match.group(2).strip() if match.group(2) else ""
            classes.append((class_name, class_desc))
        
        # Extract functions (excluding methods in classes)
        func_matches = re.finditer(r'^def\s+(\w+)\s*\(.*?\):\s*(?:"""(.*?)""")?', content, re.MULTILINE | re.DOTALL)
        for match in func_matches:
            func_name = match.group(1)
            if not func_name.startswith('_'):  # Skip private functions
                func_desc = match.group(2).strip() if match.group(2) else ""
                functions.append((func_name, func_desc))
        
        return classes, functions
    
    def _extract_javascript_elements(self, content: str) -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]]]:
        """
        Extract classes and functions from JavaScript/TypeScript code.
        
        Args:
            content: JavaScript/TypeScript code content
            
        Returns:
            Tuple of (classes, functions) where each is a list of (name, description) tuples
        """
        classes = []
        functions = []
        
        # Extract classes
        class_matches = re.finditer(r'class\s+(\w+)(?:\s+extends\s+\w+)?(?:\s+implements\s+\w+)?\s*{', content)
        for match in class_matches:
            class_name = match.group(1)
            # Try to find JSDoc comment before class
            jsdoc_match = re.search(r'/\*\*(.*?)\*/\s*class\s+' + re.escape(class_name), content, re.DOTALL)
            class_desc = ""
            if jsdoc_match:
                # Extract description from JSDoc
                jsdoc = jsdoc_match.group(1)
                desc_match = re.search(r'^\s*\*\s+(.*?)(?:\s*@|\s*\*/$)', jsdoc, re.MULTILINE | re.DOTALL)
                if desc_match:
                    class_desc = desc_match.group(1).strip()
            
            classes.append((class_name, class_desc))
        
        # Extract functions
        patterns = [
            r'function\s+(\w+)\s*\(',  # function declarations
            r'const\s+(\w+)\s*=\s*(?:async\s*)?\(.*?\)\s*=>',  # arrow functions
            r'(\w+)\s*:\s*(?:async\s*)?\(.*?\)\s*=>'  # object method shorthand
        ]
        
        for pattern in patterns:
            func_matches = re.finditer(pattern, content)
            for match in func_matches:
                func_name = match.group(1)
                if not func_name.startswith('_'):  # Skip private functions
                    # Try to find JSDoc comment before function
                    jsdoc_match = re.search(r'/\*\*(.*?)\*/\s*(?:function|const|let|var)?\s*' + re.escape(func_name), content, re.DOTALL)
                    func_desc = ""
                    if jsdoc_match:
                        # Extract description from JSDoc
                        jsdoc = jsdoc_match.group(1)
                        desc_match = re.search(r'^\s*\*\s+(.*?)(?:\s*@|\s*\*/$)', jsdoc, re.MULTILINE | re.DOTALL)
                        if desc_match:
                            func_desc = desc_match.group(1).strip()
                    
                    functions.append((func_name, func_desc))
        
        return classes, functions
    
    def _extract_java_elements(self, content: str) -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]]]:
        """
        Extract classes and methods from Java code.
        
        Args:
            content: Java code content
            
        Returns:
            Tuple of (classes, methods) where each is a list of (name, description) tuples
        """
        classes = []
        methods = []
        
        # Extract classes
        class_matches = re.finditer(r'(?:public|protected|private)?\s+(?:abstract|final)?\s*class\s+(\w+)', content)
        for match in class_matches:
            class_name = match.group(1)
            # Try to find JavaDoc comment before class
            javadoc_match = re.search(r'/\*\*(.*?)\*/\s*(?:public|protected|private)?\s+(?:abstract|final)?\s*class\s+' + re.escape(class_name), content, re.DOTALL)
            class_desc = ""
            if javadoc_match:
                # Extract description from JavaDoc
                javadoc = javadoc_match.group(1)
                desc_match = re.search(r'^\s*\*\s+(.*?)(?:\s*@|\s*\*/$)', javadoc, re.MULTILINE | re.DOTALL)
                if desc_match:
                    class_desc = desc_match.group(1).strip()
            
            classes.append((class_name, class_desc))
        
        # Extract methods
        method_pattern = r'(?:public|protected|private|static|\s)+[\w\<\>\[\]]+\s+(\w+)\s*\([^\)]*\)\s*(?:throws[\w\s,]+)?'
        method_matches = re.finditer(method_pattern, content)
        for match in method_matches:
            method_name = match.group(1)
            if not method_name.startsWith('_'):  # Skip private methods
                # Try to find JavaDoc comment before method
                javadoc_match = re.search(r'/\*\*(.*?)\*/\s*(?:public|protected|private|static|\s)+[\w\<\>\[\]]+\s+' + re.escape(method_name), content, re.DOTALL)
                method_desc = ""
                if javadoc_match:
                    # Extract description from JavaDoc
                    javadoc = javadoc_match.group(1)
                    desc_match = re.search(r'^\s*\*\s+(.*?)(?:\s*@|\s*\*/$)', javadoc, re.MULTILINE | re.DOTALL)
                    if desc_match:
                        method_desc = desc_match.group(1).strip()
                
                methods.append((method_name, method_desc))
        
        return classes, methods
    
    def _extract_section(self, content: str, section_name: str, end_section_name: str = "") -> Optional[str]:
        """
        Extract a specific section from content.
        
        Args:
            content: Content to extract section from
            section_name: Name of the section to extract
            end_section_name: Name of the section that marks the end of extraction
            
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
            if end_section_name:
                end_pattern += rf"{end_section_name}.*?$"
            
            end_match = re.search(end_pattern, content[start_pos+1:], re.MULTILINE)
            
            if end_match:
                end_pos = start_pos + 1 + end_match.start()
                return content[start_pos:end_pos].strip()
            else:
                # If no end section found, go until the end of file
                return content[start_pos:].strip()
        
        return None