import React from 'react';
import { render } from '@testing-library/react-native';
import OperatingHoursComponent from '@/components/modal/OperatingHoursComponent';

// Mock Date to control time in tests
const mockDate = (hours: number, minutes: number, period: 'am' | 'pm') => {
  const mockNow = new Date(2024, 2, 4, 
    period === 'pm' && hours !== 12 ? hours + 12 : 
    period === 'am' && hours === 12 ? 0 : 
    hours
  );
  mockNow.toLocaleTimeString = () => `${hours}:${minutes.toString().padStart(2, '0')}${period}`;
  
  jest.spyOn(global, 'Date').mockImplementation(() => mockNow as any);
};

describe('OperatingHoursComponent', () => {
  // Reset mocks after each test
  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('Open Status Scenarios', () => {
    it('displays "Open until" message when currently open', () => {
      // Mock current time within operating hours
      mockDate(2, 30, 'pm');

      const hoursToday = ['9:00am - 5:00pm', '6:00pm - 9:00pm'];
      const { getByText } = render(<OperatingHoursComponent hoursToday={hoursToday} />);
      
      const statusText = getByText(/Open until 5:00pm/);
      expect(statusText).toBeTruthy();
      expect(statusText.props.style.color).toBe('green');
    });

    it('displays "Open until Midnight" for late hours', () => {
      // Mock current time within last operating period
      mockDate(11, 30, 'pm');

      const hoursToday = ['9:00am - 5:00pm', '6:00pm - 12:00am'];
      const { getByText } = render(<OperatingHoursComponent hoursToday={hoursToday} />);
      
      const statusText = getByText('Open until Midnight');
      expect(statusText).toBeTruthy();
      expect(statusText.props.style.color).toBe('green');
    });

    it('displays "Closed" when no hours are available', () => {
      // Mock time outside of any operating hours
      mockDate(6, 0, 'am');

      const hoursToday = ['Closed all day'];
      const { getByText } = render(<OperatingHoursComponent hoursToday={hoursToday} />);
      
      const statusText = getByText('Closed');
      expect(statusText).toBeTruthy();
      expect(statusText.props.style.color).toBe('red');
    });
  });

  describe('Closed Status Scenarios', () => {
    it('shows next open time when currently closed', () => {
      // Mock time before first operating period
      mockDate(6, 0, 'am');

      const hoursToday = ['9:00am - 5:00pm', '6:00pm - 9:00pm'];
      const { getByText } = render(<OperatingHoursComponent hoursToday={hoursToday} />);
      
      const statusText = getByText('Closed until 9:00am');
      expect(statusText).toBeTruthy();
      expect(statusText.props.style.color).toBe('red');
    });

    it('handles multiple time ranges correctly', () => {
      // Mock time between operating periods
      mockDate(5, 30, 'pm');

      const hoursToday = ['9:00am - 5:00pm', '6:00pm - 9:00pm'];
      const { getByText } = render(<OperatingHoursComponent hoursToday={hoursToday} />);
      
      const statusText = getByText('Closed until 6:00pm');
      expect(statusText).toBeTruthy();
      expect(statusText.props.style.color).toBe('red');
    });
  });

  describe('Edge Cases', () => {
    it('handles 12-hour time format edge cases', () => {
      // Test midnight and noon transitions
      mockDate(12, 0, 'am');
      const midnightHours = ['9:00am - 5:00pm', '6:00pm - 12:00am'];
      const { getByText: byTextMidnight } = render(<OperatingHoursComponent hoursToday={midnightHours} />);
      
      mockDate(12, 0, 'pm');
      const noonHours = ['9:00am - 12:00pm', '1:00pm - 9:00pm'];
      const { getByText: byTextNoon } = render(<OperatingHoursComponent hoursToday={noonHours} />);
      
      expect(byTextMidnight('Closed until 9:00am')).toBeTruthy();
      expect(byTextNoon('Closed until 1:00pm')).toBeTruthy();
    });

    it('handles single time range', () => {
      mockDate(10, 0, 'am');

      const hoursToday = ['9:00am - 5:00pm'];
      const { getByText } = render(<OperatingHoursComponent hoursToday={hoursToday} />);
      
      const statusText = getByText(/Open until 5:00pm/);
      expect(statusText).toBeTruthy();
    });
  });

  describe('Styling', () => {
    it('uses bold red text when closed', () => {
      mockDate(6, 0, 'am');

      const hoursToday = ['9:00am - 5:00pm'];
      const { getByText } = render(<OperatingHoursComponent hoursToday={hoursToday} />);
      
      const statusText = getByText('Closed until 9:00am');
      expect(statusText.props.style).toEqual(expect.objectContaining({
        color: 'red',
        fontWeight: 'bold',
        fontSize: 18,
      }));
    });
  });

  describe('Snapshot Testing', () => {
    it('matches snapshot for open status', () => {
      mockDate(2, 30, 'pm');

      const hoursToday = ['9:00am - 5:00pm', '6:00pm - 9:00pm'];
      const { toJSON } = render(<OperatingHoursComponent hoursToday={hoursToday} />);
      
      expect(toJSON()).toMatchSnapshot();
    });

    it('matches snapshot for closed status', () => {
      mockDate(6, 0, 'am');

      const hoursToday = ['9:00am - 5:00pm', '6:00pm - 9:00pm'];
      const { toJSON } = render(<OperatingHoursComponent hoursToday={hoursToday} />);
      
      expect(toJSON()).toMatchSnapshot();
    });
  });
});