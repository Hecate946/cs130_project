import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { act } from 'react-test-renderer';
import NotificationsScreen from '@/app/NotificationsScreen';
import { Platform } from 'react-native';
import { Categories } from '@/constants/Categories';
import { Colors } from '@/constants/Colors';
import { SlugMap } from '@/constants/SlugMap';
import { EXPO_API_URL } from '@/constants/ApiUrls';

// Mock dependencies
jest.mock('expo-router', () => ({
  useRouter: () => ({
    back: jest.fn(),
  }),
}));

// Mock AsyncStorage
jest.mock('@react-native-async-storage/async-storage', () => ({
  getItem: jest.fn(),
  setItem: jest.fn(),
  getAllKeys: jest.fn(),
}));

// Mock Haptics
jest.mock('expo-haptics', () => ({
  impactAsync: jest.fn(),
  ImpactFeedbackStyle: {
    Light: 'light',
    Medium: 'medium',
    Heavy: 'heavy',
  },
}));

// Mock Notifications
jest.mock('expo-notifications', () => ({
  setNotificationChannelAsync: jest.fn(),
  getPermissionsAsync: jest.fn(),
  requestPermissionsAsync: jest.fn(),
  getExpoPushTokenAsync: jest.fn(),
  AndroidImportance: {
    MAX: 5,
  },
}));

// Mock Constants
jest.mock('expo-constants', () => ({
  expoConfig: {
    extra: {
      eas: {
        projectId: 'test-project-id',
      },
    },
  },
}));

// Mock fetch
global.fetch = jest.fn();

// Mock NotificationItem component
jest.mock('@/components/notifications/NotificationItem', () => {
  const MockNotificationItem = ({ name, id, onPreferenceChange }) => (
    <div data-testid={`notification-item-${id}`}>
      <button
        data-testid={`toggle-${id}`}
        onClick={() => onPreferenceChange(`slug-${id}`, true, 50)}
      >
        Toggle {name}
      </button>
    </div>
  );
  return MockNotificationItem;
});

// Mock Divider component
jest.mock('@/components/Divider', () => {
  const MockDivider = ({ name }) => <div data-testid={`divider-${name}`}>{name}</div>;
  return MockDivider;
});

// Mock react-native-paper components
jest.mock('react-native-paper', () => ({
  Button: ({ onPress, children }) => (
    <button data-testid="done-button" onClick={onPress}>
      {children}
    </button>
  ),
  Switch: ({ value, onValueChange }) => (
    <button data-testid="toggle-all-switch" onClick={() => onValueChange(!value)}>
      {value ? 'ON' : 'OFF'}
    </button>
  ),
}));

const AsyncStorage = require('@react-native-async-storage/async-storage');
const Haptics = require('expo-haptics');
const Notifications = require('expo-notifications');

describe('NotificationsScreen', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Default AsyncStorage mock implementations
    AsyncStorage.getItem.mockImplementation((key) => {
      if (key === 'expoPushToken') return Promise.resolve('mock-token');
      if (key === 'notifications_all_enabled') return Promise.resolve('false');
      return Promise.resolve(JSON.stringify({ enabled: false, threshold: 50 }));
    });
    
    AsyncStorage.getAllKeys.mockResolvedValue([
      'notification_dh1',
      'notification_to1',
      'notification_gym1',
      'notification_lib1',
    ]);
    
    AsyncStorage.setItem.mockResolvedValue(undefined);
    
    // Default Haptics mock implementations
    Haptics.impactAsync.mockResolvedValue(undefined);
    
    // Default Notifications mock implementations
    Notifications.getPermissionsAsync.mockResolvedValue({ status: 'granted' });
    Notifications.requestPermissionsAsync.mockResolvedValue({ status: 'granted' });
    Notifications.getExpoPushTokenAsync.mockResolvedValue({ data: 'new-token' });
    Notifications.setNotificationChannelAsync.mockResolvedValue(undefined);
    
    // Default fetch mock implementation
    global.fetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ is_active: false }),
    });
  });

  it('renders correctly with notifications disabled', async () => {
    AsyncStorage.getItem.mockImplementation((key) => {
      if (key === 'notifications_all_enabled') return Promise.resolve('false');
      return Promise.resolve(null);
    });

    const component = render(<NotificationsScreen onFinish={jest.fn()} />);

    await waitFor(() => {
      expect(component.getByText('Notifications')).toBeTruthy();
      expect(component.getByText('Enable All Notifications')).toBeTruthy();
      
      // When allEnabled is false, category sections should not be visible
      expect(component.queryByTestId('divider-Restaurants')).toBeNull();
    });
  });

  it('loads push token and preferences on mount', async () => {
    const component = render(<NotificationsScreen onFinish={jest.fn()} />);
    
    expect(AsyncStorage.getItem).toHaveBeenCalledWith('expoPushToken');
    expect(AsyncStorage.getItem).toHaveBeenCalledWith('notifications_all_enabled');
    expect(global.fetch).toHaveBeenCalled();
  });

  it('handles toggle all notifications', async () => {
    const component = render(<NotificationsScreen onFinish={jest.fn()} />);

    
    await act(async () => {
      fireEvent.click(component.getByTestId('toggle-all-switch'));
    });
    
    expect(AsyncStorage.setItem).toHaveBeenCalledWith('notifications_all_enabled', 'true');
    expect(Haptics.impactAsync).toHaveBeenCalledWith(Haptics.ImpactFeedbackStyle.Light);
    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:5001/api/v1/notifications/update-preferences',
      expect.objectContaining({
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      })
    );
  });

  it('registers for push notifications when token is not available', async () => {
    AsyncStorage.getItem.mockImplementation((key) => {
      if (key === 'expoPushToken') return Promise.resolve(null);
      return Promise.resolve(null);
    });
    
    let component;
    await act(async () => {
      component = render(<NotificationsScreen onFinish={jest.fn()} />);
    });
    
    await act(async () => {
      fireEvent.click(component.getByTestId('toggle-all-switch'));
    });
    
    expect(Notifications.getPermissionsAsync).toHaveBeenCalled();
    expect(Notifications.getExpoPushTokenAsync).toHaveBeenCalled();
    expect(AsyncStorage.setItem).toHaveBeenCalledWith('expoPushToken', 'new-token');
    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:5001/api/v1/notifications/register',
      expect.anything()
    );
  });

  it('requests permissions if not already granted', async () => {
    AsyncStorage.getItem.mockImplementation((key) => {
      if (key === 'expoPushToken') return Promise.resolve(null);
      return Promise.resolve(null);
    });
    
    Notifications.getPermissionsAsync.mockResolvedValue({ status: 'undetermined' });
    
    let component;
    await act(async () => {
      component = render(<NotificationsScreen onFinish={jest.fn()} />);
    });
    
    await act(async () => {
      fireEvent.click(component.getByTestId('toggle-all-switch'));
    });
    
    expect(Notifications.getPermissionsAsync).toHaveBeenCalled();
    expect(Notifications.requestPermissionsAsync).toHaveBeenCalled();
  });

  it('does not proceed if permissions are denied', async () => {
    AsyncStorage.getItem.mockImplementation((key) => {
      if (key === 'expoPushToken') return Promise.resolve(null);
      return Promise.resolve(null);
    });
    
    Notifications.getPermissionsAsync.mockResolvedValue({ status: 'undetermined' });
    Notifications.requestPermissionsAsync.mockResolvedValue({ status: 'denied' });
    
    let component;
    await act(async () => {
      component = render(<NotificationsScreen onFinish={jest.fn()} />);
    });
    
    await act(async () => {
      fireEvent.click(component.getByTestId('toggle-all-switch'));
    });
    
    expect(Notifications.requestPermissionsAsync).toHaveBeenCalled();
    expect(Notifications.getExpoPushTokenAsync).not.toHaveBeenCalled();
  });

  it('creates notification channel on Android', async () => {
    const originalPlatform = Platform.OS;
    Platform.OS = 'android';
    
    AsyncStorage.getItem.mockImplementation((key) => {
      if (key === 'expoPushToken') return Promise.resolve(null);
      return Promise.resolve(null);
    });
    
    let component;
    await act(async () => {
      component = render(<NotificationsScreen onFinish={jest.fn()} />);
    });
    
    await act(async () => {
      fireEvent.click(component.getByTestId('toggle-all-switch'));
    });
    
    expect(Notifications.setNotificationChannelAsync).toHaveBeenCalledWith('default', expect.anything());
    
    // Restore original platform
    Platform.OS = originalPlatform;
  });

  it('handles preference change for a facility', async () => {
    AsyncStorage.getItem.mockImplementation((key) => {
      if (key === 'expoPushToken') return Promise.resolve('mock-token');
      if (key === 'notifications_all_enabled') return Promise.resolve('true');
      return Promise.resolve(JSON.stringify({ enabled: false, threshold: 50 }));
    });
    
    let component;
    await act(async () => {
      component = render(<NotificationsScreen onFinish={jest.fn()} />);
    });
    
    await act(async () => {
      fireEvent.click(component.getByTestId('toggle-dh1'));
    });
    
    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:5001/api/v1/notifications/update-preferences',
      expect.objectContaining({
        method: 'POST',
      })
    );
  });

  it('handles API error during preference update', async () => {
    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();
    
    global.fetch.mockResolvedValue({
      ok: false,
      json: () => Promise.resolve({ error: 'API error' }),
    });
    
    let component;
    await act(async () => {
      component = render(<NotificationsScreen onFinish={jest.fn()} />);
    });
    
    await act(async () => {
      fireEvent.click(component.getByTestId('toggle-all-switch'));
    });
    
    expect(consoleErrorSpy).toHaveBeenCalled();
    consoleErrorSpy.mockRestore();
  });

  it('handles finish button press', async () => {
    const onFinishMock = jest.fn();
    const routerBackMock = jest.fn();
    
    jest.spyOn(require('expo-router'), 'useRouter').mockReturnValue({
      back: routerBackMock,
    });
    
    let component;
    await act(async () => {
      component = render(<NotificationsScreen onFinish={onFinishMock} />);
    });
    
    await act(async () => {
      fireEvent.click(component.getByTestId('done-button'));
    });
    
    expect(Haptics.impactAsync).toHaveBeenCalledWith(Haptics.ImpactFeedbackStyle.Heavy);
    expect(routerBackMock).toHaveBeenCalled();
    expect(onFinishMock).toHaveBeenCalled();
  });

  it('registers for push notifications when a preference is changed without token', async () => {
    AsyncStorage.getItem.mockImplementation((key) => {
      if (key === 'expoPushToken') return Promise.resolve(null);
      if (key === 'notifications_all_enabled') return Promise.resolve('true');
      return Promise.resolve(JSON.stringify({ enabled: false, threshold: 50 }));
    });
    
    let component;
    await act(async () => {
      component = render(<NotificationsScreen onFinish={jest.fn()} />);
    });
    
    await act(async () => {
      fireEvent.click(component.getByTestId('toggle-dh1'));
    });
    
    expect(Notifications.getPermissionsAsync).toHaveBeenCalled();
    expect(Notifications.getExpoPushTokenAsync).toHaveBeenCalled();
  });

  it('handles errors during token and sync loading', async () => {
    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();
    
    AsyncStorage.getItem.mockRejectedValue(new Error('AsyncStorage error'));
    
    await act(async () => {
      render(<NotificationsScreen onFinish={jest.fn()} />);
    });
    
    expect(consoleErrorSpy).toHaveBeenCalledWith('Error in loadTokenAndSync:', expect.any(Error));
    consoleErrorSpy.mockRestore();
  });

  it('handles errors during preference change', async () => {
    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();
    
    global.fetch.mockRejectedValue(new Error('Fetch error'));
    
    let component;
    await act(async () => {
      component = render(<NotificationsScreen onFinish={jest.fn()} />);
    });
    
    await act(async () => {
      fireEvent.click(component.getByTestId('toggle-dh1'));
    });
    
    expect(consoleErrorSpy).toHaveBeenCalledWith('Error in handlePreferenceChange:', expect.any(Error));
    consoleErrorSpy.mockRestore();
  });
});