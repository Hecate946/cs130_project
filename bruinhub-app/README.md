
# File Structure

`/app` contains the screens for the app.

`/assets` contains all images used in the app.

`/components` contains all reusable components. components shared across screens are within `/components` directory, while screen-specific components are in subdirectories (e.g. `/components/home`).

`/constants` contains colors and defined categories for the app.

`/hooks` contains pre-defined hooks.

`__tests__` reflects the same directory structure as `/bruinhub-app`. Namely, tests for screens live under `__tests__/app` and tests for components live under `__tests__/components`. Further subdirectories are also reflected. 

# Test Cases

## Screen Test Cases

### HomeScreen Test Cases

1. Renders HomeScreen correctly

Expected Success: The HomeScreen should render with key UI elements like the search bar and sections labeled "Pinned" and "The Rest."
Expected Failure: If any of these elements do not appear, it may indicate issues with component rendering or incorrect initial state setup.

2. Loads pinned items on mount

Expected Success: When AsyncStorage.getAllKeys returns pinned item keys, the "Pinned" section should be visible.
Expected Failure: If no pinned items load, potential issues include incorrect AsyncStorage mocking, improper key handling, or a failure in the component's effect hooks.

3. Filters items based on search query

Expected Success: When entering "Test" in the search bar, only "Test Item" should be displayed, and "Another Item" should be hidden.
Expected Failure: If the filtering does not work, it could indicate issues with how search queries update state, how items are rendered, or incorrect interaction with CategoriesMap.

4. Calls onFinish and clears pins when finishing onboarding

Expected Success: Pressing the button should trigger AsyncStorage.setItem("finishedOnboarding", "false") and call mockOnFinish.
Expected Failure: If either action does not occur, there may be issues with button event handling, incorrect AsyncStorage interaction, or missing function calls in the component logic.

### Onboarding Screen Test Cases

1. Renders OnboardingScreen correctly

Expected Success: The screen should render key UI elements, including the "Welcome" text, category sections, and the "Let's Go" button.
Expected Failure: If elements are missing, it may indicate rendering issues, incorrect props, or missing dependencies.

2. Triggers handleFinish on button press

Expected Success: Pressing "Let's Go" should trigger haptic feedback, set onboarding completion in AsyncStorage, and call mockOnFinish.
Expected Failure: If any function is not called, potential issues include incorrect event handling, missing async handling, or failed mock implementation.

## Component Test Cases

### Divider Component Test Cases

1. Renders Divider component correctly with the provided name

Expected Success: The Divider component should display the provided text (e.g., "Test Divider").
Expected Failure: If the text does not appear, potential issues include incorrect prop handling, missing styles, or component rendering failures.

### HomeCard Component Test Cases

1. Renders HomeCard with provided name and description

Expected Success: The component should correctly display the name and description passed as props.
Expected Failure: If text does not appear, there may be issues with prop handling or rendering.

2. Triggers haptic feedback when card is pressed

Expected Success: Pressing the card should call Haptics.impactAsync with Light feedback.
Expected Failure: If haptic feedback is not triggered, the press event may not be working correctly.

3. Calls pinCallback when pin button is pressed

Expected Success: Pressing the pin icon should invoke pinCallback.
Expected Failure: If pinCallback is not called, event handling for the button may be incorrect.

### SelectableChip Component Test Cases

1. Rendering the SelectableChip Component

Success: The component should correctly render with the provided name displayed.
Failure: If the name is not displayed, it could indicate an issue with prop handling or rendering logic.

2. Toggling Selection and Updating AsyncStorage

Success: Pressing the chip should toggle its selected state, calling AsyncStorage.setItem when selected and AsyncStorage.removeItem when unselected.
Failure: If AsyncStorage methods are not called appropriately, it could mean the state update logic is not functioning correctly.

3. Triggering Haptic Feedback on Press

Success: Pressing the chip should trigger Haptics.impactAsync with Haptics.ImpactFeedbackStyle.Light.
Failure: If haptic feedback does not trigger, it may indicate an issue with the function call or the mocked implementation in tests.


