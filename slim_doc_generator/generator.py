"""
Main generator class for the SLIM Documentation Generator.
"""
import logging
import os
import shutil
import subprocess
from typing import Dict, Optional

from slim_doc_generator.analyzer.repo_analyzer import RepoAnalyzer
from slim_doc_generator.content.overview_generator import OverviewGenerator
from slim_doc_generator.content.installation_generator import InstallationGenerator
from slim_doc_generator.content.api_generator import ApiGenerator
from slim_doc_generator.content.development_generator import DevelopmentGenerator
from slim_doc_generator.content.contributing_generator import ContributingGenerator
from slim_doc_generator.enhancer.ai_enhancer import AIEnhancer
from slim_doc_generator.template.template_manager import TemplateManager
from slim_doc_generator.template.config_updater import ConfigUpdater
from slim_doc_generator.utils.helpers import load_config, run_command


class SlimDocGenerator:
    """
    Main class for generating documentation sites based on the SLIM template.
    """
    
    def __init__(
        self, 
        target_repo_path: str, 
        output_dir: str,
        template_repo: str = "https://github.com/NASA-AMMOS/slim-docsite-template.git",
        use_ai: Optional[str] = None,
        config_file: Optional[str] = None,
        verbose: bool = False
    ):
        """
        Initialize the SLIM documentation generator.
        
        Args:
            target_repo_path: Path to the target repository to document
            output_dir: Directory where the documentation site will be generated
            template_repo: URL or path to the template repository
            use_ai: Optional AI model to use for content enhancement (format: provider/model)
            config_file: Optional path to configuration file
            verbose: Whether to enable verbose logging
        """
        # Set up logging
        self.logger = logging.getLogger("slim-doc-generator")
        
        # Set properties
        self.target_repo_path = os.path.abspath(target_repo_path)
        self.output_dir = os.path.abspath(output_dir)
        self.template_repo = template_repo
        self.use_ai = use_ai
        self.config = load_config(config_file) if config_file else {}
        self.verbose = verbose
        
        # Validate target repository
        if not os.path.exists(target_repo_path):
            raise ValueError(f"Target repository path does not exist: {target_repo_path}")
        
        # Initialize components
        self.analyzer = RepoAnalyzer(target_repo_path, self.logger)
        self.template_manager = TemplateManager(template_repo, output_dir, self.logger)
        self.config_updater = ConfigUpdater(output_dir, self.logger)
        
        # Initialize content generators
        self.content_generators = {
            "overview": OverviewGenerator(self.target_repo_path, self.logger),
            "installation": InstallationGenerator(self.target_repo_path, self.logger),
            "api": ApiGenerator(self.target_repo_path, self.logger),
            "development": DevelopmentGenerator(self.target_repo_path, self.logger),
            "contributing": ContributingGenerator(self.target_repo_path, self.logger)
        }
        
        # Initialize AI enhancer if enabled
        self.ai_enhancer = AIEnhancer(use_ai, self.logger) if use_ai else None
        
        self.logger.info(f"Initialized SLIM Doc Generator for {os.path.basename(target_repo_path)}")
    


    def generate(self) -> bool:
        """
        Generate the documentation site.
        
        Returns:
            True if generation was successful, False otherwise
        """
        try:
            # Step 1: Clone the template repository
            if not self.template_manager.clone_template():
                return False
            
            # Step 2: Analyze the target repository
            repo_info = self.analyzer.analyze()
            
            # Step 3: Create the docs directory
            docs_dir = os.path.join(self.output_dir, 'docs')
            os.makedirs(docs_dir, exist_ok=True)
            
            # Step 4: Generate content for each section
            sections = {
                "overview": "Overview",
                "installation": "Installation",
                "api": "API Reference",
                "development": "Development",
                "contributing": "Contributing"
            }
            
            for section_id, section_title in sections.items():
                # Generate content
                generator = self.content_generators[section_id]
                content = generator.generate(repo_info)
                
                # Enhance with AI if enabled
                if self.ai_enhancer and content:
                    content = self.ai_enhancer.enhance(content, section_id)
                
                # Write to file if content was generated
                if content:
                    file_path = os.path.join(docs_dir, f"{section_id}.md")
                    with open(file_path, 'w') as f:
                        # Add frontmatter
                        f.write("---\n")
                        f.write(f"id: {section_id}\n")
                        f.write(f"title: {section_title}\n")
                        f.write("---\n\n")
                        f.write(content)
                    self.logger.info(f"Generated {section_id} content")
            
            # Step 5: Generate index.md
            self._generate_index(repo_info, docs_dir)
            
            # Step 6: Update configuration files - must come after content generation
            # so we know which sections were actually created
            self.config_updater.update_config(repo_info)
            
            # Step 7: Generate or update sidebars.js
            sections_with_content = {section_id for section_id in sections if 
                                    os.path.exists(os.path.join(docs_dir, f"{section_id}.md"))}
            sections_with_content.add("index")  # Make sure index is always included
            self.config_updater.update_sidebars(sections_with_content)
            
            # Step 8: Verify the structure is correct for Docusaurus
            self._verify_docusaurus_structure()
            
            self.logger.info(f"Documentation successfully generated at {self.output_dir}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error generating documentation: {str(e)}")
            if self.verbose:
                import traceback
                self.logger.debug(traceback.format_exc())
            return False
        

    def _generate_index(self, repo_info: Dict, docs_dir: str) -> None:
        """
        Generate the index.md file.
        
        Args:
            repo_info: Repository information dictionary
            docs_dir: Directory where docs are being generated
        """
        project_name = repo_info.get("project_name", os.path.basename(self.target_repo_path))
        description = repo_info.get("description", f"{project_name} documentation")
        
        content = [
            f"# {project_name} Documentation",
            "",
            description,
            "",
            "## Getting Started",
            ""
        ]
        
        # Add links to generated sections
        if os.path.exists(os.path.join(docs_dir, "overview.md")):
            content.append("- [Overview](overview.md)")
        if os.path.exists(os.path.join(docs_dir, "installation.md")):
            content.append("- [Installation](installation.md)")
        
        content.extend([
            "",
            "## Reference",
            ""
        ])
        
        if os.path.exists(os.path.join(docs_dir, "api.md")):
            content.append("- [API Reference](api.md)")
        if os.path.exists(os.path.join(docs_dir, "development.md")):
            content.append("- [Development](development.md)")
        if os.path.exists(os.path.join(docs_dir, "contributing.md")):
            content.append("- [Contributing](contributing.md)")
        
        # Write to file
        with open(os.path.join(docs_dir, 'index.md'), 'w') as f:
            f.write("---\n")
            f.write("slug: /\n")
            f.write("id: index\n")
            f.write(f"title: {project_name} Documentation\n")
            f.write("---\n\n")
            f.write("\n".join(content))
        
        self.logger.info("Generated index.md")
        
    def _verify_docusaurus_structure(self) -> None:
        """
        Verify and fix the Docusaurus structure to prevent common errors.
        
        This method checks for common issues in the Docusaurus structure
        and attempts to fix them to prevent errors during build/runtime.
        """
        # Check 1: Ensure the docs directory contains an index.md file
        docs_dir = os.path.join(self.output_dir, 'docs')
        index_path = os.path.join(docs_dir, 'index.md')
        if not os.path.exists(index_path):
            self.logger.warning("index.md not found in docs directory. Generating a basic one.")
            with open(index_path, 'w') as f:
                f.write("---\n")
                f.write("slug: /\n")
                f.write("id: index\n")
                f.write("title: Documentation\n")
                f.write("---\n\n")
                f.write("# Documentation\n\n")
                f.write("Welcome to the documentation.\n")
        
        # Check 2: Ensure the sidebars.js file exists and is properly formatted
        sidebars_path = os.path.join(self.output_dir, 'sidebars.js')
        if not os.path.exists(sidebars_path):
            self.logger.warning("sidebars.js not found. Generating a basic one.")
            with open(sidebars_path, 'w') as f:
                f.write("/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */\n")
                f.write("const sidebars = {\n")
                f.write("  tutorialSidebar: [\n")
                f.write("    {\n")
                f.write("      type: 'doc',\n")
                f.write("      id: 'index',\n")
                f.write("      label: 'Home',\n")
                f.write("    },\n")
                f.write("  ],\n")
                f.write("};\n\n")
                f.write("module.exports = sidebars;\n")
        
        # Check 3: Verify the docusaurus.config.js has the right sidebar ID
        config_path = os.path.join(self.output_dir, 'docusaurus.config.js')
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config_content = f.read()
                
                # Make sure there's a reference to 'tutorialSidebar' in the navbar items
                if 'sidebarId: "tutorialSidebar"' not in config_content:
                    self.logger.warning("tutorialSidebar not found in docusaurus.config.js. Attempting to fix.")
                    if re.search(r'sidebarId:\s*"[^"]+"', config_content):
                        # Replace the existing sidebarId
                        config_content = re.sub(
                            r'sidebarId:\s*"[^"]+"',
                            'sidebarId: "tutorialSidebar"',
                            config_content
                        )
                        
                        with open(config_path, 'w') as f:
                            f.write(config_content)
            except Exception as e:
                self.logger.warning(f"Error checking docusaurus.config.js: {str(e)}")
        
        # Check 4: Make sure static directories exist
        static_dir = os.path.join(self.output_dir, 'static')
        if not os.path.exists(static_dir):
            os.makedirs(static_dir, exist_ok=True)
            
        img_dir = os.path.join(static_dir, 'img')
        if not os.path.exists(img_dir):
            os.makedirs(img_dir, exist_ok=True)
            
        self.logger.info("Verified Docusaurus structure")


    
    def install_dependencies(self) -> bool:
        """
        Install the dependencies for the generated documentation site.
        
        Returns:
            True if installation was successful, False otherwise
        """
        try:
            self.logger.info("Installing dependencies")
            return run_command(["npm", "install"], self.output_dir, self.logger)
        except Exception as e:
            self.logger.error(f"Error installing dependencies: {str(e)}")
            return False
    
    def start_server(self) -> bool:
        """
        Start the development server for the generated documentation site.
        
        Returns:
            True if server was started successfully, False otherwise
        """
        try:
            self.logger.info("Starting development server")
            return run_command(["npm", "start"], self.output_dir, self.logger)
        except Exception as e:
            self.logger.error(f"Error starting server: {str(e)}")
            return False