import React from "react";
import { render, fireEvent, waitFor, act } from "@testing-library/react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import * as Haptics from "expo-haptics";
import SelectableChip from "@/components/onboarding/SelectableChip";

jest.mock("@react-native-async-storage/async-storage", () => ({
  setItem: jest.fn(),
  removeItem: jest.fn(),
}));

jest.mock("expo-haptics", () => ({
  impactAsync: jest.fn(),
  ImpactFeedbackStyle: {
    Light: "Light",
    Medium: "Medium",
    Heavy: "Heavy",
  },
}));

describe("SelectableChip Component", () => {
  it("should render SelectableChip with provided name", () => {
    const { getByText } = render(<SelectableChip name="Test Chip" id="1" />);
    expect(getByText("Test Chip")).toBeTruthy();
  });

  it("should toggle selection and update AsyncStorage on press", async () => {
    const { getByText } = render(<SelectableChip name="Test Chip" id="1" />);
    const chip = getByText("Test Chip");

    await act(async () => {
      fireEvent.press(chip);
    });

    await waitFor(() => {
      expect(AsyncStorage.setItem).toHaveBeenCalledWith("pin_1", "true");
    });

    await act(async () => {
      fireEvent.press(chip);
    });

    await waitFor(() => {
      expect(AsyncStorage.removeItem).toHaveBeenCalledWith("pin_1");
    });
  });

  it("should trigger haptic feedback on press", async () => {
    const { getByText } = render(<SelectableChip name="Test Chip" id="1" />);
    const chip = getByText("Test Chip");

    fireEvent.press(chip);
    await waitFor(() => {
      expect(Haptics.impactAsync).toHaveBeenCalledWith(Haptics.ImpactFeedbackStyle.Light);
    });
  });
});
