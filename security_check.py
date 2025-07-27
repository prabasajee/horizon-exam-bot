#!/usr/bin/env python3
"""
Security Checker for Horizon Exam Bot
Performs comprehensive security analysis and vulnerability scanning
"""

import os
import re
import json
import sys
from typing import List, Dict, Any
import subprocess
from datetime import datetime


class SecurityIssue:
    """Represents a security issue"""
    
    def __init__(self, severity: str, category: str, description: str, 
                 file_path: str = "", line_number: int = 0, 
                 recommendation: str = "", code_snippet: str = ""):
        self.severity = severity  # CRITICAL, HIGH, MEDIUM, LOW
        self.category = category
        self.description = description
        self.file_path = file_path
        self.line_number = line_number
        self.recommendation = recommendation
        self.code_snippet = code_snippet
        self.timestamp = datetime.now().isoformat()


class SecurityChecker:
    """Main security checker class"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = os.path.abspath(project_root)
        self.issues: List[SecurityIssue] = []
        
    def scan_all(self) -> List[SecurityIssue]:
        """Run all security checks"""
        print("🔍 Starting comprehensive security scan...")
        
        self.check_hardcoded_secrets()
        self.check_debug_mode()
        self.check_security_configurations()
        self.check_file_upload_security()
        self.check_input_validation()
        self.check_error_handling()
        self.check_dependencies()
        self.check_security_headers()
        self.check_session_management()
        self.check_xss_vulnerabilities()
        
        return self.issues
    
    def check_hardcoded_secrets(self):
        """Check for hardcoded secrets and credentials"""
        print("🔐 Checking for hardcoded secrets...")
        
        secret_patterns = [
            (r'SECRET_KEY\s*=\s*[\'"][^\'\"]*[\'"]', 'Hardcoded Secret Key'),
            (r'password\s*=\s*[\'"][^\'\"]+[\'"]', 'Hardcoded Password'),
            (r'api_key\s*=\s*[\'"][^\'\"]+[\'"]', 'Hardcoded API Key'),
            (r'token\s*=\s*[\'"][^\'\"]+[\'"]', 'Hardcoded Token'),
            (r'your-secret-key-here', 'Default Secret Key'),
            (r'your-secret-key-change-this', 'Default Secret Key Template'),
        ]
        
        python_files = self._get_python_files()
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                for i, line in enumerate(lines, 1):
                    for pattern, description in secret_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            self.issues.append(SecurityIssue(
                                severity="CRITICAL",
                                category="Secrets Management",
                                description=f"{description} found in code",
                                file_path=file_path,
                                line_number=i,
                                code_snippet=line.strip(),
                                recommendation="Use environment variables or secure secret management"
                            ))
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    
    def check_debug_mode(self):
        """Check for debug mode configurations"""
        print("🐛 Checking debug mode configurations...")
        
        debug_patterns = [
            r'debug\s*=\s*True',
            r'FLASK_DEBUG\s*=\s*True',
            r'DEBUG\s*=\s*True',
            r'app\.run\([^)]*debug\s*=\s*True',
        ]
        
        python_files = self._get_python_files()
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                for i, line in enumerate(lines, 1):
                    for pattern in debug_patterns:
                        if re.search(pattern, line):
                            self.issues.append(SecurityIssue(
                                severity="HIGH",
                                category="Configuration",
                                description="Debug mode enabled",
                                file_path=file_path,
                                line_number=i,
                                code_snippet=line.strip(),
                                recommendation="Disable debug mode in production"
                            ))
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    
    def check_security_configurations(self):
        """Check for insecure configurations"""
        print("⚙️ Checking security configurations...")
        
        config_issues = [
            (r'host\s*=\s*[\'"]0\.0\.0\.0[\'"]', 'Binding to all interfaces'),
            (r'ssl_context\s*=\s*None', 'SSL disabled'),
            (r'verify\s*=\s*False', 'SSL verification disabled'),
        ]
        
        python_files = self._get_python_files()
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                for i, line in enumerate(lines, 1):
                    for pattern, description in config_issues:
                        if re.search(pattern, line):
                            self.issues.append(SecurityIssue(
                                severity="MEDIUM",
                                category="Configuration",
                                description=description,
                                file_path=file_path,
                                line_number=i,
                                code_snippet=line.strip(),
                                recommendation="Use secure configuration for production"
                            ))
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    
    def check_file_upload_security(self):
        """Check file upload security"""
        print("📁 Checking file upload security...")
        
        # Check for secure_filename usage
        found_secure_filename = False
        python_files = self._get_python_files()
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'secure_filename' in content:
                        found_secure_filename = True
                    
                    # Check for file size limits
                    if 'MAX_CONTENT_LENGTH' not in content and 'request.files' in content:
                        self.issues.append(SecurityIssue(
                            severity="MEDIUM",
                            category="File Upload",
                            description="File upload without size limit",
                            file_path=file_path,
                            recommendation="Implement file size limits"
                        ))
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    
    def check_input_validation(self):
        """Check for input validation issues"""
        print("✅ Checking input validation...")
        
        validation_patterns = [
            (r'request\.args\.get\([^)]+\)', 'Unvalidated query parameter'),
            (r'request\.form\.get\([^)]+\)', 'Unvalidated form input'),
            (r'request\.get_json\(\)', 'Unvalidated JSON input'),
        ]
        
        python_files = self._get_python_files()
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                for i, line in enumerate(lines, 1):
                    for pattern, description in validation_patterns:
                        if re.search(pattern, line):
                            # Check if there's validation nearby or if it's part of validation function
                            context_lines = lines[max(0, i-3):i+3]
                            context = '\n'.join(context_lines)
                            
                            # Skip if it's part of validation function or has validation
                            if ('validate_json_input' in context or 
                                'def validate_' in context or
                                any(keyword in context.lower() for keyword in 
                                   ['validate', 'check', 'verify', 'sanitize', 'if not', 'required_fields'])):
                                continue
                                
                            self.issues.append(SecurityIssue(
                                severity="MEDIUM",
                                category="Input Validation",
                                description=description,
                                file_path=file_path,
                                line_number=i,
                                code_snippet=line.strip(),
                                recommendation="Add proper input validation and sanitization"
                            ))
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    
    def check_error_handling(self):
        """Check error handling for information disclosure"""
        print("🚨 Checking error handling...")
        
        python_files = self._get_python_files()
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                for i, line in enumerate(lines, 1):
                    # Check for exposed error messages
                    if re.search(r'return.*str\(e\)', line):
                        self.issues.append(SecurityIssue(
                            severity="MEDIUM",
                            category="Information Disclosure",
                            description="Error message may expose internal information",
                            file_path=file_path,
                            line_number=i,
                            code_snippet=line.strip(),
                            recommendation="Use generic error messages for users"
                        ))
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    
    def check_dependencies(self):
        """Check for dependency vulnerabilities"""
        print("📦 Checking dependencies...")
        
        requirements_file = os.path.join(self.project_root, 'requirements.txt')
        
        if os.path.exists(requirements_file):
            try:
                # Try to use safety if available
                result = subprocess.run(['safety', 'check', '-r', requirements_file], 
                                      capture_output=True, text=True)
                if result.returncode != 0 and 'not found' not in result.stderr:
                    self.issues.append(SecurityIssue(
                        severity="HIGH",
                        category="Dependencies",
                        description="Potential vulnerabilities in dependencies",
                        file_path=requirements_file,
                        recommendation="Run 'pip install safety && safety check' for detailed analysis"
                    ))
            except FileNotFoundError:
                self.issues.append(SecurityIssue(
                    severity="LOW",
                    category="Dependencies",
                    description="Cannot check dependencies - safety tool not installed",
                    file_path=requirements_file,
                    recommendation="Install 'safety' tool for dependency vulnerability scanning"
                ))
    
    def check_security_headers(self):
        """Check for security headers implementation"""
        print("🛡️ Checking security headers...")
        
        security_headers = [
            'Content-Security-Policy',
            'X-Frame-Options',
            'X-Content-Type-Options',
            'X-XSS-Protection',
            'Strict-Transport-Security'
        ]
        
        python_files = self._get_python_files()
        found_headers = False
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for header in security_headers:
                        if header in content:
                            found_headers = True
                            break
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
        
        if not found_headers:
            self.issues.append(SecurityIssue(
                severity="MEDIUM",
                category="Security Headers",
                description="Missing security headers",
                recommendation="Implement security headers middleware"
            ))
    
    def check_session_management(self):
        """Check session management security"""
        print("🔒 Checking session management...")
        
        python_files = self._get_python_files()
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Check for secure session configuration
                    if 'session' in content.lower():
                        if 'SESSION_COOKIE_SECURE' not in content:
                            self.issues.append(SecurityIssue(
                                severity="MEDIUM",
                                category="Session Management",
                                description="Session cookies not configured as secure",
                                file_path=file_path,
                                recommendation="Set SESSION_COOKIE_SECURE=True for HTTPS"
                            ))
                        
                        if 'SESSION_COOKIE_HTTPONLY' not in content:
                            self.issues.append(SecurityIssue(
                                severity="MEDIUM",
                                category="Session Management",
                                description="Session cookies not configured as HTTP-only",
                                file_path=file_path,
                                recommendation="Set SESSION_COOKIE_HTTPONLY=True"
                            ))
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    
    def check_xss_vulnerabilities(self):
        """Check for XSS vulnerabilities in templates"""
        print("🕷️ Checking for XSS vulnerabilities...")
        
        template_files = []
        templates_dir = os.path.join(self.project_root, 'templates')
        
        if os.path.exists(templates_dir):
            for file in os.listdir(templates_dir):
                if file.endswith('.html'):
                    template_files.append(os.path.join(templates_dir, file))
        
        for file_path in template_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                for i, line in enumerate(lines, 1):
                    # Check for unescaped variables
                    if re.search(r'\{\{\s*[^}|]+\s*\}\}', line):
                        if '|safe' in line or '|e' not in line:
                            self.issues.append(SecurityIssue(
                                severity="HIGH",
                                category="XSS",
                                description="Potential XSS vulnerability in template",
                                file_path=file_path,
                                line_number=i,
                                code_snippet=line.strip(),
                                recommendation="Use proper escaping or validate input"
                            ))
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    
    def _get_python_files(self) -> List[str]:
        """Get all Python files in the project"""
        python_files = []
        
        for root, dirs, files in os.walk(self.project_root):
            # Skip common directories
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'venv', '.env']]
            
            for file in files:
                if file.endswith('.py') and file != 'security_check.py':  # Exclude self
                    python_files.append(os.path.join(root, file))
        
        return python_files
    
    def generate_report(self) -> str:
        """Generate a comprehensive security report"""
        if not self.issues:
            return "✅ No security issues found!"
        
        # Sort issues by severity
        severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        sorted_issues = sorted(self.issues, key=lambda x: severity_order.get(x.severity, 4))
        
        report = []
        report.append("🔒 SECURITY SCAN REPORT")
        report.append("=" * 50)
        report.append(f"Scan completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total issues found: {len(self.issues)}")
        report.append("")
        
        # Summary by severity
        severity_counts = {}
        for issue in self.issues:
            severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1
        
        report.append("📊 SEVERITY BREAKDOWN:")
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            count = severity_counts.get(severity, 0)
            if count > 0:
                emoji = {'CRITICAL': '🚨', 'HIGH': '⚠️', 'MEDIUM': '💛', 'LOW': '💙'}[severity]
                report.append(f"  {emoji} {severity}: {count}")
        report.append("")
        
        # Detailed issues
        current_severity = None
        for issue in sorted_issues:
            if issue.severity != current_severity:
                current_severity = issue.severity
                emoji = {'CRITICAL': '🚨', 'HIGH': '⚠️', 'MEDIUM': '💛', 'LOW': '💙'}[issue.severity]
                report.append(f"{emoji} {issue.severity} SEVERITY ISSUES:")
                report.append("-" * 30)
            
            report.append(f"Category: {issue.category}")
            report.append(f"Description: {issue.description}")
            if issue.file_path:
                report.append(f"File: {issue.file_path}")
            if issue.line_number:
                report.append(f"Line: {issue.line_number}")
            if issue.code_snippet:
                report.append(f"Code: {issue.code_snippet}")
            if issue.recommendation:
                report.append(f"Recommendation: {issue.recommendation}")
            report.append("")
        
        return "\n".join(report)
    
    def save_report(self, filename: str = "security_report.txt"):
        """Save the security report to a file"""
        report = self.generate_report()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"📄 Security report saved to: {filename}")


def main():
    """Main function"""
    print("🔒 Horizon Exam Bot Security Checker")
    print("=" * 40)
    
    checker = SecurityChecker()
    issues = checker.scan_all()
    
    print("\n" + checker.generate_report())
    
    # Save report
    checker.save_report()
    
    # Exit with error code if critical or high severity issues found
    critical_or_high = [i for i in issues if i.severity in ['CRITICAL', 'HIGH']]
    if critical_or_high:
        print(f"\n❌ Found {len(critical_or_high)} critical/high severity issues!")
        print("🔧 Please fix these issues before deploying to production.")
        sys.exit(1)
    else:
        print("\n✅ No critical or high severity issues found.")
        sys.exit(0)


if __name__ == "__main__":
    main()