import React from "react";
import { render, waitFor } from "@testing-library/react-native";
import NotificationsScreen from "@/app/NotificationsScreen";
import { Categories } from "@/constants/Categories";
import AsyncStorage from "@react-native-async-storage/async-storage";

jest.mock("@react-native-async-storage/async-storage", () => ({
  getAllKeys: jest.fn() as jest.MockedFunction<typeof AsyncStorage.getAllKeys>,
  setItem: jest.fn(),
  removeItem: jest.fn(),
  multiRemove: jest.fn(),
}));

jest.mock("expo-haptics", () => ({
  impactAsync: jest.fn(),
}));

describe("NotificationsScreen", () => {
  const mockOnFinish = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("should render notifs Screen correctly", async () => {
    const { getByText } = render(<NotificationsScreen onFinish={mockOnFinish} />);

    await waitFor(() => {
      expect(getByText("Notifications")).toBeTruthy();
      expect(getByText("Select the facilities you'd like to receive notifications for, including hours updates and holiday reminders.")).toBeTruthy();
    });
  });

  it("should display all categories", async () => {
    const { getByText } = render(<NotificationsScreen onFinish={mockOnFinish} />);

    await waitFor(() => {
      expect(getByText("Restaurants")).toBeTruthy();
      expect(getByText("Takeout")).toBeTruthy();
      expect(getByText("Gyms")).toBeTruthy();
      expect(getByText("Libraries")).toBeTruthy();
      expect(getByText("ResLife Study Rooms")).toBeTruthy();
      expect(getByText("ResLife Spaces")).toBeTruthy();
    });
  });

  it("should render notification items for each category", async () => {
    const { getByText } = render(<NotificationsScreen onFinish={mockOnFinish} />);

    await waitFor(() => {
      Categories.diningHalls.forEach((item) => expect(getByText(item.name)).toBeTruthy());
      Categories.takeout.forEach((item) => expect(getByText(item.name)).toBeTruthy());
      Categories.gym.forEach((item) => expect(getByText(item.name)).toBeTruthy());
      Categories.libraries.forEach((item) => expect(getByText(item.name)).toBeTruthy());
      Categories.reslifeStudy.forEach((item) => expect(getByText(item.name)).toBeTruthy());
      Categories.reslifeSpaces.forEach((item) => expect(getByText(item.name)).toBeTruthy());
    });
  });
});
