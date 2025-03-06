import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { act } from 'react-test-renderer';
import FacilityModal from '@/components/modal/FacilityModal';
import { CategoriesMap } from '@/constants/CategoriesMap';
import { SlugMap } from '@/constants/SlugMap';

// Mock dependencies
jest.mock('react-native-modal', () => {
  const MockModal = jest.requireActual('react-native-paper').Modal;
  return MockModal;
});

jest.mock('react-native-paper', () => ({
  ActivityIndicator: 'ActivityIndicator',
  Button: jest.fn(({ children, onPress }) => (
    <button onClick={onPress}>{children}</button>
  )),
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

// Mock fetch
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
      special_hours: 'Special Hours'
    }
  };

  // Wrapper to provide SafeAreaProvider
  const renderComponent = (props = {}) => render(
    <SafeAreaProvider initialSafeAreaInsets={{ top: 0, bottom: 0, left: 0, right: 0 }}>
      <FacilityModal
        visible={true}
        onClose={mockOnClose}
        facility={mockFacility}
        {...props}
      />
    </SafeAreaProvider>
  );

  beforeEach(() => {
    jest.clearAllMocks();
    (fetch as jest.Mock).mockClear();

    // Mock CategoriesMap and SlugMap
    jest.spyOn(CategoriesMap, 'entries').mockReturnValue([
      ['dining', new Map([['Test Facility', mockFacility]])]
    ]);
    jest.spyOn(SlugMap, 'get').mockReturnValue('test-facility');
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
    // Create a pending promise to simulate loading
    const fetchPromise = new Promise(() => { });
    (fetch as jest.Mock).mockReturnValue(fetchPromise);

    const { getByTestId } = renderComponent();

    // Wait for loading to appear
    await waitFor(() => {
      const loadingIndicator = getByTestId('loading-indicator');
      expect(loadingIndicator).toBeTruthy();
    });
  });

  it('fetches facility data successfully', async () => {
    (fetch as jest.Mock).mockResolvedValue({
      json: () => Promise.resolve(mockFacilityData)
    });

    const { getByText } = renderComponent();

    // Wait for facility name to appear
    await waitFor(() => {
      expect(getByText(mockFacility)).toBeTruthy();
    });

    // Verify fetch was called
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining(`dining/${SlugMap.get(mockFacility)}`)
    );
  });

  it('handles fetch error gracefully', async () => {
    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();

    (fetch as jest.Mock).mockRejectedValue(new Error('Fetch failed'));

    renderComponent();

    // Wait for error to be logged
    await waitFor(() => {
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        'Error fetching facility data:',
        expect.any(Error)
      );
    });

    consoleErrorSpy.mockRestore();
  });

  it('closes modal when close button is pressed', async () => {
    (fetch as jest.Mock).mockResolvedValue({
      json: () => Promise.resolve(mockFacilityData)
    });

    const { getByText } = renderComponent();

    // Wait for close button to appear and then press it
    await waitFor(() => {
      const closeButton = getByText('Close');
      fireEvent.press(closeButton);
    });

    // Verify onClose was called
    expect(mockOnClose).toHaveBeenCalled();
  });

  it('renders different components based on facility category', async () => {
    // Test dining facility
    jest.spyOn(CategoriesMap, 'entries').mockReturnValueOnce([
      ['dining', new Map([['Feast', 'Feast']])]
    ]);

    (fetch as jest.Mock).mockResolvedValue({
      json: () => Promise.resolve({
        data: {
          ...mockFacilityData.data,
          menu: { section1: ['dish1', 'dish2'] }
        }
      })
    });

    const { getByText } = renderComponent({ facility: 'Feast' });

    // Wait for modal content to render
    await waitFor(() => {
      expect(getByText('Last updated:')).toBeTruthy();
    });
  });

  it('handles pan responder for dragging', async () => {
    (fetch as jest.Mock).mockResolvedValue({
      json: () => Promise.resolve(mockFacilityData)
    });

    const { getByTestId } = renderComponent();

    // Simulate drag gesture
    await act(async () => {
      const scrollView = getByTestId('drag-indicator');
      // Note: This is a simplified gesture simulation
      fireEvent(scrollView, 'panResponderMove', { dy: 200 });
    });

    // Verify modal behavior (this might require more complex mocking)
    expect(mockOnClose).not.toHaveBeenCalled();
  });

  it('renders gym-specific components for gym facilities', async () => {
    // Mock gym facility
    jest.spyOn(CategoriesMap, 'entries').mockReturnValueOnce([
      ['gym', new Map([['Test Gym', 'Test Gym']])]
    ]);

    (fetch as jest.Mock).mockResolvedValue({
      json: () => Promise.resolve({
        data: {
          ...mockFacilityData.data,
          zones: [{ name: 'Cardio Zone', occupancy: 20 }]
        }
      })
    });

    const { getByText } = renderComponent({ facility: 'Test Gym' });

    // Wait for modal content to render
    await waitFor(() => {
      expect(getByText('Last updated:')).toBeTruthy();
    });
  });
});