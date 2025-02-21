import React from "react";
import { render } from "@testing-library/react-native";
import Divider from "@/components/Divider";

describe("Divider Component", () => {
  it("should render the Divider component correctly with the provided name", async () => {
    const { getByText } = render(<Divider name="Test Divider" />);

    expect(getByText("Test Divider")).toBeTruthy();
  });
});
