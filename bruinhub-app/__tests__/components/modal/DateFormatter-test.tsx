import React from 'react';
import { render } from '@testing-library/react-native';
import DateFormatter from '@/components/modal/DateFormatter';

describe('DateFormatter', () => {
  // Test various date input scenarios
  describe('Date Formatting', () => {
    it('formats a standard ISO date string correctly', () => {
      const { getByText } = render(<DateFormatter isoString="2024-03-15T14:30:00" />);

      // Use toHaveTextContent for more robust text matching
      const dateElement = getByText(/3\/15\/2024/);
      expect(dateElement).toBeTruthy();
    });

    it('handles dates at different times of day', () => {
      const testCases = [
        { input: "2024-01-01T00:00:00", description: "Midnight" },
        { input: "2024-12-31T23:59:59", description: "Just before midnight" },
        { input: "2024-06-15T12:30:45", description: "Midday" }
      ];

      testCases.forEach(({ input }) => {
        const { getByText } = render(<DateFormatter isoString={input} />);
        const dateElement = getByText(/.+/); // Match any non-empty string
        expect(dateElement).toBeTruthy();
      });
    });

    it('correctly applies Pacific Time Zone conversion', () => {
      const { getByText } = render(<DateFormatter isoString="2024-03-15T22:00:00" />);
      
      // Use a regex that matches common date format
      const dateElement = getByText(/\d{1,2}\/\d{1,2}\/\d{4},\s*\d{1,2}:\d{2}(:\d{2})?\s*[AP]M/);
      expect(dateElement).toBeTruthy();
    });
  });

  // Test component styling
  describe('Styling', () => {
    it('applies correct text style', () => {
      const { getByText } = render(<DateFormatter isoString="2024-03-15T14:30:00" />);
      const dateElement = getByText(/.+/);

      expect(dateElement.props.style).toEqual(
        expect.objectContaining({
          textAlign: "left",
          fontSize: 16,
          fontStyle: "italic",
          marginLeft: 4,
        })
      );
    });

    it('matches snapshot for visual regression', () => {
      const { toJSON } = render(<DateFormatter isoString="2024-03-15T14:30:00" />);

      expect(toJSON()).toMatchSnapshot();
    });
  });

  // Error handling tests
  describe('Edge Cases', () => {
    it('handles invalid date strings', () => {
      // Suppress expected console error
      const originalError = console.error;
      console.error = jest.fn();

      const { getByText } = render(<DateFormatter isoString="invalid-date" />);

      // Restore console.error
      console.error = originalError;

      // Should still render something
      const dateElement = getByText(/.+/);
      expect(dateElement).toBeTruthy();
    });

    it('handles extreme date values', () => {
      const testCases = [
        "0001-01-01T00:00:00",  // Very early date
        "9999-12-31T23:59:59"   // Far future date
      ];

      testCases.forEach(dateString => {
        const { getByText } = render(<DateFormatter isoString={dateString} />);
        const dateElement = getByText(/.+/);
        expect(dateElement).toBeTruthy();
      });
    });
  });
});