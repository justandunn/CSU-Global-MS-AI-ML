# personality_traits.py

class Trait:
    def __init__(self, name, description):
        self.name = name
        self.description = description

class DeveloperBuilder:
    def __init__(self):
        self.traits = []

    def add_trait(self, trait):
        self.traits.append(trait)
        return self

    def build(self):
        return self.traits

if __name__ == "__main__":
    # Define traits
    collaboration = Trait("Collaboration", "Works effectively in teams and communicates clearly.")
    problem_solving = Trait("Problem-Solving", "Able to identify problems and create efficient solutions.")
    adaptability = Trait("Adaptability", "Quickly learns new tools and adjusts to project changes.")

    # Build developer traits list
    builder = DeveloperBuilder()
    traits = builder.add_trait(collaboration).add_trait(problem_solving).add_trait(adaptability).build()

    # Output program description
    print("=== Common Personality Traits of Excellent Software Developers ===\n")
    print("This program demonstrates how key personality traits can be built step by step (Builder Pattern).")
    print(f"\nTotal Traits: {len(traits)}\n")

    # Show each trait
    for i, t in enumerate(traits, start=1):
        print(f"{i}. {t.name} - {t.description}")

    # Show steps
    print("\nSteps in Program:")
    print("1. Define traits")
    print("2. Add traits using DeveloperBuilder")
    print("3. Build final developer profile")
    print("4. Print results")
