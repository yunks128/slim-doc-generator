"""
Command-line interface for the SLIM Documentation Generator.
"""
import logging
import os
import sys
from typing import Optional

import click

from slim_doc_generator.generator import SlimDocGenerator


def setup_logging(verbose: bool = False) -> logging.Logger:
    """
    Set up logging configuration.
    
    Args:
        verbose: Whether to enable verbose logging
        
    Returns:
        Logger instance
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    return logging.getLogger('slim-doc-generator')


@click.command()
@click.argument('repo_path', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--output-dir', '-o', 
              type=click.Path(file_okay=False),
              default='./docsite',
              help='Directory where documentation should be generated')
@click.option('--template-repo', '-t',
              default="https://github.com/NASA-AMMOS/slim-docsite-template.git",
              help='URL or path to the template repository')
@click.option('--use-ai',
              help='Enable AI enhancement with specified model (e.g., "openai/gpt-4o", "ollama/mistral")')
@click.option('--config', '-c',
              type=click.Path(exists=True, dir_okay=False),
              help='Path to configuration file')
@click.option('--install', is_flag=True,
              help='Install dependencies after generation')
@click.option('--start', is_flag=True,
              help='Start development server after generation')
@click.option('--verbose', '-v', is_flag=True,
              help='Enable verbose logging')
def main(
    repo_path: str,
    output_dir: str,
    template_repo: str,
    use_ai: Optional[str],
    config: Optional[str],
    install: bool,
    start: bool,
    verbose: bool
) -> int:
    """
    Generate documentation for a repository using the SLIM docsite template.
    
    REPO_PATH is the path to the repository to document.
    """
    logger = setup_logging(verbose)
    logger.info(f"Starting SLIM Documentation Generator")
    
    try:
        # Create generator
        generator = SlimDocGenerator(
            target_repo_path=repo_path,
            output_dir=output_dir,
            template_repo=template_repo,
            use_ai=use_ai,
            config_file=config,
            verbose=verbose
        )
        
        # Generate documentation
        success = generator.generate()
        if not success:
            logger.error("Documentation generation failed")
            return 1
        
        # Optionally install dependencies
        if install:
            logger.info("Installing dependencies")
            if not generator.install_dependencies():
                logger.error("Failed to install dependencies")
                return 1
        
        # Optionally start development server
        if start:
            logger.info("Starting development server")
            if not generator.start_server():
                logger.error("Failed to start development server")
                return 1
        
        logger.info(f"Documentation successfully generated at {output_dir}")
        return 0
        
    except Exception as e:
        logger.exception(f"An error occurred: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())