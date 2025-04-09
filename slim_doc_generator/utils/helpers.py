"""
Helper functions for the SLIM documentation generator.
"""
import logging
import os
import subprocess
import yaml
import re
from typing import Dict, List, Optional, Tuple, Union


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


def escape_mdx_special_characters(content: str) -> str:
    """
    Escape special characters in markdown content that might cause issues with MDX parsing.
    
    Args:
        content: Markdown content to process
        
    Returns:
        Processed content with special characters escaped
    """
    if not content:
        return content
        
    # Keep track of code block state
    in_code_block = False
    
    # Process content line by line
    lines = content.split('\n')
    processed_lines = []
    
    for line in lines:
        # Check for code block delimiters (```javascript, ```python, etc.)
        code_block_match = re.match(r'^```(\w*)$', line)
        if code_block_match:
            in_code_block = not in_code_block  # Toggle code block state
            processed_lines.append(line)
            continue
            
        if not in_code_block:
            # Process line for potential HTML-like tags and other special characters
            processed_line = _process_line(line)
            processed_lines.append(processed_line)
        else:
            # In a code block - no need to escape special characters
            processed_lines.append(line)
    
    return '\n'.join(processed_lines)


def _process_line(line: str) -> str:
    """
    Process a single line of text to escape special characters and handle HTML-like tags.
    
    Args:
        line: Line of text to process
        
    Returns:
        Processed line with special characters escaped
    """
    # Skip processing for lines that are Markdown headings, links, etc.
    if re.match(r'^#{1,6}\s', line) or re.match(r'^>\s', line) or re.match(r'^[-*+]\s', line):
        return line
        
    # Handle inline code blocks first
    parts = []
    current_pos = 0
    
    # Split by inline code (text wrapped in backticks)
    for match in re.finditer(r'`[^`]+`', line):
        start, end = match.span()
        
        # Add text before the code with escaped characters
        if start > current_pos:
            text_before = line[current_pos:start]
            parts.append(_process_text(text_before))
        
        # Add the code block unchanged
        parts.append(line[start:end])
        current_pos = end
    
    # Add any remaining text with escaped characters
    if current_pos < len(line):
        parts.append(_process_text(line[current_pos:]))
    
    return ''.join(parts)


def _process_text(text: str) -> str:
    """
    Process a segment of text to escape special characters and handle HTML-like tags.
    
    Args:
        text: Text to process
        
    Returns:
        Processed text with special characters escaped
    """
    # First, find any potential HTML-like tags
    tag_matches = list(re.finditer(r'<([A-Za-z][A-Za-z0-9_.-]*)(?:\s+[^>]*)?>', text))
    
    if not tag_matches:
        # No HTML-like tags, just escape special characters
        return _escape_special_chars(text)
        
    # Build the result, escaping each part appropriately
    result = []
    current_pos = 0
    
    for match in tag_matches:
        start, end = match.span()
        tag_name = match.group(1)
        
        # Check if this looks like a real HTML tag we should preserve or an accidental tag
        if _is_common_html_tag(tag_name):
            # This looks like a real HTML tag, preserve it
            # Process text before the tag
            if start > current_pos:
                result.append(_escape_special_chars(text[current_pos:start]))
            # Add the tag unchanged
            result.append(text[start:end])
        else:
            # This is not a common HTML tag, escape the angle brackets
            if start > current_pos:
                result.append(_escape_special_chars(text[current_pos:start]))
            # Add the "tag" with escaped angle brackets
            escaped_tag = text[start:end].replace('<', '\\<').replace('>', '\\>')
            result.append(escaped_tag)
        
        current_pos = end
    
    # Add any remaining text
    if current_pos < len(text):
        result.append(_escape_special_chars(text[current_pos:]))
    
    return ''.join(result)


def _escape_special_chars(text: str) -> str:
    """
    Escape special characters in text.
    
    Args:
        text: Text to escape
        
    Returns:
        Text with special characters escaped
    """
    # Escape curly braces that aren't already escaped
    text = re.sub(r'(?<!\\){', '\\{', text)
    text = re.sub(r'(?<!\\)}', '\\}', text)
    
    # Escape angle brackets not followed by standard HTML tag patterns
    # More careful approach to avoid double-escaping
    text = re.sub(r'(?<!\\)<(?![a-zA-Z\/])', '\\<', text)
    text = re.sub(r'(?<![a-zA-Z\/])(?<!\\)>', '\\>', text)
    
    return text


def _is_common_html_tag(tag_name: str) -> bool:
    """
    Check if a tag name is a common HTML tag we should preserve.
    
    Args:
        tag_name: Tag name to check
        
    Returns:
        True if it's a common HTML tag, False otherwise
    """
    common_tags = {
        # Block elements
        'div', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'header', 'footer', 'main', 'section', 'article',
        'aside', 'nav', 'figure', 'figcaption', 'blockquote', 'pre', 'code', 'ul', 'ol', 'li', 'dl', 'dt',
        'dd', 'table', 'thead', 'tbody', 'tr', 'td', 'th', 'form', 'fieldset', 'legend', 'hr',
        
        # Inline elements
        'a', 'span', 'strong', 'em', 'i', 'b', 'u', 's', 'sub', 'sup', 'mark', 'q', 'cite', 'time',
        'address', 'abbr', 'dfn', 'code', 'var', 'samp', 'kbd', 'data', 'small', 'br', 'wbr', 'img',
        'picture', 'source', 'iframe', 'embed', 'object', 'param', 'audio', 'video', 'track', 'canvas',
        'map', 'area', 'math', 'svg',
        
        # Form elements
        'input', 'button', 'select', 'option', 'optgroup', 'textarea', 'label', 'datalist', 'output',
        'progress', 'meter',
    }
    
    # Check if it's a common HTML tag or if it starts with uppercase (likely a React component)
    return tag_name.lower() in common_tags or (tag_name[0].isupper() if tag_name else False)


def clean_api_doc(api_doc_path: str) -> None:
    """
    Clean up the API documentation file to fix common MDX parsing issues.
    Applies targeted fixes for specific patterns known to cause problems.
    
    Args:
        api_doc_path: Path to the API documentation file to clean
    """
    if not os.path.exists(api_doc_path):
        return
        
    try:
        # Read the file content
        with open(api_doc_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Specific fixes for common API documentation issues
        
        # Fix 1: Replace angle brackets around type parameters (like <T> or <ES>)
        # This handles cases like "Type<T>" or "<ES> tag"
        content = re.sub(r'(?<![a-zA-Z/="`])(<)([A-Za-z][A-Za-z0-9_]*)(>)', r'\\<\2\\>', content)
        
        # Fix 2: Fix unclosed apparent HTML tags in text
        # Look for potential unclosed tags in sentences (not in code blocks)
        lines = content.split('\n')
        in_code_block = False
        for i, line in enumerate(lines):
            if line.strip() == '```' or re.match(r'^```\w*$', line.strip()):
                in_code_block = not in_code_block
                continue
                
            if not in_code_block and '<' in line and '>' in line:
                # Outside code blocks, escape any remaining angle brackets that look suspicious
                lines[i] = re.sub(r'<([A-Za-z][A-Za-Z0-9_]*)(?!\s*[/>])(?!.*</\1>)', r'\\<\1', line)
                lines[i] = re.sub(r'(?<!\\)<([A-Za-z][A-Za-Z0-9_]*)\s+', r'\\<\1 ', lines[i])
                
        content = '\n'.join(lines)
        
        # Fix 3: Replace problematic character sequences
        problematic_sequences = [
            ('<ES>', '\\<ES\\>'),
            ('<Type>', '\\<Type\\>'),
            ('<Generic>', '\\<Generic\\>'),
            ('<Value>', '\\<Value\\>'),
            ('<Key>', '\\<Key\\>'),
            ('<Parameter>', '\\<Parameter\\>'),
            ('<Class>', '\\<Class\\>'),
            ('<Method>', '\\<Method\\>'),
            ('<Function>', '\\<Function\\>'),
            ('<Property>', '\\<Property\\>'),
        ]
        
        for seq, replacement in problematic_sequences:
            content = content.replace(seq, replacement)
        
        # Write the cleaned content back
        with open(api_doc_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        logging.info(f"Cleaned API documentation for MDX compatibility")
            
    except Exception as e:
        logging.error(f"Error cleaning API documentation: {str(e)}")
        # Continue with generation even if cleaning fails