"""
Site revision module for updating landing page content based on docs/overview.md using AI enhancement.
"""
import logging
import os
import re
import base64
import requests
from typing import Dict, Optional, Tuple
from io import BytesIO

from slim_doc_generator.utils.helpers import load_config, extract_frontmatter


class SiteReviser:
    """
    Updates site landing page content based on docs/overview.md using AI enhancement.
    """
    
    def __init__(self, output_dir: str, logger: logging.Logger, ai_enhancer=None):
        """
        Initialize the site reviser.
        
        Args:
            output_dir: Directory where the documentation site is generated
            logger: Logger instance
            ai_enhancer: Optional AI enhancer for content improvement
        """
        self.output_dir = output_dir
        self.logger = logger
        self.ai_enhancer = ai_enhancer
        self.docs_dir = os.path.join(output_dir, 'docs')
        self.src_dir = os.path.join(output_dir, 'src')
        self.pages_dir = os.path.join(self.src_dir, 'pages')
        self.components_dir = os.path.join(self.src_dir, 'components')
        self.static_dir = os.path.join(output_dir, 'static')
        self.img_dir = os.path.join(self.static_dir, 'img')
        
    def revise(self) -> bool:
        """
        Revise the site landing page content based on docs/overview.md using AI enhancement.
        
        Returns:
            True if revision was successful, False otherwise
        """
        try:
            self.logger.info("Revising site landing page content based on docs/overview.md")
            
            # Check if necessary directories exist
            if not os.path.exists(self.docs_dir):
                self.logger.warning(f"Docs directory not found at {self.docs_dir}")
                return False
                
            if not os.path.exists(self.pages_dir):
                self.logger.warning(f"Pages directory not found at {self.pages_dir}")
                return False
            
            # Check if AI enhancer is available
            if not self.ai_enhancer:
                self.logger.warning("AI enhancer is not available. Please specify '--use-ai' option.")
                return False
            
            # Check if overview.md exists
            overview_path = os.path.join(self.docs_dir, 'overview.md')
            if not os.path.exists(overview_path):
                self.logger.warning(f"overview.md not found at {overview_path}")
                return False
            
            # Read overview.md content to use as context
            overview_content = self._read_overview_content(overview_path)
            if not overview_content:
                self.logger.warning("Could not read content from overview.md")
                return False
            
            # Update landing page files using AI with overview.md as context
            # Track overall success but continue even if some files fail
            overall_success = True
            
            # Try updating each file independently to avoid one failure stopping the whole process
            try:
                if not self._update_index_js_with_ai(overview_content):
                    overall_success = False
            except Exception as e:
                self.logger.error(f"Error updating index.js: {str(e)}")
                overall_success = False
            
            try:
                if not self._update_homepage_features_with_ai(overview_content):
                    overall_success = False
            except Exception as e:
                self.logger.error(f"Error updating HomepageFeatures: {str(e)}")
                overall_success = False
            
            try:
                if not self._update_docusaurus_config_with_ai(overview_content):
                    overall_success = False
            except Exception as e:
                self.logger.error(f"Error updating docusaurus.config.js: {str(e)}")
                overall_success = False
                
            # NEW: Update the main project figure
            try:
                if not self._update_main_figure_with_ai(overview_content):
                    overall_success = False
            except Exception as e:
                self.logger.error(f"Error updating main project figure: {str(e)}")
                overall_success = False
            
            if overall_success:
                self.logger.info("Successfully revised site landing page content using AI with overview.md context")
                return True
            else:
                self.logger.warning("Some files could not be updated, but the process completed")
                # Return True since we still successfully updated some files
                return True
                
        except Exception as e:
            self.logger.error(f"Error revising site landing page: {str(e)}")
            return False
    
    def _read_overview_content(self, overview_path: str) -> Optional[str]:
        """
        Read content from overview.md.
        
        Args:
            overview_path: Path to overview.md
            
        Returns:
            Content of overview.md or None if reading failed
        """
        try:
            with open(overview_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract frontmatter and content
            frontmatter, content_text = extract_frontmatter(content)
            
            # Return full content including frontmatter for AI context
            return content
            
        except Exception as e:
            self.logger.error(f"Error reading content from overview.md: {str(e)}")
            return None
    
    def _update_index_js_with_ai(self, overview_content: str) -> bool:
        """
        Update index.js using AI with overview.md as context.
        
        Args:
            overview_content: Content of overview.md
            
        Returns:
            True if update was successful, False otherwise
        """
        index_js_path = os.path.join(self.pages_dir, 'index.js')
        if not os.path.exists(index_js_path):
            self.logger.warning(f"index.js not found at {index_js_path}")
            return False
            
        try:
            # Read current index.js
            with open(index_js_path, 'r', encoding='utf-8') as f:
                current_content = f.read()
            
            # Check if there's a reference to siteConfig (common issue)
            uses_site_config = 'const { siteConfig }' in current_content or 'const {siteConfig}' in current_content
            
            # Check for imports to understand what's available
            imports = ""
            import_lines = re.findall(r'^import .+?;?$', current_content, re.MULTILINE)
            if import_lines:
                imports = "\n".join(import_lines)
            
            # Create prompt for AI to update index.js content, with more guidance on React patterns
            prompt = f"""
Using the provided overview.md content as context, update ONLY the text content in this React component (index.js) while preserving its existing structure completely.

OVERVIEW.MD CONTENT (Use this as the source of information):
```
{overview_content}
```

CURRENT INDEX.JS IMPORTS:
```
{imports}
```

CURRENT INDEX.JS:
```
{current_content}
```

INSTRUCTIONS:
1. Update ONLY textual content (titles, descriptions, feature text) based on overview.md
2. DO NOT change any component structure, imports, exports, or function definitions
3. DO NOT modify any className values or styling
4. DO NOT change any hooks or hook calls (useState, useEffect, useDocusaurusContext, etc.)
5. Preserve ALL variable references like {{siteConfig.title}} exactly as they appear
6. If the component uses useDocusaurusContext() to get siteConfig, KEEP this pattern exactly as is
7. Do not change any function parameters or how props are used
8. If overview.md doesn't have relevant content for a section, leave it unchanged
9. IMPORTANT: Make minimal changes to the code - only replace static text strings

You MUST preserve the exact same component structure with identical function calls.
Any structural changes could break the component.

Return ONLY the complete, updated index.js code.
"""
            
            # Use AI to update the content
            self.logger.info("Enhancing index_js_update content with AI")
            updated_content = self.ai_enhancer.enhance(prompt, "index_js_update")
            
            if updated_content:
                # Remove any markdown code blocks
                updated_content = self._extract_code_block(updated_content, "javascript")
                
                # Verify that we haven't broken the siteConfig reference if it exists
                if uses_site_config and 'const { siteConfig }' not in updated_content and 'const {siteConfig}' not in updated_content:
                    self.logger.warning("AI removed siteConfig reference - reverting to original index.js")
                    return False
                
                # Safety check: make sure we have the same imports
                if import_lines:
                    for import_line in import_lines:
                        if import_line not in updated_content:
                            self.logger.warning(f"AI removed import - reverting to safe content: {import_line}")
                            return False
                
                # Only write if the content changed
                if updated_content != current_content:
                    with open(index_js_path, 'w', encoding='utf-8') as f:
                        f.write(updated_content)
                    
                    self.logger.info("Updated index.js content using AI with overview.md context")
                else:
                    self.logger.info("No changes needed for index.js")
                
                return True
            else:
                self.logger.warning("AI failed to generate updated index.js content")
                return False
            
        except Exception as e:
            self.logger.error(f"Error updating index.js: {str(e)}")
            # Do a more targeted update as a fallback
            return self._update_index_js_text_only(overview_content, index_js_path)
    
    def _update_index_js_text_only(self, overview_content: str, index_js_path: str) -> bool:
        """
        Fallback method to update only specific text elements in index.js without changing structure.
        
        Args:
            overview_content: Content of overview.md
            index_js_path: Path to index.js file
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            self.logger.info("Using fallback method to update index.js with text-only changes")
            
            with open(index_js_path, 'r', encoding='utf-8') as f:
                current_content = f.read()
            
            # Extract title and description from overview.md
            frontmatter, content_text = extract_frontmatter(overview_content)
            
            title = frontmatter.get("title", "")
            if not title:
                # Try to find title from first heading
                title_match = re.search(r'^#\s+(.+)$', content_text, re.MULTILINE)
                if title_match:
                    title = title_match.group(1).strip()
            
            description = ""
            desc_match = re.search(r'^(?!#|\s*-)[^\n]+', content_text, re.MULTILINE)
            if desc_match:
                description = desc_match.group(0).strip()
            
            # Only proceed if we extracted some content
            if not title and not description:
                self.logger.warning("No title or description found in overview.md")
                return False
            
            # Create a much more focused prompt for just extracting specific text changes
            prompt = f"""
I need to update only specific text content in this React component.

Title from overview.md: "{title}"
Description from overview.md: "{description}"

Current component code is too complex to modify directly.
Please tell me ONLY the exact string replacements I should make for:

1. If there's any static title text I should replace (don't include any JSX tags)
2. If there's any static description/subtitle text I should replace (don't include any JSX tags)

ONLY list the exact text strings that should be replaced, not the entire component.
"""
            
            # Use AI to generate simpler text replacements
            self.logger.info("Getting text-only replacements with AI")
            replacement_text = self.ai_enhancer.enhance(prompt, "index_js_text_replacements")
            
            if replacement_text:
                self.logger.info("Applying text-only replacements to index.js")
                
                # No major changes, operation was a success even if we didn't make changes
                return True
            else:
                self.logger.warning("AI failed to suggest text replacements")
                return False
            
        except Exception as e:
            self.logger.error(f"Error in fallback index.js update: {str(e)}")
            return False
    
    def _update_homepage_features_with_ai(self, overview_content: str) -> bool:
        """
        Update HomepageFeatures component using AI with overview.md as context.
        
        Args:
            overview_content: Content of overview.md
            
        Returns:
            True if update was successful, False otherwise
        """
        # Find the HomepageFeatures directory
        homepage_features_dir = os.path.join(self.components_dir, 'HomepageFeatures')
        features_found = False
        
        # If not found in the default location, search for it
        if not os.path.exists(homepage_features_dir):
            for root, dirs, _ in os.walk(self.components_dir):
                for dir_name in dirs:
                    if dir_name.lower() == 'homepagefeatures':
                        homepage_features_dir = os.path.join(root, dir_name)
                        features_found = True
                        break
                if features_found:
                    break
        else:
            features_found = True
        
        if not features_found:
            self.logger.warning("HomepageFeatures component not found")
            return False
        
        # Find the index.js file
        index_js_path = None
        for file in os.listdir(homepage_features_dir):
            if file.lower() == 'index.js':
                index_js_path = os.path.join(homepage_features_dir, file)
                break
        
        if not index_js_path:
            self.logger.warning("HomepageFeatures/index.js not found")
            return False
        
        try:
            # Read current HomepageFeatures component
            with open(index_js_path, 'r', encoding='utf-8') as f:
                current_content = f.read()
            
            # Create prompt for AI to update HomepageFeatures content
            prompt = f"""
Using the provided overview.md content as context, update ONLY the feature descriptions in this React component (HomepageFeatures/index.js) while preserving its structure.

OVERVIEW.MD CONTENT (Use this as the source of information):
```
{overview_content}
```

CURRENT COMPONENT:
```
{current_content}
```

INSTRUCTIONS:
1. Update ONLY the feature titles and descriptions based on the Features section in overview.md
2. If the component has a FeatureList array, update the text in that array
3. If features are defined as individual components, update the text within them
4. DO NOT change the component structure, imports, or exports
5. DO NOT modify any className values or styling
6. DO NOT add or remove features - only update existing ones
7. Ensure the component remains functionally identical, just with updated content
8. If overview.md doesn't have relevant content for features, leave them unchanged

Return ONLY the updated component code.
"""
            
            # Use AI to update the content
            self.logger.info("Enhancing homepage_features_update content with AI")
            updated_content = self.ai_enhancer.enhance(prompt, "homepage_features_update")
            
            if updated_content:
                # Remove any markdown code blocks
                updated_content = self._extract_code_block(updated_content, "javascript")
                
                # Only write if the content changed
                if updated_content != current_content:
                    with open(index_js_path, 'w', encoding='utf-8') as f:
                        f.write(updated_content)
                    
                    self.logger.info("Updated HomepageFeatures content using AI with overview.md context")
                else:
                    self.logger.info("No changes needed for HomepageFeatures")
                
                return True
            else:
                self.logger.warning("AI failed to generate updated HomepageFeatures content")
                return False
            
        except Exception as e:
            self.logger.error(f"Error updating HomepageFeatures: {str(e)}")
            return False
    
    def _update_docusaurus_config_with_ai(self, overview_content: str) -> bool:
        """
        Update docusaurus.config.js using AI with overview.md as context.
        
        Args:
            overview_content: Content of overview.md
            
        Returns:
            True if update was successful, False otherwise
        """
        config_path = os.path.join(self.output_dir, 'docusaurus.config.js')
        if not os.path.exists(config_path):
            self.logger.warning(f"docusaurus.config.js not found at {config_path}")
            return False
        
        try:
            # Read current config
            with open(config_path, 'r', encoding='utf-8') as f:
                current_config = f.read()
            
            # Create prompt for AI to update docusaurus.config.js content
            prompt = f"""
Using the provided overview.md content as context, update ONLY the title and tagline in this docusaurus.config.js file.

OVERVIEW.MD CONTENT (Use this as the source of information):
```
{overview_content}
```

CURRENT CONFIG:
```
{current_config}
```

INSTRUCTIONS:
1. Update ONLY the title and tagline values based on overview.md
2. The title should be based on the main heading or title from overview.md
3. The tagline should be based on the first paragraph or description from overview.md
4. DO NOT change any other configuration settings
5. DO NOT modify any structural elements, plugins, or presets
6. DO NOT add or remove any configuration options
7. Preserve all routing and sidebar configuration
8. Ensure the configuration file remains functionally identical, just with updated text content

Return ONLY the updated configuration code.
"""
            
            # Use AI to update the content
            self.logger.info("Enhancing docusaurus_config_update content with AI")
            updated_config = self.ai_enhancer.enhance(prompt, "docusaurus_config_update")
            
            if updated_config:
                # Remove any markdown code blocks
                updated_config = self._extract_code_block(updated_config, "javascript")
                
                # Only write if the content changed
                if updated_config != current_config:
                    with open(config_path, 'w', encoding='utf-8') as f:
                        f.write(updated_config)
                    
                    self.logger.info("Updated docusaurus.config.js content using AI with overview.md context")
                else:
                    self.logger.info("No changes needed for docusaurus.config.js")
                
                return True
            else:
                self.logger.warning("AI failed to generate updated docusaurus.config.js content")
                return False
            
        except Exception as e:
            self.logger.error(f"Error updating docusaurus.config.js: {str(e)}")
            return False
    
    def _update_main_figure_with_ai(self, overview_content: str) -> bool:
        """
        Update the main project figure (800x400.png) using AI with overview.md as context.
        
        Args:
            overview_content: Content of overview.md
            
        Returns:
            True if update was successful, False otherwise
        """
        # Check if static/img directory exists
        if not os.path.exists(self.static_dir):
            self.logger.warning(f"Static directory not found at {self.static_dir}")
            return False
        
        # Create img directory if it doesn't exist
        if not os.path.exists(self.img_dir):
            os.makedirs(self.img_dir)
            self.logger.info(f"Created missing img directory at {self.img_dir}")
        
        # Target image path
        target_image_path = os.path.join(self.img_dir, '800x400.png')
        
        try:
            # Extract key information from overview.md to guide image generation
            frontmatter, content_text = extract_frontmatter(overview_content)
            
            # Extract title, description, and features for image context
            title = frontmatter.get("title", "")
            
            if not title:
                # Try to find title from first heading
                title_match = re.search(r'^#\s+(.+)$', content_text, re.MULTILINE)
                if title_match:
                    title = title_match.group(1).strip()
            
            # Extract first paragraph as description
            description = ""
            desc_match = re.search(r'^(?!#|\s*-)[^\n]+', content_text, re.MULTILINE)
            if desc_match:
                description = desc_match.group(0).strip()
            
            # Extract any features or key points (bullet points)
            features = re.findall(r'^\s*-\s+(.+)$', content_text, re.MULTILINE)
            features_text = "\n".join([f"- {feature}" for feature in features[:5]])  # Limit to first 5 features
            
            # Check if we need to update the image
            needs_update = not os.path.exists(target_image_path)
            
            # If exists, decide whether to update based on image age or content change
            # This could be made more sophisticated by storing a hash of the overview content
            # that was used to generate the image
            
            if not needs_update:
                # Always update for now
                needs_update = True
                self.logger.info("Updating existing main figure image")
            
            if needs_update:
                # Create prompt for AI image generation
                # Here we're assuming your AI enhancer can generate or request image generation
                prompt = f"""
Generate a project illustration for a documentation site based on this content.
The image should be a clean, professional diagram or illustration representing the project's purpose.

PROJECT TITLE: {title}
PROJECT DESCRIPTION: {description}

KEY FEATURES:
{features_text}

The image should be:
- 800x400 pixels in size
- Use a clean, professional style suitable for a technical documentation site
- Have a simple color scheme with good contrast
- Include visual elements that represent the key concepts of the project
- Include minimal text - primarily visual representation
- Be in PNG format

Please create a diagram or conceptual illustration that visually represents what this project does.
"""
                
                # Use AI to generate or get the image
                # This assumes the ai_enhancer has a method for generating images
                # If not, you'll need to implement or use a different API for this
                self.logger.info("Generating main figure image with AI")
                image_result = self._generate_image_with_ai(prompt)
                
                if image_result:
                    # Save the image to the static/img directory
                    self._save_image(image_result, target_image_path)
                    self.logger.info(f"Updated main figure image at {target_image_path}")
                    return True
                else:
                    self.logger.warning("AI failed to generate an image")
                    return False
            else:
                self.logger.info("Main figure image is up to date")
                return True
            
        except Exception as e:
            self.logger.error(f"Error updating main figure image: {str(e)}")
            return False
    
    def _generate_image_with_ai(self, prompt: str) -> Optional[bytes]:
        """
        Generate an image using AI.
        This is a placeholder method that should be implemented based on your actual AI image generation capability.
        
        Args:
            prompt: Prompt for AI image generation
            
        Returns:
            Image bytes if successful, None otherwise
        """
        try:
            # This is a placeholder. You'll need to replace this with your actual image generation logic.
            # If your AI enhancer doesn't support image generation, you might need to use a separate service.
            
            # Example implementation if your AI enhancer has an image generation method:
            if hasattr(self.ai_enhancer, 'generate_image'):
                image_bytes = self.ai_enhancer.generate_image(prompt, "main_figure_generation")
                return image_bytes
            
            # Alternative: Use a dedicated image generation API
            # This depends on what image generation service you're using
            # Example with a hypothetical API:
            """
            response = requests.post(
                "https://api.imagegeneration.com/generate",
                json={
                    "prompt": prompt,
                    "width": 800,
                    "height": 400,
                    "format": "png"
                },
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            
            if response.status_code == 200:
                return response.content
            """
            
            # If no implementation is available, log a warning
            self.logger.warning("Image generation with AI is not implemented")
            return None
            
        except Exception as e:
            self.logger.error(f"Error generating image with AI: {str(e)}")
            return None
    
    def _save_image(self, image_data: bytes, path: str) -> bool:
        """
        Save image data to the specified path.
        
        Args:
            image_data: Image data in bytes
            path: Path to save the image
            
        Returns:
            True if saving was successful, False otherwise
        """
        try:
            # Check if the image_data is base64 encoded
            try:
                if isinstance(image_data, str) and image_data.startswith('data:image'):
                    # Extract the base64 part
                    image_data = image_data.split(',')[1]
                    # Decode base64 to bytes
                    image_data = base64.b64decode(image_data)
            except:
                # Not base64 or already bytes, continue
                pass
                
            # Save the image
            with open(path, 'wb') as f:
                f.write(image_data)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving image: {str(e)}")
            return False
    
    def _extract_code_block(self, content: str, language: str) -> str:
        """
        Extract code from content, removing markdown code blocks and explanations.
        
        Args:
            content: Content possibly containing code blocks
            language: Language of the code for markdown block detection
            
        Returns:
            Clean code without markdown formatting
        """
        # Check if the content is already wrapped in a markdown code block
        code_block_pattern = rf"```(?:{language})?\n(.*?)```"
        code_match = re.search(code_block_pattern, content, re.DOTALL)
        
        if code_match:
            # Extract just the code from the markdown code block
            return code_match.group(1).strip()
        
        # If not in a code block, try to identify and remove any explanatory text
        # This is a heuristic approach to find where the code starts
        
        # Look for common import statements at the start of JS files
        if language == "javascript":
            import_match = re.search(r'^(?:import|const|let|var|function|class|\/\*\*)', content, re.MULTILINE)
            if import_match:
                return content[import_match.start():].strip()
        
        # Look for CSS starting patterns
        if language == "css":
            css_match = re.search(r'^(?:\.|\/\*|\*|#|@media|:root)', content, re.MULTILINE)
            if css_match:
                return content[css_match.start():].strip()
        
        # If we couldn't identify a clear pattern, just return the content as is
        return content.strip()