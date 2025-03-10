import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as Haptics from 'expo-haptics';
import { SlugMap } from '@/constants/SlugMap';
import { Categories } from '@/constants/Categories';
import { useFocusEffect } from '@react-navigation/native';
import NotificationBell from '@/components/NotificationBellComponent';

// Mock the dependencies
jest.mock('@react-native-async-storage/async-storage', () => ({
  getItem: jest.fn(),
  setItem: jest.fn(),
  getAllKeys: jest.fn(),
}));

jest.mock('expo-haptics', () => ({
  impactAsync: jest.fn(),
  ImpactFeedbackStyle: { Light: 'Light' },
}));

jest.mock('@react-navigation/native', () => ({
  useFocusEffect: jest.fn((callback) => callback()),
}));

// Mock the constants
jest.mock('@/constants/SlugMap', () => ({
  SlugMap: new Map([['Test Facility', 'test-facility']]),
}));

jest.mock('@/constants/Categories', () => ({
  Categories: {
    diningHalls: [{ key: '123', name: 'Test Facility' }],
    takeout: [],
    gym: [],
    libraries: [],
  },
}));

jest.mock('@/constants/ApiUrls', () => ({
  EXPO_API_URL: 'http://localhost',
}));

// Mock global fetch
global.fetch = jest.fn(() => 
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({ success: true }),
  }) as Promise<Response>
);

// Increase Jest timeout to handle async operations
jest.setTimeout(10000);

describe('NotificationBell Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders with notification off by default', async () => {
    (AsyncStorage.getItem as jest.Mock).mockResolvedValue(null);

    const { getByTestId } = render(
      <NotificationBell facilityId={123} facilityName="Test Facility" />
    );

    await waitFor(() => {
      expect(AsyncStorage.getItem).toHaveBeenCalledWith('notification_123');
    });
    
    await waitFor(() => {
      expect(AsyncStorage.setItem).toHaveBeenCalledWith(
        'notification_123',
        JSON.stringify({ enabled: false, threshold: 50 })
      );
    });
    
    await waitFor(() => {
      const bellIcon = getByTestId('notification-bell-icon');
      expect(bellIcon.props.name).toBe('bell-off-outline');
    });
  });

  it('renders with notification on when stored as enabled', async () => {
    (AsyncStorage.getItem as jest.Mock).mockImplementation((key) => {
      if (key === 'notification_123') {
        return Promise.resolve(JSON.stringify({ enabled: true, threshold: 50 }));
      }
      return Promise.resolve(null);
    });

    const { getByTestId } = render(
      <NotificationBell facilityId={123} facilityName="Test Facility" />
    );

    await waitFor(() => {
      const bellIcon = getByTestId('notification-bell-icon');
      expect(bellIcon.props.name).toBe('bell-check-outline');
    });
  });

  it('toggles notification state when pressed', async () => {
    // Start with notifications off
    (AsyncStorage.getItem as jest.Mock).mockImplementation((key) => {
      if (key === 'notification_123') {
        return Promise.resolve(JSON.stringify({ enabled: false, threshold: 50 }));
      }
      if (key === 'expoPushToken') {
        return Promise.resolve('mock-expo-token');
      }
      return Promise.resolve(null);
    });

    const { getByTestId } = render(
      <NotificationBell facilityId={123} facilityName="Test Facility" />
    );

    // Verify initial state
    await waitFor(() => {
      const bellIcon = getByTestId('notification-bell-icon');
      expect(bellIcon.props.name).toBe('bell-off-outline');
    });

    // Trigger the press event
    fireEvent.press(getByTestId('notification-bell-button'));

    // Verify the state changes and AsyncStorage is updated
    await waitFor(() => {
      expect(AsyncStorage.setItem).toHaveBeenCalledWith(
        'notification_123',
        JSON.stringify({ enabled: true, threshold: 50 })
      );
    });
    
    await waitFor(() => {
      expect(Haptics.impactAsync).toHaveBeenCalledWith(Haptics.ImpactFeedbackStyle.Light);
    });
    
    await waitFor(() => {
      const bellIcon = getByTestId('notification-bell-icon');
      expect(bellIcon.props.name).toBe('bell-check-outline');
    });
  });

  it('syncs with backend when toggling notifications', async () => {
    // Mock the AsyncStorage getItem for the push token and notification preference
    (AsyncStorage.getItem as jest.Mock).mockImplementation((key) => {
      if (key === 'expoPushToken') {
        return Promise.resolve('mock-expo-token');
      }
      if (key === 'notification_123') {
        return Promise.resolve(JSON.stringify({ enabled: false, threshold: 50 }));
      }
      return Promise.resolve(null);
    });

    // Mock the AsyncStorage getAllKeys for the backend sync
    (AsyncStorage.getAllKeys as jest.Mock).mockResolvedValue(['notification_123']);

    const { getByTestId } = render(
      <NotificationBell facilityId={123} facilityName="Test Facility" />
    );

    // Toggle notifications
    fireEvent.press(getByTestId('notification-bell-button'));

    // Verify backend sync is called with correct parameters
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('http://localhost'),
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: expect.any(String),
        })
      );
    });

    await waitFor(() => {
      // Parse the request body to verify its contents
      const callArgs = (fetch as jest.Mock).mock.calls[0];
      const requestBody = JSON.parse(callArgs[1].body);
      
      expect(requestBody).toEqual({
        pushToken: 'mock-expo-token',
        preferences: {
          capacity: {
            'test-facility': {
              enabled: true,
              threshold: 50,
            },
          },
        },
        is_active: true,
      });
    });
  });

  it('reloads notification state on screen focus', async () => {
    // Mock implementation to track calls
    let focusCallback: Function;
    (useFocusEffect as jest.Mock).mockImplementation((callback) => {
      focusCallback = callback;
    });

    (AsyncStorage.getItem as jest.Mock).mockImplementation((key) => {
      if (key === 'notification_123') {
        return Promise.resolve(JSON.stringify({ enabled: false, threshold: 50 }));
      }
      return Promise.resolve(null);
    });

    render(<NotificationBell facilityId={123} facilityName="Test Facility" />);

    // Clear mocks to track new calls
    jest.clearAllMocks();
    
    // First mock that the notification is disabled
    (AsyncStorage.getItem as jest.Mock).mockResolvedValue(
      JSON.stringify({ enabled: false, threshold: 50 })
    );
    
    // Simulate screen focus
    focusCallback();
    
    await waitFor(() => {
      expect(AsyncStorage.getItem).toHaveBeenCalledWith('notification_123');
    });

    // Now mock that the notification is enabled
    (AsyncStorage.getItem as jest.Mock).mockResolvedValue(
      JSON.stringify({ enabled: true, threshold: 50 })
    );
    
    // Simulate screen focus again
    focusCallback();
    
    await waitFor(() => {
      expect(AsyncStorage.getItem).toHaveBeenCalledWith('notification_123');
    });
  });

  it('handles AsyncStorage errors gracefully', async () => {
    // Mock AsyncStorage to throw an error
    (AsyncStorage.getItem as jest.Mock).mockRejectedValue(new Error('Storage error'));
    
    const { getByTestId } = render(
      <NotificationBell facilityId={123} facilityName="Test Facility" />
    );

    // Should default to notifications off
    await waitFor(() => {
      const bellIcon = getByTestId('notification-bell-icon');
      expect(bellIcon.props.name).toBe('bell-off-outline');
    });
  });

  it('handles backend sync errors gracefully', async () => {
    // Mock AsyncStorage successful responses
    (AsyncStorage.getItem as jest.Mock).mockImplementation((key) => {
      if (key === 'expoPushToken') {
        return Promise.resolve('mock-expo-token');
      }
      if (key === 'notification_123') {
        return Promise.resolve(JSON.stringify({ enabled: false, threshold: 50 }));
      }
      return Promise.resolve(null);
    });
    (AsyncStorage.getAllKeys as jest.Mock).mockResolvedValue(['notification_123']);
    
    // Mock failed API response
    (global.fetch as jest.Mock).mockImplementationOnce(() => 
      Promise.reject(new Error('API error'))
    );
    
    // Spy on console.error
    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();
    
    const { getByTestId } = render(
      <NotificationBell facilityId={123} facilityName="Test Facility" />
    );

    // Toggle notifications
    fireEvent.press(getByTestId('notification-bell-button'));

    // Should still update local state even if backend sync fails
    await waitFor(() => {
      expect(AsyncStorage.setItem).toHaveBeenCalledWith(
        'notification_123',
        JSON.stringify({ enabled: true, threshold: 50 })
      );
    });
    
    await waitFor(() => {
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        'Error syncing with backend:',
        expect.any(Error)
      );
    });
    
    consoleErrorSpy.mockRestore();
  });
});