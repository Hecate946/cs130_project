import React from 'react';
import { render } from '@testing-library/react-native';
import CapacityComponent from '@/components/modal/CapacityComponent';

describe('CapacityComponent', () => {
  describe('Rendering', () => {
    it('renders correctly with 0% occupancy', () => {
      const { getByText, getByTestId } = render(<CapacityComponent percentage={0} />);

      // Check text rendering
      const textElement = getByText('Current Occupancy: 0%');
      expect(textElement).toBeTruthy();
    });

    it('renders correctly with 50% occupancy', () => {
      const { getByText, getByTestId } = render(<CapacityComponent percentage={0.5} />);

      // Check text rendering
      const textElement = getByText('Current Occupancy: 50%');
      expect(textElement).toBeTruthy();
    });

    it('renders correctly with 100% occupancy', () => {
      const { getByText } = render(<CapacityComponent percentage={1} />);

      // Check text rendering
      const textElement = getByText('Current Occupancy: 100%');
      expect(textElement).toBeTruthy();
    });
  });

  // Test progress bar properties
  describe('ProgressBar Properties', () => {
    it('sets correct progress bar value', () => {
      const testPercentage = 0.75;
      const { getByTestId } = render(<CapacityComponent percentage={testPercentage} />);
    });

    it('uses correct color from Colors constant', () => {
      const { toJSON } = render(<CapacityComponent percentage={0.5} />);
      const renderResult = toJSON();

      // Check if the color matches the expected color from Colors constant
      expect(renderResult).toMatchSnapshot();
    });
  });

  // Test rounding behavior
  describe('Percentage Rounding', () => {
    it('correctly rounds percentage', () => {
      const { getByText } = render(<CapacityComponent percentage={0.4567} />);

      const textElement = getByText('Current Occupancy: 46%');
      expect(textElement).toBeTruthy();
    });

    it('handles decimal percentages correctly', () => {
      const { getByText } = render(<CapacityComponent percentage={0.9999} />);

      const textElement = getByText('Current Occupancy: 100%');
      expect(textElement).toBeTruthy();
    });
  });

  // Test component styles
  describe('Styling', () => {
    it('matches snapshot for visual regression testing', () => {
      const { toJSON } = render(<CapacityComponent percentage={0.5} />);

      expect(toJSON()).toMatchSnapshot();
    });
  });
});
