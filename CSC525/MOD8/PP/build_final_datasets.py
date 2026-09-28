"""Build independent calibration and final-test datasets for the chatbot."""

from __future__ import annotations

import csv
import shutil
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
COURSE_DIR = BASE_DIR.parents[1]
DATA_DIR = BASE_DIR / "data"
TRAINING_PATH = DATA_DIR / "training_corpus.csv"
LEGACY_TRAINING_PATH = (
    COURSE_DIR / "MOD6" / "PM" / "data" / "custom_enterprise_faq_sop_corpus.csv"
)
CALIBRATION_PATH = DATA_DIR / "calibration_messages.csv"
TEST_PATH = DATA_DIR / "test_messages.csv"
OOD = "__out_of_domain__"


CALIBRATION_MESSAGES = {
    "account_access": [
        "I changed my password yesterday and now the portal will not let me in.",
        "Why does the website keep saying my sign-in is invalid?",
        "Please restore access to my online profile.",
        "My user account appears to be locked.",
    ],
    "billing_invoice": [
        "Could you email me the receipt for the payment I made last week?",
        "The amount due on this statement does not look correct.",
        "I need to change the person who receives our invoices.",
        "Why was my card charged twice for the same purchase?",
    ],
    "human_escalation": [
        "I have tried the automated steps and need a real person now.",
        "Please have a supervisor review this unresolved problem.",
        "Can a support representative call me back today?",
        "This complaint needs to be escalated beyond the chatbot.",
    ],
    "onboarding_help": [
        "I just joined the company and do not know which setup tasks come first.",
        "What should a newly created user complete during orientation?",
        "Please send the checklist for getting a new employee started.",
        "Where are the initial setup instructions for a first-time user?",
    ],
    "order_status": [
        "My package was supposed to arrive yesterday. Where is it?",
        "Can you tell me whether order 4821 has shipped?",
        "The tracking page has not changed in several days.",
        "I am still waiting and need an updated delivery estimate.",
    ],
    "policy_lookup": [
        "Which company rule applies before this request can be approved?",
        "Please locate the official procedure for handling this situation.",
        "I need the current compliance guideline before I respond.",
        "Where is the controlled SOP that explains the required approvals?",
    ],
    "returns_refunds": [
        "The item is not right for me. How can I send it back?",
        "When should the money from my cancelled purchase be credited?",
        "Can I swap this product for a different model?",
        "Please help me determine whether I am still inside the return period.",
    ],
    "service_scheduling": [
        "Could we move the technician visit from Tuesday to Thursday?",
        "I need to book a repair appointment at my location.",
        "What times are open for a service call next week?",
        "Please cancel the current appointment and choose another day.",
    ],
    "technical_support": [
        "The application crashes every time I try to save my work.",
        "My device stopped responding after the latest setup step.",
        "I keep seeing an error code and need troubleshooting help.",
        "A feature is broken even after I restarted the software.",
    ],
    "training_materials": [
        "Is there a video or manual that teaches this workflow?",
        "Please point me to the latest knowledge article for this tool.",
        "Our team needs documentation before using the new process.",
        "Where can I find a tutorial that explains this task?",
    ],
    OOD: [
        "What is the weather forecast for this weekend?",
        "Tell me the current stock price for a technology company.",
        "Write a short poem about summer.",
        "Who won the basketball game last night?",
        "What is the capital city of Brazil?",
        "Can you recommend a restaurant near the airport?",
        "How many miles are in a marathon?",
        "Please translate hello into Japanese.",
        "What movies are playing downtown?",
        "Give me a recipe for chocolate cake.",
        "Set an alarm for seven tomorrow morning.",
        "Explain how photosynthesis works.",
    ],
}


TEST_MESSAGES = {
    "account_access": [
        "After too many attempts I can no longer sign into the dashboard.",
        "The portal refuses every password I try.",
        "I lost access to my profile after resetting my credentials.",
        "Can someone help me recover my username and enter the account?",
        "My authentication is failing even though the account should be active.",
    ],
    "billing_invoice": [
        "I am confused because the balance on this month's statement increased.",
        "Where can I download proof that my invoice was paid?",
        "There is an unfamiliar fee listed on our latest bill.",
        "Please resend invoice 775 to the correct billing contact.",
        "The payment went through, but my account still shows an amount due.",
    ],
    "human_escalation": [
        "This is the third time I have asked; transfer me to a manager.",
        "The suggested answer did not help, so I need a live agent.",
        "I would like a person to take ownership of this urgent case.",
        "Please stop the automated conversation and connect me with support.",
        "Who can review a complaint that remains unresolved?",
    ],
    "onboarding_help": [
        "My first day is Monday. What accounts and training should I set up?",
        "A new teammate needs the getting-started steps for this system.",
        "I have never used this portal and need the introductory checklist.",
        "What orientation materials are required for a new hire?",
        "Help me prepare system access and initial training for a new user.",
    ],
    "order_status": [
        "I am frustrated that my purchase still has no delivery update.",
        "Has the warehouse fulfilled my order yet?",
        "The carrier number is available, but it shows no movement.",
        "When should I expect the shipment from my recent purchase?",
        "Please check whether order 9107 is still being processed.",
    ],
    "policy_lookup": [
        "Before taking action, I need to verify what the official policy permits.",
        "Which documented rule covers approval of this type of exception?",
        "Can you find the current SOP for responding to this case?",
        "I need the compliance requirement and its controlled source document.",
        "What procedure should the team follow before completing this request?",
    ],
    "returns_refunds": [
        "The product arrived damaged and I would like my money back.",
        "How do I obtain a label to ship this item back?",
        "I cancelled the order but have not received the credit.",
        "Would this purchase qualify for an exchange instead of a refund?",
        "Please explain the steps for returning something bought last week.",
    ],
    "service_scheduling": [
        "No one can be home Wednesday; can the service visit be moved?",
        "I would like the earliest available technician appointment.",
        "Please arrange an on-site service call for next month.",
        "The scheduled time no longer works and needs to be changed.",
        "Is there any availability on the repair calendar this Friday?",
    ],
    "technical_support": [
        "The screen freezes whenever I open the reporting feature.",
        "Installation finished, but the product will not start.",
        "Can someone diagnose why the application keeps displaying error 51?",
        "The device disconnects repeatedly and normal troubleshooting did not work.",
        "I need product support because an important function stopped working.",
    ],
    "training_materials": [
        "I cannot remember this process. Is there a current user guide?",
        "Could you share the approved lesson for learning this software?",
        "Where is the reference manual for the new workflow?",
        "The team needs a step-by-step tutorial before tomorrow's training.",
        "Please send the latest documentation from the knowledge base.",
    ],
    OOD: [
        "How tall is the tallest building in the world?",
        "Find me a flight from Denver to Chicago.",
        "What is the score of today's baseball game?",
        "Summarize the plot of a science fiction movie.",
        "How do I grow tomatoes in a small garden?",
        "Convert 200 degrees Fahrenheit to Celsius.",
        "What time does the public library close?",
        "Create a grocery list for a camping trip.",
        "Who is the governor of Colorado?",
        "Can you solve a quadratic equation for me?",
        "Play some relaxing music.",
        "What is the exchange rate between dollars and euros?",
    ],
}


def ensure_training_corpus() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if TRAINING_PATH.exists():
        return
    if not LEGACY_TRAINING_PATH.exists():
        raise FileNotFoundError(
            "Training corpus is missing. Include data/training_corpus.csv in the package."
        )
    shutil.copy2(LEGACY_TRAINING_PATH, TRAINING_PATH)


def write_messages(path: Path, groups: dict[str, list[str]], split: str) -> None:
    rows: list[dict[str, str]] = []
    for expected_route, messages in groups.items():
        case_type = "out_of_domain" if expected_route == OOD else "in_domain"
        for index, message in enumerate(messages, start=1):
            rows.append(
                {
                    "message_id": f"{split}_{expected_route}_{index:02d}",
                    "message": message,
                    "expected_route": expected_route,
                    "case_type": case_type,
                }
            )
    with path.open("w", encoding="utf-8", newline="") as file_obj:
        writer = csv.DictWriter(
            file_obj,
            fieldnames=["message_id", "message", "expected_route", "case_type"],
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    ensure_training_corpus()
    write_messages(CALIBRATION_PATH, CALIBRATION_MESSAGES, "calibration")
    write_messages(TEST_PATH, TEST_MESSAGES, "test")
    print(f"Training rows: {sum(1 for _ in TRAINING_PATH.open(encoding='utf-8-sig')) - 1}")
    print(f"Calibration rows: {sum(len(items) for items in CALIBRATION_MESSAGES.values())}")
    print(f"Test rows: {sum(len(items) for items in TEST_MESSAGES.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
