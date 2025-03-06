import React from 'react';
import { render } from '@testing-library/react-native';
import HourComponent from '@/components/modal/HourComponent';

describe('HourComponent', () => {
  // Sample test data
  const mockSchedule = [
    {
      day: 'Monday',
      hours: ['9:00 AM - 5:00 PM', '6:00 PM - 8:00 PM']
    },
    {
      day: 'Tuesday',
      hours: ['10:00 AM - 6:00 PM']
    },
    {
      day: 'Wednesday',
      hours: []
    }
  ];

  describe('Rendering', () => {
    it('renders all days in the schedule', () => {
      const { getByText } = render(<HourComponent schedule={mockSchedule} />);

      expect(getByText('Monday')).toBeTruthy();
      expect(getByText('Tuesday')).toBeTruthy();
      expect(getByText('Wednesday')).toBeTruthy();
    });

    it('renders multiple hours for a day', () => {
      const { getByText } = render(<HourComponent schedule={mockSchedule} />);

      expect(getByText('9:00 AM - 5:00 PM')).toBeTruthy();
      expect(getByText('6:00 PM - 8:00 PM')).toBeTruthy();
    });

    it('renders "Closed" for days with no hours', () => {
      const { getByText } = render(<HourComponent schedule={mockSchedule} />);

      const closedText = getByText('Closed');
      expect(closedText).toBeTruthy();
    });
  });

  describe('Conditional Rendering', () => {
    it('handles empty schedule', () => {
      const { queryByText } = render(<HourComponent schedule={[]} />);

      expect(queryByText('Monday')).toBeNull();
      expect(queryByText('Closed')).toBeNull();
    });
  });

  describe('Edge Cases', () => {
    it('handles schedule with single day', () => {
      const singleDaySchedule = [
        {
          day: 'Friday',
          hours: ['9:00 AM - 9:00 PM']
        }
      ];

      const { getByText } = render(<HourComponent schedule={singleDaySchedule} />);

      expect(getByText('Friday')).toBeTruthy();
      expect(getByText('9:00 AM - 9:00 PM')).toBeTruthy();
    });

    it('handles very long hour strings', () => {
      const longHourSchedule = [
        {
          day: 'Saturday',
          hours: ['Extended Hours: 7:00 AM - 10:00 PM with special late night extension']
        }
      ];

      const { getByText } = render(<HourComponent schedule={longHourSchedule} />);

      expect(getByText(/Extended Hours: 7:00 AM - 10:00 PM/)).toBeTruthy();
    });
  });

  describe('Snapshot Testing', () => {
    it('matches snapshot', () => {
      const { toJSON } = render(<HourComponent schedule={mockSchedule} />);

      expect(toJSON()).toMatchSnapshot();
    });
  });
});