---
name: react-dotnet-unit-testing-best-practices
description: Skill for React and .NET unit-testing guidance covering test selection, structure, naming, mocking boundaries, deterministic setup, and common xUnit, Vitest, and Testing Library patterns. Use this when adding tests, covering a bug, writing a unit test, improving coverage, refactoring tests, or reviewing whether test cases are sufficient.
---

# Unit Testing Best Practices

These are the standards for unit tests in this codebase. A unit test verifies one small piece of behavior in isolation, runs fast, and gives an unambiguous pass/fail. The goal is a suite that catches real regressions, reads as living documentation, and rarely breaks for the wrong reasons.

## Core principles (apply to both backend and frontend)

**Test behavior, not implementation.** Assert on observable outcomes — return values, state the caller can see, calls to collaborators that matter. Do not assert on private fields, internal method call order, or anything a refactor would change without changing behavior. Tests coupled to implementation break constantly and discourage refactoring, which defeats their purpose.

**One logical behavior per test.** A test should have a single reason to fail. Multiple unrelated assertions in one test make failures ambiguous and hide later assertions when an earlier one fails. Multiple assertions describing _one_ outcome are fine.

**Make tests deterministic and isolated (the FIRST idea).** Tests must be Fast, Independent, Repeatable, Self-validating, and Timely. No test may depend on another test's state or on execution order. No real clock, randomness, network, filesystem, or database in a unit test — inject or fake those. A test that passes or fails depending on the day, the machine, or what ran before it is worse than no test.

**Arrange–Act–Assert.** Structure every test in three visually distinct phases: set up the inputs and dependencies, perform the single action under test, then assert the outcome. This makes intent obvious at a glance.

**Name tests so a failure reads like a sentence.** The name should say what's being tested, under what condition, and the expected result. When a test fails in CI, the name alone should tell you what broke without opening the file.

**Cover the paths that matter, not a coverage number.** Always cover: the happy path, boundary/edge values (empty, null, zero, max, off-by-one), and failure paths (invalid input, thrown exceptions, rejected promises). Chasing 100% line coverage produces tests that assert nothing meaningful; aim for meaningful behavior coverage instead.

**Mock only at real boundaries.** Replace external dependencies (HTTP, database, time, third-party services) — not the code you're actually testing. Over-mocking produces tests that pass while the real system is broken. If you find yourself mocking the unit under test, restructure instead.

**Keep tests DRY where it helps readability, WET where it helps clarity.** Extract shared setup into builders/factories/fixtures, but keep the meaningful inputs of each test visible in the test body. A reader should not have to chase helpers to understand why a test passes.

**Tests are production code.** They get reviewed, refactored, and held to the same naming and cleanliness bar. Delete dead tests; don't comment them out.

---

## Backend — .NET

Detect the existing setup first and match it: test framework (xUnit / NUnit / MSTest), mocking library (Moq / NSubstitute), and assertions (FluentAssertions or built-in). The patterns below assume **xUnit + Moq + FluentAssertions**; adapt if the project differs. Do not introduce a new framework into a project that already standardized on one.

**Naming.** Use `Method_Scenario_ExpectedResult`.

```
CalculateDiscount_WhenCartIsEmpty_ReturnsZero
GetUser_WhenIdNotFound_ThrowsNotFoundException
```

**Structure with AAA and FluentAssertions:**

```csharp
[Fact]
public void CalculateTotal_WithMultipleItems_SumsLineTotals()
{
    // Arrange
    var sut = new OrderCalculator();
    var order = new OrderBuilder().WithItem(price: 10m, qty: 2).WithItem(price: 5m, qty: 1).Build();

    // Act
    var total = sut.CalculateTotal(order);

    // Assert
    total.Should().Be(25m);
}
```

**Parameterize input variations** with `[Theory]` + `[InlineData]` / `[MemberData]` instead of copy-pasting near-identical tests:

```csharp
[Theory]
[InlineData(0, 0)]
[InlineData(100, 10)]
[InlineData(250, 25)]
public void Discount_IsTenPercent(decimal subtotal, decimal expected) =>
    new DiscountService().For(subtotal).Should().Be(expected);
```

**Mock collaborators with Moq; verify only interactions that are part of the contract:**

```csharp
var repo = new Mock<IUserRepository>();
repo.Setup(r => r.GetByIdAsync(42)).ReturnsAsync(new User(42));
var sut = new UserService(repo.Object);

var result = await sut.GetDisplayNameAsync(42);

result.Should().Be("Ada");
repo.Verify(r => r.GetByIdAsync(42), Times.Once); // only because "load exactly once" is the contract
```

**.NET specifics to get right:**

- Test `async` methods with `async Task` (never `async void`) and `await` the call. Assert thrown exceptions with `await act.Should().ThrowAsync<T>()`.
- Don't touch a real `DbContext` in a unit test. Test logic against mocked repositories/abstractions; save EF query behavior for integration tests.
- Don't read `DateTime.Now`/`Guid.NewGuid()` directly in code under test — inject an abstraction (e.g. `TimeProvider`) so tests are deterministic.
- Keep one test class per class under test (`OrderCalculatorTests`), mirroring the production namespace.
- Run `dotnet test` and confirm new tests pass — and fail when the behavior is broken — before declaring done.

---

## Frontend — React

Detect the existing setup first and match it: runner (Vitest / Jest) and library (React Testing Library + `@testing-library/user-event`). The patterns below assume **Vitest + React Testing Library**; adapt if the project differs.

**Test from the user's perspective.** Query by accessible role, label, or text — what a user perceives — not by CSS classes, component internals, or `data-testid` (use `testid` only as a last resort). This keeps tests resilient to refactors and doubles as an accessibility check.

```tsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

it("shows an error when submitting an empty email", async () => {
  // Arrange
  render(<SignupForm />);
  const user = userEvent.setup();

  // Act
  await user.click(screen.getByRole("button", { name: /sign up/i }));

  // Assert
  expect(screen.getByText(/email is required/i)).toBeInTheDocument();
});
```

**Interact via `user-event`, not `fireEvent`** — it simulates real user interaction (focus, key events, etc.) and catches more bugs.

**Cover the states, not just the happy render.** For any data-driven component, test loading, empty, error, and success states explicitly.

**Mock the network at the boundary** (e.g. MSW, or mocking the fetch/api module) — never make real requests. Reset mocks between tests so they stay independent.

**Test custom hooks in isolation** with `renderHook` when the logic is non-trivial; otherwise prefer testing the hook through a component that uses it.

**React specifics to get right:**

- Use `findBy*` / `waitFor` for anything async; never assert immediately after an action that updates state asynchronously.
- Wrap interactions that cause state updates so there are no `act(...)` warnings — `user-event`'s async API handles this for you.
- Keep each test's meaningful input (props, mocked responses) visible in the test body.
- Avoid snapshot tests for anything beyond trivial, stable output — large snapshots get blindly updated and assert nothing.
- Run the test command (e.g. `vitest run`) and confirm new tests pass before declaring done.

---

## Anti-patterns to reject (both stacks)

- Tests with no assertion, or that only assert "did not throw" for logic that has a real expected output.
- Asserting on implementation details (private state, internal call order that isn't part of the contract).
- Shared mutable state across tests, or tests that must run in a specific order.
- One giant test exercising many behaviors.
- Mocking the unit under test, or mocking so much that the test no longer exercises real logic.
- Tests written to make a coverage number go up rather than to pin down a behavior.
- Real time, randomness, network, or I/O in a unit test.

When a test would require any of the above to pass, that's usually a signal to restructure the production code (inject the dependency, separate the concern) rather than to write a fragile test.
