import React from 'react';
import { render } from '@testing-library/react-native';
import HistoricalDataComponent from '@/components/modal/HistoricalDataComponent';

describe('HistoricalDataComponent', () => {
  const mockData = {
    '8': { capacity: 100, occupants: 50 },
    '12': { capacity: 200, occupants: 150 },
    '16': { capacity: 150, occupants: 120 },
    '20': { capacity: 180, occupants: 90 },
    '24': { capacity: 0, occupants: 0 },
  };

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('Rendering', () => {
    it('renders correctly with provided data', () => {
      const { getByText } = render(<HistoricalDataComponent data={mockData} />);
      expect(getByText('Historical Capacity')).toBeTruthy();
    });
  });

  describe('Time Labels', () => {
    it('formats time labels correctly', () => {
      const { getByText } = render(<HistoricalDataComponent data={mockData} />);
      expect(getByText('8 AM')).toBeTruthy();
      expect(getByText('12 PM')).toBeTruthy();
      expect(getByText('4 PM')).toBeTruthy();
      expect(getByText('8 PM')).toBeTruthy();
      expect(getByText('12 AM')).toBeTruthy();
    });
  });

  describe('Occupancy Calculations', () => {
    it('calculates occupancy percentages correctly', () => {
      const { getByText } = render(<HistoricalDataComponent data={mockData} />);
      expect(getByText('50%')).toBeTruthy(); 
      expect(getByText('75%')).toBeTruthy(); 
      expect(getByText('80%')).toBeTruthy(); 
      expect(getByText('50%')).toBeTruthy(); 
      expect(getByText('0%')).toBeTruthy();  
    });
  });

  describe('Occupancy Statistics', () => {
    it('displays peak occupancy time correctly', () => {
      const { getByText } = render(<HistoricalDataComponent data={mockData} />);
      expect(getByText('Peak')).toBeTruthy();
      expect(getByText('4 PM')).toBeTruthy();
      expect(getByText('80%')).toBeTruthy();
    });

    it('displays lowest occupancy time correctly', () => {
      const { getByText } = render(<HistoricalDataComponent data={mockData} />);
      expect(getByText('Lowest')).toBeTruthy();
      expect(getByText('12 AM')).toBeTruthy();
      expect(getByText('0%')).toBeTruthy();
    });

    it('calculates average occupancy correctly', () => {
      const { getByText } = render(<HistoricalDataComponent data={mockData} />);
      expect(getByText('Average')).toBeTruthy();
      expect(getByText('51%')).toBeTruthy(); 
    });
  });

  describe('Styling', () => {
    it('matches snapshot', () => {
      const { toJSON } = render(<HistoricalDataComponent data={mockData} />);
      expect(toJSON()).toMatchSnapshot();
    });
  });
});
