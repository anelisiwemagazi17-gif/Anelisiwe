"""
Validation module for SOR Automation System
Validates learner data before PDF generation
"""
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class ValidationIssue:
    field: str
    message: str

@dataclass
class ValidationReport:
    issues: List[ValidationIssue] = field(default_factory=list)
    
    def add_error(self, field: str, message: str):
        self.issues.append(ValidationIssue(field, message))
    
    def has_errors(self) -> bool:
        return len(self.issues) > 0
    
    def print_report(self):
        if self.issues:
            print("Validation Errors:")
            for issue in self.issues:
                print(f"  - {issue.field}: {issue.message}")
        else:
            print("[OK] No validation errors")

class SORValidator:
    """Validates learner data for SOR generation"""
    
    def __init__(self):
        pass
    
    def validate_all(self, learner_data: Dict) -> ValidationReport:
        report = ValidationReport()
        self.validate_learner_info(learner_data.get('learner', {}), report)
        self.validate_profile(learner_data.get('profile', {}), report)
        self.validate_results(learner_data.get('results', []), report)
        return report
    
    def validate_learner_info(self, learner: Dict, report: ValidationReport):
        if not learner.get('firstname') or not learner.get('lastname'):
            report.add_error("Learner", "Full name missing")
        if not learner.get('email'):
            report.add_error("Learner", "Email missing")
    
    def validate_profile(self, profile: Dict, report: ValidationReport):
        # Check for common field name variations
        required_fields = [
            ("Registration Number", ["Registration Number", "registration_number", "reg_number"]),
            ("Date of Birth", ["Date of Birth", "dob", "dateofbirth", "ID Number", "idnumber"]),
            ("Learner Number", ["Learner Number", "learner_number", "learner_id"])
        ]

        for field_display_name, field_variations in required_fields:
            # Check if any variation exists
            found = False
            for variation in field_variations:
                if profile.get(variation):
                    found = True
                    break

            if not found:
                # Soft warning - don't block PDF generation
                print(f"[!]  Warning: {field_display_name} not found (checked: {', '.join(field_variations)})")
    
    def validate_results(self, results: List, report: ValidationReport):
        if not results:
            report.add_error("Results", "No quiz results found")

# Create validator instance
validator = SORValidator()