"""
Command-line interface for the SLIM Documentation Generator.
"""
import logging
import os
import sys
from typing import Optional

import click

from slim_doc_generator.generator import SlimDocGenerator
from slim_doc_generator.site_reviser import SiteReviser
from slim_doc_generator.enhancer.ai_enhancer import AIEnhancer


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
@click.argument('repo_path', type=click.Path(exists=True, file_okay=False, dir_okay=True), required=False)
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
@click.option('--verbose', '-v', is_flag=True,
              help='Enable verbose logging')
@click.option('--template-only', is_flag=True,
              help='Generate only the template without any modifications')
@click.option('--revise-site', is_flag=True,
              help='Revise the site landing page based on documentation content')
def main(
    repo_path: Optional[str],
    output_dir: str,
    template_repo: str,
    use_ai: Optional[str],
    config: Optional[str],
    verbose: bool,
    template_only: bool,
    revise_site: bool
) -> int:
    """
    Generate documentation for a repository using the SLIM docsite template.
    
    REPO_PATH is the path to the repository to document. If not provided:
    - with --revise-site: only revises existing site without generating docs
    - with --template-only: only generates the template without modifications
    
    Use --use-ai with a model identifier to enhance content with AI.
    """
    logger = setup_logging(verbose)
    logger.info(f"Starting SLIM Documentation Generator")
    
    try:
        # If only revising an existing site, we don't need a repo path
        if revise_site and not repo_path:
            # Check if output directory exists
            if not os.path.exists(output_dir):
                logger.error(f"Output directory does not exist: {output_dir}")
                click.echo(f"Error: The directory {output_dir} does not exist. Please specify an existing documentation site.")
                return 1
            
            # Initialize AI enhancer if requested
            ai_enhancer = None
            if use_ai:
                try:
                    logger.info(f"Initializing AI enhancer with model: {use_ai}")
                    ai_enhancer = AIEnhancer(use_ai, logger)
                except Exception as e:
                    logger.error(f"Failed to initialize AI enhancer: {str(e)}")
                    click.echo(f"Error: Failed to initialize AI enhancer: {str(e)}")
                    return 1
            
            # Just run site reviser on existing output directory
            site_reviser = SiteReviser(output_dir, logger, ai_enhancer)
            if site_reviser.revise():
                logger.info(f"Successfully revised site landing page at {output_dir}")
                click.echo(f"Successfully revised site landing page at {output_dir}")
                return 0
            else:
                logger.error(f"Failed to revise site landing page at {output_dir}")
                click.echo(f"Error: Failed to revise site landing page at {output_dir}")
                return 1
        
        # If no repo_path is provided and not just revising, activate template-only mode
        if not repo_path:
            template_only = True
            logger.info("No repository path provided - activating template-only mode")
            click.echo("Template-only mode activated: Will generate the template without any modifications")
        
        # Create generator
        generator = SlimDocGenerator(
            target_repo_path=repo_path,
            output_dir=output_dir,
            template_repo=template_repo,
            use_ai=use_ai,
            config_file=config,
            verbose=verbose,
            template_only=template_only,
            revise_site=revise_site
        )
        
        # Generate documentation
        success = generator.generate()
        if not success:
            logger.error("Documentation generation failed")
            return 1
        
        if template_only:
            logger.info(f"Template structure successfully generated at {output_dir}")
            click.echo(f"Template structure successfully generated at {output_dir}")
            click.echo("You can now customize the template with your own content.")
        else:
            logger.info(f"Documentation successfully generated at {output_dir}")
            click.echo(f"Documentation successfully generated at {output_dir}")
        return 0
        
    except Exception as e:
        logger.exception(f"An error occurred: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())