import React from "react";
import { render, fireEvent, waitFor, act } from "@testing-library/react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import * as Haptics from "expo-haptics";
import NotificationItem from "@/components/notifications/NotificationItem";

jest.mock("@react-native-async-storage/async-storage", () => ({
  getItem: jest.fn(),
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

describe("NotificationItem Component", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("should render NotificationItem with the provided name", () => {
    const { getByText } = render(<NotificationItem name="Test Notification" id="1" />);
    expect(getByText("Test Notification")).toBeTruthy();
  });

  it("should load the initial toggle state from AsyncStorage", async () => {
    (AsyncStorage.getItem as jest.Mock).mockResolvedValue("on");

    const { getByRole } = render(<NotificationItem name="Test Notification" id="1" />);

    await waitFor(() => {
      expect(getByRole("switch").props.value).toBe(true);
    });
  });

  it("should toggle switch and update AsyncStorage", async () => {
    (AsyncStorage.getItem as jest.Mock).mockResolvedValue("off");

    const { getByRole, rerender } = render(<NotificationItem name="Test Notification" id="1" />);
    let switchComponent = getByRole("switch");

    await act(async () => {
      fireEvent(switchComponent, "valueChange", true);
    });

    //Rerendering the component to reflect new state changes and also get the latest switch instance
    rerender(<NotificationItem name="Test Notification" id="1" />);
    switchComponent = getByRole("switch");

    await waitFor(() => {
      expect(AsyncStorage.setItem).toHaveBeenCalledWith("notification_1", "on");
    });
  });

  it("should trigger haptic feedback when toggled", async () => {
    const { getByRole } = render(<NotificationItem name="Test Notification" id="1" />);
    const switchComponent = getByRole("switch");

    fireEvent(switchComponent, "valueChange", true);

    await waitFor(() => {
      expect(Haptics.impactAsync).toHaveBeenCalledWith(Haptics.ImpactFeedbackStyle.Light);
    });
  });
});