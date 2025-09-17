#!/usr/bin/env python3
"""
LegalOps Specifications Validator

This script validates all specifications in the LegalOps project
to ensure they meet the defined standards and requirements.
"""

import os
import yaml
import json
import re
from pathlib import Path
from typing import Dict, List, Any

class SpecValidator:
    def __init__(self, specs_dir: str = "specs"):
        self.specs_dir = Path(specs_dir)
        self.config_file = self.specs_dir / "spec-config.yaml"
        self.config = self.load_config()
        self.errors = []
        self.warnings = []
    
    def load_config(self) -> Dict[str, Any]:
        """Load the specification configuration file."""
        try:
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Warning: Configuration file {self.config_file} not found")
            return {}
        except yaml.YAMLError as e:
            print(f"Error loading configuration: {e}")
            return {}
    
    def validate_api_spec(self, file_path: Path) -> bool:
        """Validate OpenAPI specification files."""
        try:
            with open(file_path, 'r') as f:
                if file_path.suffix == '.yaml' or file_path.suffix == '.yml':
                    spec = yaml.safe_load(f)
                else:
                    spec = json.load(f)
            
            # Check required fields
            required_fields = ['openapi', 'info', 'paths']
            for field in required_fields:
                if field not in spec:
                    self.errors.append(f"{file_path}: Missing required field '{field}'")
                    return False
            
            # Check OpenAPI version
            if not spec.get('openapi', '').startswith('3.0'):
                self.warnings.append(f"{file_path}: OpenAPI version should be 3.0.x")
            
            # Check info section
            info = spec.get('info', {})
            if not info.get('title'):
                self.errors.append(f"{file_path}: Missing API title")
            if not info.get('version'):
                self.errors.append(f"{file_path}: Missing API version")
            
            # Check paths
            paths = spec.get('paths', {})
            if not paths:
                self.warnings.append(f"{file_path}: No API paths defined")
            
            return True
            
        except Exception as e:
            self.errors.append(f"{file_path}: Error validating API spec - {e}")
            return False
    
    def validate_markdown_spec(self, file_path: Path) -> bool:
        """Validate Markdown specification files."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for required sections
            required_sections = ['# Overview', '## Requirements', '## Implementation']
            for section in required_sections:
                if section not in content:
                    self.warnings.append(f"{file_path}: Missing recommended section '{section}'")
            
            # Check for broken links
            link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            links = re.findall(link_pattern, content)
            for link_text, link_url in links:
                if link_url.startswith('http'):
                    # External link - just warn
                    self.warnings.append(f"{file_path}: External link '{link_url}' - verify accessibility")
                elif not link_url.startswith('#'):
                    # Internal link - check if file exists
                    target_path = file_path.parent / link_url
                    if not target_path.exists():
                        self.errors.append(f"{file_path}: Broken internal link '{link_url}'")
            
            # Check for images
            img_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
            images = re.findall(img_pattern, content)
            for alt_text, img_url in images:
                if not img_url.startswith('http'):
                    img_path = file_path.parent / img_url
                    if not img_path.exists():
                        self.errors.append(f"{file_path}: Missing image '{img_url}'")
            
            return True
            
        except Exception as e:
            self.errors.append(f"{file_path}: Error validating Markdown spec - {e}")
            return False
    
    def validate_all_specs(self) -> bool:
        """Validate all specifications in the specs directory."""
        print("🔍 Validating LegalOps Specifications...")
        print("=" * 50)
        
        total_files = 0
        valid_files = 0
        
        # Validate API specifications
        api_dir = self.specs_dir / "api"
        if api_dir.exists():
            for file_path in api_dir.glob("*.yaml"):
                total_files += 1
                print(f"📋 Validating API spec: {file_path.name}")
                if self.validate_api_spec(file_path):
                    valid_files += 1
                    print(f"  ✅ Valid")
                else:
                    print(f"  ❌ Invalid")
        
        # Validate system specifications
        system_dir = self.specs_dir / "system"
        if system_dir.exists():
            for file_path in system_dir.glob("*.md"):
                total_files += 1
                print(f"🏗️  Validating system spec: {file_path.name}")
                if self.validate_markdown_spec(file_path):
                    valid_files += 1
                    print(f"  ✅ Valid")
                else:
                    print(f"  ❌ Invalid")
        
        # Validate compliance specifications
        compliance_dir = self.specs_dir / "compliance"
        if compliance_dir.exists():
            for file_path in compliance_dir.glob("*.md"):
                total_files += 1
                print(f"⚖️  Validating compliance spec: {file_path.name}")
                if self.validate_markdown_spec(file_path):
                    valid_files += 1
                    print(f"  ✅ Valid")
                else:
                    print(f"  ❌ Invalid")
        
        # Print summary
        print("\n" + "=" * 50)
        print(f"📊 Validation Summary:")
        print(f"  Total files: {total_files}")
        print(f"  Valid files: {valid_files}")
        print(f"  Invalid files: {total_files - valid_files}")
        
        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")
        
        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        return len(self.errors) == 0
    
    def generate_report(self) -> str:
        """Generate a validation report."""
        report = []
        report.append("# LegalOps Specifications Validation Report")
        report.append(f"Generated: {Path().cwd()}")
        report.append("")
        
        if self.errors:
            report.append("## Errors")
            for error in self.errors:
                report.append(f"- {error}")
            report.append("")
        
        if self.warnings:
            report.append("## Warnings")
            for warning in self.warnings:
                report.append(f"- {warning}")
            report.append("")
        
        if not self.errors and not self.warnings:
            report.append("## Status: ✅ All specifications are valid!")
        
        return "\n".join(report)

def main():
    """Main validation function."""
    validator = SpecValidator()
    
    # Change to the project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Validate all specifications
    is_valid = validator.validate_all_specs()
    
    # Generate and save report
    report = validator.generate_report()
    with open("specs/validation-report.md", "w") as f:
        f.write(report)
    
    print(f"\n📄 Validation report saved to: specs/validation-report.md")
    
    # Exit with appropriate code
    exit(0 if is_valid else 1)

if __name__ == "__main__":
    main()
