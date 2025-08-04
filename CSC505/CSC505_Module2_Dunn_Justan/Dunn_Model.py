class Dunn:
    def __init__(self):
        self.phases = {
            "Communication": [],
            "Planning": [],
            "Modeling": [],
            "Construction": [],
            "Evaluation": [],  # Dunn Addition
            "Deployment": []
        }

    def prompt_user_input(self):
        print("Welcome to the Dunn Model Input Wizard.\n")
        for phase in self.phases:
            print(f"Enter tasks for the '{phase}' phase (type 'done' when finished):")
            while True:
                task = input(f"  - Task for {phase}: ").strip()
                if task.lower() == "done":
                    break
                elif task == "":
                    continue
                self.phases[phase].append(task)
            print()  # spacing between phases

    def display_model(self):
        print("\n========== Dunn Model ==========\n")
        for phase, tasks in self.phases.items():
            print(f"{phase}:")
            for task in tasks:
                print(f"  • {task}")
            print()  # spacing between phases


if __name__ == "__main__":
    model = Dunn()
    model.prompt_user_input()
    model.display_model()