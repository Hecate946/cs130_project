import React from 'react';
import { render, fireEvent, waitFor, act } from '@testing-library/react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import FacilityModal from '@/components/modal/FacilityModal';
import { CategoriesMap } from '@/constants/CategoriesMap';
import { SlugMap } from '@/constants/SlugMap';
import { NavigationContainer } from '@react-navigation/native';

jest.mock('react-native-modal', () => ({
  __esModule: true,
  default: jest.fn(({ children }) => <>{children}</>), // Ensures children render
}));

jest.mock('react-native-paper', () => ({
  __esModule: true,
  ActivityIndicator: jest.fn(() => <div data-testid="loading-indicator" />),
  Button: jest.fn(({ children, onPress }) => (
      <button data-testid={"close-button"} onClick={onPress}>{children}</button>
    )),
}));

jest.mock('@react-native-async-storage/async-storage', () => ({
  getItem: jest.fn(() => Promise.resolve(null)),
  setItem: jest.fn(() => Promise.resolve()),
  removeItem: jest.fn(() => Promise.resolve()),
}));

// Mock child components to simplify testing
jest.mock('@/components/modal/MenuComponent', () => 'MenuComponent');
jest.mock('@/components/modal/CapacityComponent', () => 'CapacityComponent');
jest.mock('@/components/modal/DateFormatter', () => 'DateFormatter');
jest.mock('@/components/modal/OperatingHoursComponent', () => 'OperatingHoursComponent');
jest.mock('@/components/modal/GymOperatingHoursComponent', () => 'GymOperatingHoursComponent');
jest.mock('@/components/modal/GymZonesComponent', () => 'GymZonesComponent');
jest.mock('@/components/modal/LibraryReservationComponent', () => 'LibraryReservationComponent');
jest.mock('@/components/modal/FeastMenuComponent', () => 'FeastMenuComponent');
jest.mock('@/components/modal/FeastMenuComponent', () => 'FeastMenuComponent');

global.fetch = jest.fn();

describe('FacilityModal', () => {
  const mockOnClose = jest.fn();
  const mockFacility = 'Test Facility';

  const mockFacilityData = {
    data: {
      occupants: 50,
      capacity: 100,
      last_updated: '2024-03-04T12:00:00Z',
      menu: { section1: ['item1', 'item2'] },
      hours_today: '9:00 AM - 5:00 PM',
      zones: [{ name: 'Zone A', occupancy: 30 }],
      regular_hours: 'Regular Hours',
      special_hours: 'Special Hours',
    }
  };

  // Wrapper to provide SafeAreaProvider
  const renderComponent = (props = {}) => render(
    <NavigationContainer>
      <SafeAreaProvider initialSafeAreaInsets={{ top: 0, bottom: 0, left: 0, right: 0 }}>
          <FacilityModal visible={true} onClose={mockOnClose} facility={mockFacility} {...props} />
      </SafeAreaProvider>
      </NavigationContainer>
  );

  beforeEach(() => {
    jest.restoreAllMocks();
    jest.clearAllMocks();
    (fetch as jest.Mock).mockResolvedValue({
      ok: true,
      text: jest.fn().mockResolvedValue(JSON.stringify(mockFacilityData)),
      json: jest.fn().mockResolvedValue(mockFacilityData),
    });

    jest.spyOn(CategoriesMap, 'entries').mockReturnValue(new Map([
      ['dining', new Map([['Test Facility', mockFacility]])],
      ['gym', new Map([['BFit', 'BFit']])]
    ]).entries());

    jest.spyOn(SlugMap, 'get').mockImplementation((key) => {
      const mockSlugMap = new Map([
        ["Test Facility", "test-facility"],
        ["BFit", "BFit"],
        ["Wooden", "john-wooden-center"]
      ]);
      return mockSlugMap.get(key);
    });
    jest.spyOn(React, 'useState').mockRestore();
  });

  it('renders nothing when not visible', () => {
    const { queryByText } = render(
      <SafeAreaProvider initialSafeAreaInsets={{ top: 0, bottom: 0, left: 0, right: 0 }}>
        <FacilityModal
          visible={false}
          onClose={mockOnClose}
          facility={null}
        />
      </SafeAreaProvider>
    );

    expect(queryByText(mockFacility)).toBeNull();
  });

  it('shows loading indicator when fetching data', async () => {
    (fetch as jest.Mock).mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve({ json: () => Promise.resolve(mockFacilityData) }), 500))
    );

    const { getByTestId } = renderComponent();

    await waitFor(() => {
      expect(getByTestId('loading-indicator')).toBeTruthy();
    }, { timeout: 1000 }); // make sure we wait so we can see loading indicator
  });

  it('fetches facility data successfully', async () => {
    const { getByText } = renderComponent({ visible: true, facility: mockFacility });
  
    await waitFor(() => {
      expect(getByText(mockFacility)).toBeTruthy();
    });

    expect(fetch).toHaveBeenCalled();
  });

  it('handles fetch error gracefully', async () => {
    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();

    (fetch as jest.Mock).mockRejectedValue(new Error('Fetch failed'));

    renderComponent();

    await waitFor(() => {
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        'Error fetching facility data:',
        expect.any(Error)
      );
    });

    consoleErrorSpy.mockRestore();
  });

  it('closes modal when close button is pressed', async () => {

    const { getByText } = renderComponent({ visible: true, facility: mockFacility });
  
    await waitFor(() => {
      const closeButton = getByText('Close');
      fireEvent.press(closeButton);
    });

    expect(mockOnClose).toHaveBeenCalled();
  });

  it('displays correct category-specific information', async () => {
    (fetch as jest.Mock).mockResolvedValue({
      ok: true,
      text: jest.fn().mockResolvedValue(JSON.stringify({
        data: {
          occupants: 50,
          capacity: 100,
          last_updated: '2024-03-04T12:00:00Z',
          menu: { section1: ['item1', 'item2'] },
          hours_today: '9:00 AM - 5:00 PM',
          regular_hours: 'Regular Hours',
          special_hours: 'Special Hours',
          zones: [{ name: 'Cardio Zone', occupancy: 20 }]
        }
      })),
      json: jest.fn().mockResolvedValue({
        data: {
          occupants: 50,
          capacity: 100,
          last_updated: '2024-03-04T12:00:00Z',
          menu: { section1: ['item1', 'item2'] },
          hours_today: '9:00 AM - 5:00 PM',
          regular_hours: 'Regular Hours',
          special_hours: 'Special Hours',
          zones: [{ name: 'Cardio Zone', occupancy: 20 }]
        }
      })
    });    

    const { getByText } = renderComponent({ facility: 'BFit' });

    await waitFor(() => {
      expect(getByText('Last updated:')).toBeTruthy();
    });
  });

  it('does not crash when no facility data is available', async () => {
    (fetch as jest.Mock).mockResolvedValue({
      json: () => Promise.resolve(null)
    });

    const { queryByText } = renderComponent();

    await waitFor(() => {
      expect(queryByText('Historical Capacity')).toBeNull();
    });
  });

  it('ensures fetch is called with correct URL based on category', async () => {
    (fetch as jest.Mock).mockResolvedValue({
      json: () => Promise.resolve(mockFacilityData)
    });

    renderComponent();

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining(`dining/${SlugMap.get(mockFacility)}`)
      );
    });
  });
});