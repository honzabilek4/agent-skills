---
name: software-design-principles
description: Software design principles and red flags to minimize complexity and ensure maintainability, based on John Ousterhout's "A Philosophy of Software Design." Use this skill whenever writing, reviewing, or refactoring code — apply these principles to every PR review, design discussion, architecture decision, or code cleanup. Use also when someone asks about code quality, complexity, or design patterns.
---

# Software Design Principles

All code should adhere to these software design principles to minimize complexity and ensure maintainability.

## Core Design Principles

1. **Complexity is Incremental:** Sweat the small stuff. Complexity builds up from hundreds of small, poor design choices.
2. **Strategic Programming over Tactical Programming:** Working code isn't enough. Do not introduce unnecessary complexities just to finish the current task faster. The primary goal is a clean, long-term structure.
3. **Continuous Investment in Design:** Spend about 10–20% of your development time on proactive and reactive design improvements.
4. **Design Deep Modules:** The best modules hide a lot of implementation complexity behind a very simple, clean interface. Avoid shallow classes and methods.
5. **Simplify Common Usages:** Interfaces should be designed to make the most common usage as simple as possible. Provide sensible defaults.
6. **Interface Simplicity over Implementation Simplicity:** It is more important for a module to have a simple interface than a simple implementation. The agent should suffer so the user doesn't have to.
7. **Somewhat General-Purpose Modules:** Implement new modules in a somewhat general-purpose fashion: let the functionality reflect current needs, but design the interface to be general enough to support multiple future uses.
8. **Separate General-Purpose and Special-Purpose Code:** Keep general-purpose mechanisms separated from special-purpose policy code, placing the latter in higher layers.
9. **Layered Abstractions:** Different layers of the system must provide different abstractions. If adjacent layers have similar abstractions (e.g. pass-through methods or variables), rethink your decomposition.
10. **Pull Complexity Downward:** Handle complexity internally within a module rather than letting users of the module deal with it.
11. **Define Errors Out of Existence:** Reduce exception handling complexity. Design APIs so that normal behavior handles all cases automatically and there are no exceptional conditions to report.
12. **Design It Twice:** Consider multiple radically different approaches for each major design decision and compare their pros and cons.
13. **Comments Describe Non-Obvious Information:** Comments must capture information that was in the mind of the designer but cannot be represented in the code. Avoid repeating the code. Write comments *first* as a design tool.
14. **Design for Ease of Reading:** Software should be designed for ease of reading, not ease of writing. Choose precise, consistent, and unambiguous names.
15. **Abstractions as Units of Development:** The increments of software development should be clean abstractions, not just raw features.

## Red Flags to Avoid

* **Shallow Module:** The interface for a class or method isn't much simpler than its implementation.
* **Information Leakage:** A design decision is reflected in multiple modules instead of being cleanly encapsulated.
* **Temporal Decomposition:** Code structure matches execution order rather than being organized around information hiding.
* **Overexposure:** An API forces users to learn about rarely used features.
* **Pass-Through Method:** A method does almost nothing except pass its arguments to another method with a similar signature.
* **Repetition:** A nontrivial piece of code is repeated over and over without a clean abstraction.
* **Special-General Mixture:** Special-purpose code is mixed inside a general-purpose mechanism.
* **Conjoined Methods:** Two methods depend on each other so closely that one cannot be understood without the other.
* **Comment Repeats Code:** Comment details are already obvious from looking at the code next to it.
* **Implementation Documentation Contaminates Interface:** An interface comment describes internal implementation details.
* **Vague Name:** A name is so imprecise or generic that it doesn't convey clear behavior.
* **Hard to Pick Name:** If a simple, intuitive name is hard to find, the underlying object design is likely bad.
* **Hard to Describe:** If a method/variable needs a long and complex comment to be complete, its abstraction is likely flawed.
* **Nonobvious Code:** The behavior or meaning of a piece of code cannot be understood quickly.
* **Partial Extraction:** A monolith refactor stops after pulling out the most obvious chunks (prompts, config, DB helpers) but still leaves 3+ distinct concerns — CLI dispatch, orchestration, persistence, I/O formatting — inside the "remaining" file. The test: can you describe each module's single reason to change in one sentence? If not, keep splitting. Extracting by convenience (what's easy) instead of by concern (what each module owns) produces the same spaghetti across more files.
