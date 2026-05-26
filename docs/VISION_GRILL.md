# Vision Grill

This doc is the interview surface for landing the full vision. It should be updated as answers become decisions.

## Current Product Thesis

Grocery Flywheel is not a grocery list or a food planner. It is a private, approval-first life-ops loop that turns purchase history and tiny depletion pulses into better future household replenishment decisions.

Decision: start as a grocery module, but define grocery as the full grocery-store and household replenishment surface, not food only. Extract meta-patterns throughout the drill. The product should stay compatible with many grocery types, cleaning supplies, household consumables, in-person shopping, and first-run users without digital purchase history.

## Open Questions

### 1. Product Boundary

Should Grocery Flywheel stay focused on groceries, or become the grocery module inside a broader Life Ops / Personal AI Infrastructure system?

Recommended answer: start as a grocery product with architecture that can later become a Life Ops module. Groceries are concrete enough to ship, but the primitives should be reusable: runway, pulses, preference signals, friction budget, and approval-first actions.

User answer: start as a grocery module, but deliberately extract reusable meta-patterns and adjacent use cases, including restaurant inventory and restocking.

Additional user correction: this is not just food. It includes everything sold at grocery stores and everything a household needs, including cleaning supplies.

Status: resolved for now. Grocery-store and household replenishment is the first module; the larger abstraction is the replenishment flywheel.

### 2. First Expansion Persona

After the original personal grocery workflow, which expansion persona should shape the next layer of product decisions?

Recommended answer: choose "small operator with recurring restocking pain" as the first expansion persona, especially restaurants/cafes or office kitchens. This is close enough to groceries to reuse the same mechanics, but different enough to force the product to handle multi-person inventory, in-person buying, and restock thresholds.

User answer: small operator restocking is good.

Status: resolved. First expansion persona is small operator restocking.

### 3. Primary Output

Is the product's main output a dashboard, a next-cart draft, or an always-on assistant check-in loop?

Recommended answer: the assistant loop is the product, the dashboard is the proof surface, and the next-cart draft is the high-ROI action.

### 4. Data Source Strategy

Should the MVP use manual entry, receipt imports, browser-assisted grocery history, or direct integrations?

Recommended answer: start with manual JSON plus receipt/browser import scripts. Direct grocery integrations can come later because account automation and checkout boundaries are sensitive.

### 5. Automation Boundary

What should the system be allowed to do without asking?

Recommended answer: it can read local state, analyze, render dashboards, create draft recommendations, and ask check-in questions. It cannot place purchases, submit carts, or mutate external accounts without explicit approval.

### 6. User Model

Should this optimize for one known user's behavior, or become configurable for many people?

Recommended answer: begin opinionated around the original user because the workflow is sharpest there, then generalize the terms and schema without sanding off the neurodivergent-friendly behavior.

### 7. Business Shape

Is this a private personal tool, a sellable consumer app, a consulting workflow, or infrastructure for personal AI agents?

Recommended answer: first private tool, then consulting/productized workflow, then agent infrastructure. The private tool proves the ROI loop.

## Decisions To Capture

- Product boundary.
- First expansion persona.
- Automation boundary.
- First data source.
- Whether private source snapshots stay in repo long-term.
- Whether the dashboard is static HTML, local app, or hosted app.
