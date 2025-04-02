"""
Helper functions for the SLIM documentation generator.
"""
import logging
import os
import subprocess
import yaml
from typing import Dict, Optional


def load_config(config_file: str) -> Dict:
    """
    Load configuration from YAML file.
    
    Args:
        config_file: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
            return config or {}
    except Exception as e:
        logging.warning(f"Error loading configuration from {config_file}: {str(e)}")
        return {}


def run_command(cmd: list, cwd: str, logger: logging.Logger) -> bool:
    """
    Run a command in a specific directory.
    
    Args:
        cmd: Command to run as a list of strings
        cwd: Directory to run the command in
        logger: Logger instance
        
    Returns:
        True if command succeeded, False otherwise
    """
    try:
        logger.info(f"Running command: {' '.join(cmd)}")
        
        # Create process
        process = subprocess.Popen(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # Line buffered
            universal_newlines=True
        )
        
        # Stream stdout in real-time
        for line in process.stdout:
            logger.info(line.strip())
        
        # Wait for process to complete
        process.wait()
        
        # Read stderr if there was an error
        if process.returncode != 0:
            for line in process.stderr:
                logger.error(line.strip())
            
            logger.error(f"Command failed with return code {process.returncode}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error running command: {str(e)}")
        return False


def create_file_from_template(template_path: str, output_path: str, variables: Dict) -> bool:
    """
    Create a file from a template, replacing variables.
    
    Args:
        template_path: Path to template file
        output_path: Path to output file
        variables: Dictionary of variables to replace in the template
        
    Returns:
        True if file was created successfully, False otherwise
    """
    try:
        # Check if template exists
        if not os.path.exists(template_path):
            logging.error(f"Template file not found: {template_path}")
            return False
        
        # Read template
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        # Replace variables
        for var_name, var_value in variables.items():
            template_content = template_content.replace(f"{{{{ {var_name} }}}}", str(var_value))
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Write output file
        with open(output_path, 'w') as f:
            f.write(template_content)
        
        return True
        
    except Exception as e:
        logging.error(f"Error creating file from template: {str(e)}")
        return False


def find_files_by_extension(directory: str, extension: str) -> list:
    """
    Find all files with a specific extension in a directory (recursively).
    
    Args:
        directory: Directory to search in
        extension: File extension to search for (without the dot)
        
    Returns:
        List of file paths
    """
    files = []
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith(f".{extension}"):
                files.append(os.path.join(root, filename))
    return files


def extract_frontmatter(content: str) -> tuple:
    """
    Extract frontmatter from markdown content.
    
    Args:
        content: Markdown content with frontmatter
        
    Returns:
        Tuple of (frontmatter_dict, content_without_frontmatter)
    """
    import re
    import yaml
    
    # Match frontmatter between --- markers
    frontmatter_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    
    if frontmatter_match:
        frontmatter_yaml = frontmatter_match.group(1)
        try:
            frontmatter = yaml.safe_load(frontmatter_yaml)
            content_without_frontmatter = content[frontmatter_match.end():]
            return frontmatter, content_without_frontmatter
        except Exception as e:
            logging.warning(f"Error parsing frontmatter: {str(e)}")
    
    # Return empty dict and original content if no frontmatter found
    return {}, content