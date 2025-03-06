import React from 'react';
import { render } from '@testing-library/react-native';
import GymZonesComponent from '@/components/modal/GymZonesComponent';
import CapacityComponent from '@/components/modal/CapacityComponent';
import { Colors } from '@/constants/Colors';

// Mock the CapacityComponent at the top of the file
jest.mock('@/components/modal/CapacityComponent', () => {
  return jest.fn(() => null);
});

describe('GymZonesComponent', () => {
  // Sample zones data for testing
  const mockZones = {
    'Weight Room': {
      capacity: 50,
      last_updated: '2024-03-04T14:00:00',
      percentage: 60
    },
    'Cardio Area': {
      capacity: 30,
      last_updated: '2024-03-04T14:00:00',
      percentage: 40
    },
    'Group Fitness Room': {
      capacity: 20,
      last_updated: '2024-03-04T14:00:00',
      percentage: 20
    }
  };

  describe('Rendering', () => {
    it('renders all zones correctly', () => {
      const { getByText } = render(<GymZonesComponent zones={mockZones} />);

      // Check that all zone names are rendered
      expect(getByText('Weight Room')).toBeTruthy();
      expect(getByText('Cardio Area')).toBeTruthy();
      expect(getByText('Group Fitness Room')).toBeTruthy();
    });

    it('renders correct number of zones', () => {
      const { getAllByText } = render(<GymZonesComponent zones={mockZones} />);

      // Verify the number of zones rendered
      const zoneNames = getAllByText(/Room|Area/i);
      expect(zoneNames).toHaveLength(3);
    });
  });

  describe('Capacity Component Integration', () => {
    it('passes correct percentage to CapacityComponent', () => {
      // Clear any previous calls to the mock
      (CapacityComponent as jest.Mock).mockClear();

      render(<GymZonesComponent zones={mockZones} />);

      // Verify percentages are converted correctly
      expect(CapacityComponent).toHaveBeenCalledWith(
        expect.objectContaining({ percentage: 0.6 }),
        {}
      );
      expect(CapacityComponent).toHaveBeenCalledWith(
        expect.objectContaining({ percentage: 0.4 }),
        {}
      );
      expect(CapacityComponent).toHaveBeenCalledWith(
        expect.objectContaining({ percentage: 0.2 }),
        {}
      );
    });
  });

  describe('Edge Cases', () => {
    it('handles empty zones object', () => {
      const { queryByText } = render(<GymZonesComponent zones={{}} />);

      // No zones should be rendered
      expect(queryByText(/Room|Area/i)).toBeNull();
    });

    it('handles zones with zero percentage', () => {
      const zonesWithZeroPercentage = {
        'Empty Room': {
          capacity: 10,
          last_updated: '2024-03-04T14:00:00',
          percentage: 0
        }
      };

      const { getByText } = render(<GymZonesComponent zones={zonesWithZeroPercentage} />);

      // Verify zone name is still rendered
      expect(getByText('Empty Room')).toBeTruthy();
    });
  });
});