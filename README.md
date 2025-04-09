# SLIM Documentation Generator

A tool that automatically generates comprehensive documentation sites for software projects using the SLIM docsite template and AI enhancement.

## Features

- **Automatic Documentation**: Analyzes your repository's content to generate documentation
- **SLIM Template Integration**: Uses the official NASA AMMOS SLIM docsite template
- **AI Enhancement**: Improves documentation quality with AI-powered content generation
- **Customizable Output**: Tailor the output to your project's specific needs
- **Easy to Use**: Simple command-line interface with sensible defaults

## Installation

```bash
# Install from source with a virtual environment
git clone https://github.com/NASA-AMMOS/slim-doc-generator.git
cd slim-doc-generator

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install the package in development mode
pip install -e .
```

## Quick Start

```bash
# Just template generation 
# without specifying target repo
slim-doc-generator --template-only --output-dir ./docs-site

# With AI enhancement
slim-doc-generator /path/to/your/repo --output-dir ./docs-site --use-ai "openai/gpt-4o-mini"
# Example
slim-doc-generator ../hysds --output-dir ../hysds-docs-site5 --use-ai "openai/gpt-4o-mini"

# Revise an existing documentation site's landing page (index.js, HomepageFeatures/index.js, docusaurus.config.js)
slim-doc-generator --revise-site --output-dir ./docs-site --use-ai "openai/gpt-4o-mini"
# Example
slim-doc-generator --revise-site --output-dir ../hysds-docs-site5 --use-ai "openai/gpt-4o-mini"
```

## Requirements

- Python 3.7+
- Git
- npm (if using --install or --start options)
- Internet connection (for AI enhancement and template fetching)

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

## Contributing

We welcome contributions! Please see the CONTRIBUTING.md file for guidelines.