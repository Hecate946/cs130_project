import React from "react";
import { render, fireEvent, waitFor } from "@testing-library/react-native";
import HomeCard from "@/components/home/HomeCard";
import * as Haptics from "expo-haptics";
import MaterialCommunityIcons from "react-native-vector-icons/MaterialCommunityIcons";

jest.mock("expo-haptics", () => ({
  impactAsync: jest.fn(),
  ImpactFeedbackStyle: {
    Light: "Light",
    Medium: "Medium",
    Heavy: "Heavy",
  },
}));

describe("HomeCard Component", () => {
  const mockPinCallback = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("should render HomeCard with provided name and description", async () => {
    const { getByText } = render(
      <HomeCard name="Test Name" description="Test Description" isPinned={false} pinCallback={mockPinCallback} />
    );

    expect(getByText("Test Name")).toBeTruthy();
    expect(getByText("Test Description")).toBeTruthy();
  });

  it("should trigger haptic feedback when card is pressed", async () => {
    const { getByText } = render(
      <HomeCard name="Test Name" description="Test Description" isPinned={false} pinCallback={mockPinCallback} />
    );

    fireEvent.press(getByText("Test Name"));

    await waitFor(() => {
      expect(Haptics.impactAsync).toHaveBeenCalledWith(Haptics.ImpactFeedbackStyle.Light);
    });
  });

  it("should call pinCallback when pin button is pressed", async () => {
    const { getByTestId } = render(
      <HomeCard name="Test Name" description="Test Description" isPinned={false} pinCallback={mockPinCallback} />
    );

    fireEvent.press(getByTestId("pin-button"));

    await waitFor(() => {
      expect(mockPinCallback).toHaveBeenCalled();
    });
  });
});
