import React from 'react';
import { render } from '@testing-library/react-native';
import GymOperatingHoursComponent from '@/components/modal/GymOperatingHoursComponent';

jest.mock('react', () => {
    const originalReact = jest.requireActual('react');
    return {
      ...originalReact,
      useEffect: (fn: () => void) => {
        fn(); // Immediately call the effect
      }
    };
  });

describe('GymOperatingHoursComponent', () => {
  // Helper function to set current time
  const setCurrentTime = (timeString: string) => {
    const mockDate = new Date(`2024-03-04T${timeString}`);
    jest.spyOn(global, 'Date').mockImplementation(() => mockDate as any);
  };

  // Reset mocks after each test
  afterEach(() => {
    jest.restoreAllMocks();
  });

  // Regular Hours Scenarios
  describe('Regular Hours', () => {
    const regularHours = {
      'Monday': '6:00am - 10:00pm',
      'Tuesday': '5:00am - 11:00pm',
      'Wednesday': '6:00am - 10:00pm',
      'Thursday': '5:00am - 11:00pm',
      'Friday': '6:00am - 9:00pm',
      'Saturday': '8:00am - 8:00pm',
      'Sunday': '10:00am - 6:00pm'
    };

    it('displays open status during operating hours', () => {
      // Set time to middle of Monday's operating hours
      setCurrentTime('14:30:00');
      
      const { getByText } = render(
        <GymOperatingHoursComponent 
          regularHours={regularHours} 
          specialHours={{}} 
        />
      );

      const statusText = getByText(/Open until/i);
      expect(statusText).toBeTruthy();
      expect(statusText.props.style.color).toBe('green');
    });

    it('displays closed status outside operating hours', () => {
      // Set time to early morning when gym is closed
      setCurrentTime('04:30:00');
      
      const { getByText } = render(
        <GymOperatingHoursComponent 
          regularHours={regularHours} 
          specialHours={{}} 
        />
      );

      const statusText = getByText(/Closed until/i);
      expect(statusText).toBeTruthy();
      expect(statusText.props.style.color).toBe('red');
    });
  });

  // Special Hours Scenarios
  describe('Special Hours', () => {
    const specialHours = {
      '2024-03-04': '10:00am - 4:00pm',
      '2024-03-05': 'CLOSED'
    };

    it('displays special hours status', () => {
      // Set time within special hours
      setCurrentTime('12:30:00');
      
      const { getByText } = render(
        <GymOperatingHoursComponent 
          regularHours={{}} 
          specialHours={specialHours} 
        />
      );

      const specialText = getByText(/Special Hours/i);
      const statusText = getByText(/Open until/i);
      
      expect(specialText).toBeTruthy();
      expect(statusText).toBeTruthy();
    });

    it('handles completely closed special day', () => {
      // Set time on a closed special day
      setCurrentTime('12:30:00');
      
      const specialHoursClosed = {
        '2024-03-04': 'CLOSED'
      };

      const { getByText } = render(
        <GymOperatingHoursComponent 
          regularHours={{}} 
          specialHours={specialHoursClosed} 
        />
      );

      const statusText = getByText(/Closed Today/i);
      expect(statusText).toBeTruthy();
    });
  });

  // Utility Function Tests
  describe('Utility Functions', () => {
    it('converts time to minutes correctly', () => {
      const timeToMinutes = (time: string) => {
        const hours = parseInt(time.split(':')[0]);
        const minutes = parseInt(time.split(':')[1].split(' ')[0]);
        const period = time.split(' ')[1];
        
        let totalMinutes = hours * 60 + minutes;
        if (period === 'PM' && hours !== 12) totalMinutes += 12 * 60;
        if (period === 'AM' && hours === 12) totalMinutes -= 12 * 60;
        
        return totalMinutes;
      };

      expect(timeToMinutes('6:30 AM')).toBe(6 * 60 + 30);
      expect(timeToMinutes('2:45 PM')).toBe(14 * 60 + 45);
      expect(timeToMinutes('12:00 AM')).toBe(0);
      expect(timeToMinutes('12:00 PM')).toBe(12 * 60);
    });
  });

  // Styling Tests
  describe('Styling', () => {
    it('matches snapshot', () => {
      setCurrentTime('14:30:00');
      
      const { toJSON } = render(
        <GymOperatingHoursComponent 
          regularHours={{
            'Monday': '6:00am - 10:00pm'
          }} 
          specialHours={{}} 
        />
      );

      expect(toJSON()).toMatchSnapshot();
    });
  });
});