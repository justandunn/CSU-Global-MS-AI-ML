"""Create a sanitized enterprise FAQ/SOP corpus for the chatbot milestone.

The Module 4 Portfolio Milestone selected a hybrid dataset strategy:
RSiCS for customer-service language patterns, WikiQA for answer-selection
logic, and a custom enterprise FAQ/SOP corpus for the domain-specific
knowledge base. This script builds the custom corpus used for the Module 5
training run without using private company data.
"""

from __future__ import annotations

import csv
from pathlib import Path


OUTPUT_PATH = Path(__file__).resolve().parent / "data" / "custom_enterprise_faq_sop_corpus.csv"


ROUTE_DEFINITIONS = {
    "account_access": {
        "category": "Account Access",
        "keywords": "login account profile access locked username portal authentication",
        "answer": (
            "Verify the user identity, confirm the account status, and route the "
            "case to account access support if portal access cannot be restored."
        ),
        "questions": [
            "I cannot log in to my account dashboard.",
            "My profile is locked and I need access restored.",
            "The customer portal says my username is not recognized.",
            "I need help getting back into my account.",
            "The login page keeps rejecting my credentials.",
            "Can support unlock my online profile?",
            "I am blocked from the company portal.",
            "My account access stopped working after the last password change.",
        ],
    },
    "billing_invoice": {
        "category": "Billing and Invoice",
        "keywords": "invoice bill charge payment receipt statement billing balance due",
        "answer": (
            "Review the invoice number, payment status, billing contact, and account "
            "balance before routing unresolved issues to billing support."
        ),
        "questions": [
            "I need a copy of my latest invoice.",
            "There is a charge on my bill that I do not recognize.",
            "Can you explain why my account balance changed?",
            "My payment receipt did not arrive by email.",
            "The invoice total looks different than expected.",
            "I need help updating the billing contact.",
            "Where can I download a statement for this month?",
            "The customer says the bill was already paid.",
        ],
    },
    "human_escalation": {
        "category": "Escalation",
        "keywords": "representative human agent supervisor escalation urgent complaint unresolved",
        "answer": (
            "Acknowledge the request, collect the case context, and transfer the "
            "conversation to the appropriate human support queue."
        ),
        "questions": [
            "I want to speak with a person about this issue.",
            "Please connect me with a supervisor.",
            "This problem is urgent and needs escalation.",
            "The automated answer did not solve my case.",
            "I need a human agent to review my account.",
            "Can someone from support call me back?",
            "This complaint needs to go to a manager.",
            "Route this conversation to a live representative.",
        ],
    },
    "onboarding_help": {
        "category": "Onboarding",
        "keywords": "onboarding setup new user training orientation guide first time",
        "answer": (
            "Send the onboarding checklist, confirm the user's role, and provide "
            "links to the approved setup and training materials."
        ),
        "questions": [
            "I am a new user and need the onboarding checklist.",
            "Where do I start with the system setup?",
            "Can you send the first-time user guide?",
            "I need help completing my orientation steps.",
            "What training should a new employee complete first?",
            "The new account is active but I do not know what to do next.",
            "Please point me to the onboarding instructions.",
            "I need setup guidance for a new team member.",
        ],
    },
    "order_status": {
        "category": "Order Status",
        "keywords": "order status tracking shipment delivery purchase fulfillment order number",
        "answer": (
            "Look up the order number, confirm fulfillment status, and provide the "
            "latest approved shipment or delivery update."
        ),
        "questions": [
            "Can you check the status of my order?",
            "I need tracking information for a recent purchase.",
            "The order number shows no shipment update.",
            "When will my order be delivered?",
            "Has my purchase been fulfilled yet?",
            "I want to know where my shipment is.",
            "The customer is asking for an order update.",
            "Please review the delivery status for this order.",
        ],
    },
    "policy_lookup": {
        "category": "Policy Lookup",
        "keywords": "policy procedure rule guideline approval compliance document requirement",
        "answer": (
            "Identify the relevant policy or SOP, provide the approved summary, and "
            "link the user to the controlled source document."
        ),
        "questions": [
            "What is the policy for approving this request?",
            "I need the procedure for handling a customer complaint.",
            "Where is the guideline for this process?",
            "Can you find the compliance rule for refunds?",
            "Which SOP explains the approval steps?",
            "I need the official document for this requirement.",
            "What does the company policy say about this case?",
            "Please look up the procedure before I respond.",
        ],
    },
    "returns_refunds": {
        "category": "Returns and Refunds",
        "keywords": "return refund exchange credit cancellation reimbursement return label",
        "answer": (
            "Confirm eligibility, check the purchase record, and provide the approved "
            "return, refund, or exchange workflow."
        ),
        "questions": [
            "How do I start a return?",
            "The customer is asking for a refund.",
            "Can this purchase be exchanged for another item?",
            "I need a return label for my order.",
            "When will the reimbursement be processed?",
            "The cancellation should have created a credit.",
            "Please explain the return window.",
            "I want to check whether this order qualifies for a refund.",
        ],
    },
    "service_scheduling": {
        "category": "Service Scheduling",
        "keywords": "schedule appointment service visit technician availability calendar reschedule",
        "answer": (
            "Check service availability, confirm the customer location and preferred "
            "time, and schedule or reschedule the appointment."
        ),
        "questions": [
            "I need to schedule a service appointment.",
            "Can a technician visit next week?",
            "Please reschedule my service call.",
            "What appointment times are available?",
            "The customer wants to move the visit to Friday.",
            "I need help booking a technician.",
            "Can you check the service calendar?",
            "The appointment needs to be changed to another day.",
        ],
    },
    "technical_support": {
        "category": "Technical Support",
        "keywords": "technical error bug troubleshooting device software issue broken support",
        "answer": (
            "Collect the error details, confirm the affected product or system, and "
            "route the case to technical support if basic troubleshooting fails."
        ),
        "questions": [
            "The software shows an error when I open it.",
            "I need help troubleshooting a device issue.",
            "The product is not working after setup.",
            "Can technical support review this bug?",
            "The screen freezes during the process.",
            "I keep getting the same system error.",
            "The customer says the feature is broken.",
            "Please route this to product support for troubleshooting.",
        ],
    },
    "training_materials": {
        "category": "Training Materials",
        "keywords": "training guide manual tutorial documentation lesson knowledge base material",
        "answer": (
            "Provide the approved training resource, confirm the topic, and direct the "
            "user to the current knowledge-base material."
        ),
        "questions": [
            "Where can I find the training manual?",
            "I need documentation for this workflow.",
            "Can you send a tutorial for the process?",
            "The team needs a guide for this task.",
            "Is there a lesson for using this tool?",
            "Please find the knowledge-base article.",
            "I need training material for a new process.",
            "Can support share the current user guide?",
        ],
    },
}


def main() -> int:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "record_id",
        "source_row_id",
        "route_label",
        "source_category",
        "sample_question",
        "keywords",
        "combined_text",
        "approved_answer",
        "source_note",
    ]

    rows: list[dict[str, str]] = []
    for route_label, definition in sorted(ROUTE_DEFINITIONS.items()):
        for index, question in enumerate(definition["questions"], start=1):
            record_id = f"{route_label}_{index:02d}"
            rows.append(
                {
                    "record_id": record_id,
                    "source_row_id": record_id,
                    "route_label": route_label,
                    "source_category": definition["category"],
                    "sample_question": question,
                    "keywords": definition["keywords"],
                    "combined_text": f"{question} {definition['keywords']}",
                    "approved_answer": definition["answer"],
                    "source_note": (
                        "Sanitized coursework FAQ/SOP sample based on the Module 4 "
                        "custom enterprise knowledge-base dataset plan."
                    ),
                }
            )

    with OUTPUT_PATH.open("w", encoding="utf-8", newline="") as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"wrote={OUTPUT_PATH}")
    print(f"rows={len(rows)}")
    print(f"routes={len(ROUTE_DEFINITIONS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
