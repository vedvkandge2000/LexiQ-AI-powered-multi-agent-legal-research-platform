#!/usr/bin/env python3
"""
Sample test cases based on the actual database content
"""

# Sample Case Descriptions for Testing LexiQ

SAMPLE_CASES = {
    
    # Constitutional Law Cases
    "constitutional_rights": """
    Case: Fundamental Rights Violation

    Facts: The petitioner challenges the constitutionality of a state law that restricts online speech and requires pre-approval of social media posts. The law was enacted under Article 19(2) of the Constitution claiming it protects public order and decency.

    Legal Issues:
    1. Whether the law violates Article 19(1)(a) - freedom of speech and expression?
    2. Are the restrictions under Article 19(2) reasonable and proportionate?
    3. Does the law constitute prior restraint and censorship?

    The petitioner argues that the law creates an unconstitutional chilling effect on free speech and lacks procedural safeguards.
    """,
    
    # Criminal Law Cases  
    "criminal_appeal": """
    Case: Criminal Appeal - Conviction Challenge

    Facts: The appellants were convicted by the trial court under Section 302 IPC for murder and sentenced to life imprisonment. The conviction was affirmed by the High Court. The appellants now challenge the conviction before the Supreme Court.

    Legal Issues:
    1. Whether the chain of circumstantial evidence is complete and conclusive?
    2. Whether the prosecution has proved the guilt beyond reasonable doubt?
    3. Whether the appellants are entitled to acquittal due to insufficient evidence?

    The case involves analysis of circumstantial evidence and the principle that all circumstances must point conclusively to the guilt of the accused.
    """,
    
    # POCSO/Child Protection Cases
    "pocso_case": """
    Case: POCSO Act Violation

    Facts: The accused was charged under the Protection of Children from Sexual Offences Act, 2012 and Information Technology Act, 2000 for online harassment and exploitation of a minor. The trial court convicted the accused, which was upheld by the High Court.

    Legal Issues:
    1. Whether the prosecution has established all ingredients of the POCSO Act violation?
    2. Whether the IT Act charges are maintainable along with POCSO charges?
    3. Whether the sentence imposed is appropriate and proportionate?

    The case involves interpretation of POCSO Act provisions and the intersection of cyber laws with child protection laws.
    """,
    
    # Anticipatory Bail Cases
    "anticipatory_bail": """
    Case: Anticipatory Bail Application

    Facts: The petitioner apprehends arrest in connection with a criminal case and seeks anticipatory bail under Section 438 CrPC. The petitioner claims false implication and seeks protection from arrest.

    Legal Issues:
    1. Whether the petitioner has made out a case for grant of anticipatory bail?
    2. Whether there are reasonable grounds to believe the petitioner may be arrested?
    3. What conditions should be imposed if bail is granted?

    The petitioner argues that the allegations are false and motivated, and that custodial interrogation is not necessary.
    """,
    
    # Review Petition Cases
    "review_petition": """
    Case: Review Petition - Error of Law

    Facts: The petitioner filed a review petition seeking review of a judgment on the ground that there was an apparent error of law in the decision. The court had earlier dismissed the main petition.

    Legal Issues:
    1. Whether there is an apparent error of law that warrants review?
    2. Whether the review petition is maintainable under Order XLVII Rule 1 CPC?
    3. Whether the court should entertain the review application?

    The case involves the scope and limitations of review jurisdiction and the principle that review is not an appeal in disguise.
    """,
    
    # Corporate/Commercial Cases
    "corporate_debtor": """
    Case: Corporate Debtor - Homebuyer Rights

    Facts: The appellants are homebuyers who paid substantial amounts (Rs.57,56,684 out of Rs.60,06,368) for apartments in a project developed by a Corporate Debtor. The Corporate Debtor went into insolvency and the appellants seek priority in the resolution process.

    Legal Issues:
    1. Whether homebuyers who have paid substantial amounts are entitled to priority treatment?
    2. Whether they should be treated as belated claimants entitled only to 50% refund?
    3. What is the appropriate treatment of homebuyer claims in insolvency proceedings?

    The case involves interpretation of IBC provisions and the rights of homebuyers in corporate insolvency resolution process.
    """,
    
    # Contract Law Cases
    "contract_dispute": """
    Case: Breach of Contract - Damages

    Facts: The plaintiff entered into a contract with the defendant for supply of goods worth Rs.50 lakhs. The defendant failed to deliver the goods on time, causing loss to the plaintiff's business. The plaintiff seeks damages for breach of contract.

    Legal Issues:
    1. Whether there was a valid contract between the parties?
    2. Whether the defendant committed breach of contract?
    3. What is the quantum of damages payable to the plaintiff?

    The case involves principles of contract law, breach of contract, and assessment of damages.
    """,
    
    # Civil Procedure Cases
    "civil_procedure": """
    Case: Civil Procedure - Jurisdiction

    Facts: The plaintiff filed a suit for recovery of money in the Civil Court. The defendant raised an objection regarding jurisdiction, claiming the matter should be heard by the Commercial Court due to the commercial nature of the dispute.

    Legal Issues:
    1. Whether the Civil Court has jurisdiction to entertain the suit?
    2. Whether the dispute is of commercial nature requiring transfer to Commercial Court?
    3. What is the appropriate forum for adjudication of the dispute?

    The case involves interpretation of Civil Procedure Code provisions relating to jurisdiction and the Commercial Courts Act.
    """,
    
    # Constitutional Validity Cases
    "constitutional_validity": """
    Case: Constitutional Validity Challenge

    Facts: The petitioner challenges the constitutional validity of a state legislation that imposes restrictions on fundamental rights. The state defends the law as being within the permissible restrictions under the Constitution.

    Legal Issues:
    1. Whether the impugned legislation violates fundamental rights?
    2. Whether the restrictions are reasonable and within the scope of Article 19(2)?
    3. Whether the law passes the test of constitutional validity?

    The case involves analysis of constitutional provisions, fundamental rights, and the doctrine of reasonable restrictions.
    """,
    
    # Right to Life Cases
    "right_to_life": """
    Case: Right to Life and Personal Liberty

    Facts: The petitioner was detained under preventive detention laws. The petitioner challenges the detention order as violative of Article 21 of the Constitution, claiming it lacks proper grounds and violates procedural safeguards.

    Legal Issues:
    1. Whether the detention order violates Article 21 - right to life and personal liberty?
    2. Whether proper procedural safeguards were followed in passing the detention order?
    3. Whether the grounds for detention are sufficient and valid?

    The case involves interpretation of Article 21 and the scope of preventive detention laws in India.
    """
}

def get_sample_case(case_type: str = None):
    """
    Get a sample case for testing.
    
    Args:
        case_type: Type of case to retrieve (optional)
        
    Returns:
        Dictionary of sample cases or specific case
    """
    if case_type:
        return SAMPLE_CASES.get(case_type, "Case type not found")
    
    return SAMPLE_CASES

def print_all_cases():
    """Print all available sample cases."""
    print("=" * 80)
    print("SAMPLE TEST CASES FOR LEXIQ")
    print("=" * 80)
    print("\nThese cases are designed to match content in your Supreme Court database.")
    print("They cover various areas of law found in your vector store.\n")
    
    for case_type, case_text in SAMPLE_CASES.items():
        print(f"--- {case_type.upper().replace('_', ' ')} ---")
        print(case_text[:200] + "...")
        print()

if __name__ == "__main__":
    print_all_cases()
    
    print("\n" + "=" * 80)
    print("USAGE EXAMPLES")
    print("=" * 80)
    print("\nTo get a specific case:")
    print("from sample_test_cases import get_sample_case")
    print("case = get_sample_case('constitutional_rights')")
    print("\nTo get all cases:")
    print("all_cases = get_sample_case()")
    print("\nAvailable case types:")
    for case_type in SAMPLE_CASES.keys():
        print(f"  • {case_type}")
