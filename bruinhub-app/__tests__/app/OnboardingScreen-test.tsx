import React from "react";
import { render, fireEvent, waitFor } from "@testing-library/react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import OnboardingScreen from "@/app/OnboardingScreen";
import * as Haptics from "expo-haptics";

jest.mock("@react-native-async-storage/async-storage", () => ({
  setItem: jest.fn(),
}));

jest.mock("expo-haptics", () => ({
    impactAsync: jest.fn(),
    ImpactFeedbackStyle: {
      Light: "Light",
      Medium: "Medium",
      Heavy: "Heavy",
    },
}));

describe("OnboardingScreen", () => {
  const mockOnFinish = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("should render OnboardingScreen correctly", async () => {
    const { getByText } = render(<OnboardingScreen onFinish={mockOnFinish} />);

    await waitFor(() => {
      expect(getByText("Welcome")).toBeTruthy();
      expect(getByText("Choose your favorite spots to pin!")).toBeTruthy();
      expect(getByText("Restaurants")).toBeTruthy();
      expect(getByText("Let's Go")).toBeTruthy();
    });
  });

  it("should trigger handleFinish on button press", async () => {
    const { getByText } = render(<OnboardingScreen onFinish={mockOnFinish} />);
    fireEvent.press(getByText("Let's Go"));

    await waitFor(() => {
      expect(Haptics.impactAsync).toHaveBeenCalledWith(Haptics.ImpactFeedbackStyle.Heavy);
      expect(AsyncStorage.setItem).toHaveBeenCalledWith("finishedOnboarding", "true");
      expect(mockOnFinish).toHaveBeenCalled();
    });
  });
});
