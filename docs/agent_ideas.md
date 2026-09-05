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

## 3. Opponent State Memory

Maintain an internal memory of the opponent's observable farm state to estimate their potential future production and its possible impact on the market.

- Track observable opponent plantations and animals across steps.
- Use their current state to estimate potential future production.
- Estimate when and how much of each resource the opponent may produce.
- Use this information to anticipate potential increases in market supply.
- Consider the opponent's estimated production when evaluating future market prices and market risk.