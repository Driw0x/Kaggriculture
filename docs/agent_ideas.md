# Agent Ideas

## 1. State Memory

Maintain an internal memory of persistent farm states so the agent can
track plantations and animals across steps instead of reasoning only
from the current action.

-   **Plantations:** keep a list of planted plots with their position
    and relevant state, such as crop type, planting time, growth state,
    or expected harvest state.
-   **Animals:** keep a list of animals with their position and relevant
    state so their evolution and required actions can be tracked over
    time.
-   Update the stored state as the game progresses and remove or reset
    entries when a plantation or animal no longer corresponds to the
    stored state.

**Status:** implemented. The retained planner refreshes crop and animal
state from observations and synchronizes the stored production state when
a tile changes production type.

## 2. General Path Management

Manage movement as a path rather than choosing each movement
independently. The agent should determine where it needs to go and
follow an appropriate route toward that target.

-   Use path management for all spatial actions, including moving
    between plantations, animals, market locations, or other relevant
    positions.
-   For planting, define an efficient path through the plots that need
    to be planted instead of selecting plots independently.
-   The same general path logic can be reused for other sequences of
    spatial actions to reduce unnecessary movement.

**Status:** implemented. Spatial tasks are now embedded in timed worker
schedules. Travel time between tasks is included directly in the schedule,
and shed detours are chosen from the four access tiles according to the
complete trip rather than as isolated movements.

## 3. Opponent State Memory

Maintain an internal memory of the opponent's observable farm state to estimate their potential future production and its possible impact on the market.

- Track observable opponent plantations and animals across steps.
- Use their current state to estimate potential future production.
- Estimate when and how much of each resource the opponent may produce.
- Use this information to anticipate potential increases in market supply.
- Consider the opponent's estimated production when evaluating future market prices and market risk.

**Status:** partially implemented. CHI10 can include visible/public opponent
supply projections in market estimates, but persistent opponent state memory
across steps is not part of the retained baseline.

## 4. Priority-Based Task Planning

Build the daily plan from explicit task priorities instead of treating all
actions as equally important.

- Prioritize mandatory maintenance such as crop survival, harvest/replant
  cycles and animal feeding/care.
- Schedule optional expansion or weed-clearing work only when enough worker
  capacity remains.
- Preserve dependencies between tasks so actions happen in a valid order.
- Give survival watering an explicit predecessor relationship before the
  corresponding crop chain.
- Prioritize Wheat delivery when another worker depends on it for feeding.
- Reuse free worker capacity for profitable lower-priority tasks when this
  does not endanger mandatory work.

**Status:** implemented through temporal task generation, explicit
predecessors, required/optional task flags and bounded assignment search.

## 5. Dynamic Workforce Management

Choose the number of workers dynamically from the expected workload and
economic value of extra capacity.

- Search for the minimum workforce able to complete the required tasks.
- Account for the real start tick and spawn position of newly hired workers.
- Check whether mandatory actions can still fit before the daily temporal
  deadline with the currently available workers.
- Compare the expected value created by an additional worker with the next
  Fibonacci hiring cost.
- Stop hiring when the expected additional profit no longer justifies the
  next worker.
- Do not impose an artificial maximum of ten farm hands.

**Status:** implemented.

## 6. Conditional Watering and Production Timing

Avoid spending actions on crops when watering or continued production no
longer creates useful value.

- Water only when required for crop survival or when watering is needed
  before a useful harvest.
- Track crop timing so harvest and replant decisions respect the production
  cycle.
- Avoid planting or replanting crops that cannot produce before the final
  useful sale.
- Apply the same endgame feasibility principle to new animals.
- Stop maintaining production once no additional profitable harvest can be
  completed in time.

**Status:** implemented.

## 7. Dynamic Production Selection

Choose new production according to expected profitability rather than a
fixed post-opening layout.

- Evaluate crops and animals for empty or soon-to-be-empty tiles.
- Include purchase cost, feed cost, labor cost, occupation time and space
  usage in the evaluation.
- Estimate marginal revenue using the expected market state.
- Keep only positive and affordable production choices.
- Convert the selected production plan into the required seed, animal and
  Wheat market orders.

**Status:** implemented.

## 8. Profit-Aware Land Expansion

Treat land purchase as an investment that must be justified by the
production that can still be installed on it.

- Estimate the production value available on the new quadrant.
- Include seed, animal, feed and extra hiring costs.
- Check affordability before buying land.
- Avoid late expansion when there is not enough remaining time to recover
  the investment.
- Prefer useful production space instead of expanding automatically.

**Status:** implemented.

## 9. Market-Aware Valuation and Sales

Use expected market evolution when deciding what to produce and when to
sell.

- Estimate future prices from current inventory, expected own supply, shop
  demand and visible public opponent supply.
- Simulate projected sales per unit instead of assuming a single fixed sale
  price.
- Evaluate opponent uncertainty with alternative supply/timing scenarios
  instead of assuming a single exact future opponent sale pattern.
- Sell harvested products continuously when appropriate instead of waiting
  for one global liquidation.
- Sell more aggressively when cash is needed or shed pressure becomes high,
  while retaining a Wheat reserve for active animals.
- Meter sales of price-sensitive products to avoid unnecessary price impact.
- Keep fertilizer independently sellable.
- Liquidate remaining sellable inventory near the end of day 29.

**Status:** implemented across the retained CHI9/CHI10 planner family.

## 10. Shed and Inventory Logistics

Treat the shed as a constrained logistics point instead of only a passive
storage location.

- Route workers toward the nearest valid shed-access tile when returning
  products or collecting resources.
- Use all four valid shed-access tiles when selecting return paths.
- Account for products carried by workers and products deposited during the
  current turn.
- Protect against shed overflow when planning harvests and sales.
- Coordinate Wheat harvest, shed drop and later pickup when animal feeding
  depends on Wheat produced during the same day.
- Represent shared resources with an availability tick so a worker can wait
  for a resource that another worker will deposit later.
- Allow a worker already carrying Wheat to create an explicit delivery task
  for another worker.

**Status:** implemented.

## 11. Animal Production Management

Manage animals according to their production state, feed dependency and
remaining useful capacity.

- Harvest available animal products and collect fertilizer before starting
  the next feed/care cycle when appropriate.
- Ensure feed-dependent work is delayed until enough Wheat is available.
- Avoid unnecessary CARE actions when the pending bonus and held production
  already approach the animal's useful capacity.
- Include CARE effects when estimating animal production value.
- Stop animal maintenance when no useful future sale remains or when the
  estimated remaining animal profit becomes non-positive.
- Keep animal work grouped when that reduces route fragmentation.

**Status:** implemented.

## 12. Observation-Checked Execution

Do not blindly execute a previously generated action stack when the current
observation no longer matches the assumptions used to create it.

- Validate scheduled worker actions against the current game state.
- Check shared seed stock, shed stock, worker pickups, tile mutations and
  shed capacity in engine execution order before returning the actions.
- Resynchronize production state when the content or production type of a
  tile changes.
- Recalculate relevant sale and inventory information when products are
  deposited during the current turn.
- Replace invalid scheduled actions with `PASS` instead of blindly executing
  a stale action.

**Status:** implemented in `chi10_temporal.py`.

## 13. Bounded Temporal Scheduling

Schedule work with explicit time instead of assigning only an ordered list of
tasks to each worker.

- Represent each task with its position, action sequence, expected value,
  required/optional status and predecessor dependencies.
- Represent each worker with a current position, current time, inventory and
  timed action sequence.
- Include movement time, pickup time, resource waiting time and action time in
  feasibility checks.
- Reserve shared stock according to the tick at which each quantity becomes
  available.
- Enforce the real end-of-day deadline, including the shorter final-day
  deadline required to sell deposited goods before the episode ends.
- Use a small bounded beam search to keep several alternative worker/task
  assignments without making exhaustive scheduling prohibitively expensive.
- Allow optional tasks to be skipped when doing so permits a better or more
  feasible continuation of the schedule.

**Status:** implemented.

## 14. Tick-by-Tick Worker Replanning

Do not keep executing one fixed worker route for the whole day when the game
state may have changed.

- Rebuild the live temporal task set from the current observation at every
  agent call.
- Recompute worker assignments using actual worker positions, inventories,
  observed shed stock and current tile states.
- Replan around resources that have become available, tasks that were already
  completed or actions that are no longer valid.
- Keep the higher-level daily production, hiring, land and market planning,
  while continuously replanning the worker execution layer.
- Record the new timed schedule only for the current observation and validate
  the action due on the current tick before execution.

**Status:** implemented in `chi10_temporal.py`.

## 15. Public Shop-Order Production Prior

Use the order of publicly unlocked shops as a small demand signal when several
production candidates already have similar economic scores.

- Map each crop or animal to the market product it produces.
- Compare that product with the demand of the first and second unlocked shops.
- Apply only a small multiplier so the underlying marginal-profit model remains
  the main decision criterion.
- Use only information already present in the public observation.

**Status:** implemented in `chi11.py`. The first unlocked shop applies an 8%
production-score multiplier and the second a 3% multiplier when the candidate
output matches the corresponding shop demand.

## 16. Public Farm-Similarity and Clone-Aware Sales

Use repeated similarity between the two publicly visible farms as a weak signal
that simultaneous actions may create avoidable market collision.

- Build a compact public signature from crop counts, animal counts, unlocked
  quadrants and farm-hand count.
- Require similarity to persist over many consecutive turns before activating
  any special behavior.
- Do not use opponent identity, hidden inventories, episode identifiers,
  replay lookup or future actions.
- When the condition is active, reduce ordinary sale batch size rather than
  replacing the base sale policy.
- Never restrict final liquidation.

**Status:** implemented in `chi11.py`. Detection starts at step 48, requires a
signature distance of at most 2 for 24 consecutive turns, and can activate
from step 160. Ordinary SELL quantities are capped at 10 units while active.

## 17. Market-Impact-Aware SELL Ordering

When several SELL orders already exist in the same market action, prioritize
the ones that are most exposed to their own price impact.

- Estimate the post-sale price using the current public market inventory and
  the existing per-unit price model.
- Rank existing SELL slots by estimated immediate value loss.
- Reorder only SELL orders.
- Preserve all non-SELL market slots and do not create new sales.

**Status:** implemented in `chi11.py`.

## 18. Standalone Submission Packaging

Keep the competition agent directly submittable as one Python file when a
development version would otherwise depend on another local agent module.

- Embed the retained base agent implementation directly in the submission file.
- Remove project-local imports from the final competition file.
- Keep the public `agent(obs)` entry point unchanged.
- Preserve the base agent behavior and apply the experimental overlay around a
  single base-agent call.

**Status:** implemented for CHI 11. `chi11.py` contains the CHI 10 base planner
and the CHI 11 overlay in one self-contained file.

## 19. Public Route Baseline

Keep a strong public fixed-route agent as a separate experimental baseline
instead of mixing its action tape directly into the CHI planner.

- Store the public route in readable Python form so every day, hour and action
  can be inspected and modified.
- Preserve the original action sequence exactly in the first baseline.
- Keep route-based experiments separate from the CHI planner family so
  improvements can be attributed clearly.
- Use the public route as a competitive reference and improve robustness around
  it before changing its macro strategy.

**Status:** implemented in `jet.py`. The original compressed v27 route was
expanded mechanically into 719 readable actions without changing their
contents.

## 20. Staged Runtime Fallbacks

Do not discard a complete route tick when one optional runtime correction
raises an exception.

- Preserve the base route action before applying runtime overlays.
- Isolate WEED repair, final liquidation and SELL ordering in separate guarded
  stages.
- If one overlay fails, keep the last valid action instead of returning an
  all-`PASS` turn.
- Reserve the complete `PASS` fallback for the case where no usable route action
  can be recovered.

**Status:** implemented in `jet1.py`.

## 21. Observation-Based Final Liquidation

Replace the fixed final sale quantities of a route tape with liquidation based
on the inventory that is actually sellable at the last actionable step.

- Detect the last actionable step from `episodeSteps`.
- Read the real shed contents instead of trusting the prerecorded final
  quantities.
- Include products deposited by same-tick `DROP` actions before building final
  SELL orders.
- Respect the configured market-order limit.
- Leave the route unchanged on every earlier step.

**Status:** implemented in `jet1.py`.
