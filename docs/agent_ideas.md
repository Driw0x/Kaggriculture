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

**Status:** implemented. Daily tasks are converted into paths and action
stacks, with routing based on worker positions and nearby tasks.

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
- Reuse free worker capacity for nearby lower-priority tasks when this does
  not endanger mandatory work.

**Status:** implemented through daily task generation, ordered action stacks
and capacity-aware routing.

## 5. Dynamic Workforce Management

Choose the number of workers dynamically from the expected workload and
economic value of extra capacity.

- Search for the minimum workforce able to complete the required tasks.
- Account for the real start delay and position of newly hired workers.
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
  demand and, where available, visible public opponent supply.
- Simulate projected sales per unit instead of assuming a single fixed sale
  price.
- Sell harvested products continuously when appropriate instead of waiting
  for one global liquidation.
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
- Keep animal work grouped when that reduces route fragmentation.

**Status:** implemented.

## 12. Observation-Checked Execution

Do not blindly execute a previously generated action stack when the current
observation no longer matches the assumptions used to create it.

- Validate queued worker actions against the current game state.
- Resynchronize production state when the content or production type of a
  tile changes.
- Recalculate relevant sale and inventory information when products are
  deposited during the current turn.
- Keep the planner deterministic while making execution robust to state
  changes between planning and action time.

**Status:** implemented.
