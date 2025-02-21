import React from "react";
import { render, fireEvent, waitFor } from "@testing-library/react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import HomeScreen from "@/app/HomeScreen";
import { CategoriesMap } from "@/constants/CategoriesMap";

jest.mock("@react-native-async-storage/async-storage", () => ({
    getAllKeys: jest.fn() as jest.MockedFunction<typeof AsyncStorage.getAllKeys>,
    setItem: jest.fn(),
    removeItem: jest.fn(),
    multiRemove: jest.fn(),
}));

jest.mock("expo-haptics", () => ({
  impactAsync: jest.fn(),
}));

describe("HomeScreen", () => {
  const mockOnFinish = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("should render HomeScreen correctly", async () => {
    const { getByPlaceholderText, queryByText } = render(<HomeScreen onFinish={mockOnFinish} />);

    await waitFor(() => {
        expect(getByPlaceholderText("Search")).toBeTruthy();
        expect(queryByText("Pinned")).toBeTruthy();
        expect(queryByText("The Rest")).toBeTruthy();
      });
  });

  it("loads pinned items on mount", async () => {
    (AsyncStorage.getAllKeys as jest.Mock).mockImplementation(() => Promise.resolve(["pin_1", "pin_2"]));
    const { findByText } = render(<HomeScreen onFinish={mockOnFinish} />);

    await waitFor(() => expect(findByText("Pinned")).toBeTruthy());
  });

  it("filters items based on search query", async () => {
    CategoriesMap.set("Category1", new Map([["1", "Test Item"], ["2", "Another Item"]]));
    const { getByPlaceholderText, queryByText } = render(<HomeScreen onFinish={mockOnFinish} />);

    const searchInput = getByPlaceholderText("Search");
    fireEvent.changeText(searchInput, "Test");

    await waitFor(() => {
      expect(queryByText("Test Item")).toBeTruthy();
      expect(queryByText("Another Item")).toBeNull();
    });
  });

  it("calls onFinish and clears pins when finishing onboarding", async () => {
    const { getByText } = render(<HomeScreen onFinish={mockOnFinish} />);
    fireEvent.press(getByText("Back to onboarding for dev purposes"));

    await waitFor(() => {
      expect(AsyncStorage.setItem).toHaveBeenCalledWith("finishedOnboarding", "false");
      expect(mockOnFinish).toHaveBeenCalled();
    });
  });
});
