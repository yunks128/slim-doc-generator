# SLIM Documentation Generator

A powerful tool that automatically generates comprehensive documentation sites for software projects using the SLIM docsite template and AI enhancement.

## Features

- **Automatic Documentation**: Analyzes your repository's content to generate documentation
- **SLIM Template Integration**: Uses the official NASA AMMOS SLIM docsite template
- **AI Enhancement**: Improves documentation quality with AI-powered content generation
- **Customizable Output**: Tailor the output to your project's specific needs
- **Easy to Use**: Simple command-line interface with sensible defaults

## Installation

```bash
# Install from PyPI
pip install slim-doc-generator

# Install from source
git clone https://github.com/NASA-AMMOS/slim-doc-generator.git
cd slim-doc-generator
pip install -e .
```

## Quick Start

```bash
# Basic usage
slim-doc-generator /path/to/your/repo --output-dir ./docs-site

# With AI enhancement
slim-doc-generator /path/to/your/repo --use-ai "openai/gpt-4o"

# Install dependencies and start the server
slim-doc-generator /path/to/your/repo --install --start
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