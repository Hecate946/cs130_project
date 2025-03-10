import MaterialCommunityIcons from "react-native-vector-icons/MaterialCommunityIcons";
import React, { useState, useEffect, useCallback } from "react";
import { TouchableOpacity } from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { useFocusEffect } from "@react-navigation/native";
import * as Haptics from "expo-haptics";
import { SlugMap } from "@/constants/SlugMap";
import { Categories } from "@/constants/Categories";
import { EXPO_API_URL } from "@/constants/ApiUrls";

interface NotificationBellProps {
  facilityId: number;
  facilityName: string;
}

interface NotificationPreference {
  enabled: boolean;
  threshold: number;
}

export default function NotificationBell({ facilityId, facilityName }: NotificationBellProps) {
  const [hasNotifications, setHasNotifications] = useState(false);
  const [expoPushToken, setExpoPushToken] = useState<string>('');

  // Load push token on mount
  useEffect(() => {
    const loadToken = async () => {
      const token = await AsyncStorage.getItem('expoPushToken');
      if (token) {
        setExpoPushToken(token);
      }
    };
    loadToken();
  }, []);

  const checkNotifications = async () => {
    try {
      const storedValue = await AsyncStorage.getItem(`notification_${facilityId}`);
      if (storedValue) {
        const prefs = JSON.parse(storedValue) as NotificationPreference;
        setHasNotifications(prefs.enabled);
      } else {
        // Initialize with disabled preferences
        const defaultPrefs: NotificationPreference = {
          enabled: false,
          threshold: 50
        };
        await AsyncStorage.setItem(`notification_${facilityId}`, JSON.stringify(defaultPrefs));
        setHasNotifications(false);
      }
    } catch (error) {
      setHasNotifications(false);
    }
  };

  useEffect(() => {
    checkNotifications();
  }, []);

  useFocusEffect(
    useCallback(() => {
      checkNotifications();
    }, [facilityId])
  );

  const syncWithBackend = async (prefs: NotificationPreference) => {
    if (!expoPushToken) return;

    try {
      // Get all current preferences from AsyncStorage
      const keys = await AsyncStorage.getAllKeys();
      const notificationKeys = keys.filter(key => key.startsWith('notification_'));
      const preferences: { [key: string]: any } = {};
      
      for (const key of notificationKeys) {
        const value = await AsyncStorage.getItem(key);
        if (value) {
          preferences[key] = JSON.parse(value);
        }
      }
      
      // Convert to backend format
      const capacityPreferences: { [key: string]: any } = {};
      for (const [key, value] of Object.entries(preferences)) {
        const id = key.replace('notification_', '');
        const name = [...Categories.diningHalls, ...Categories.takeout, ...Categories.gym, ...Categories.libraries]
          .find(item => item.key === id)?.name;
        
        if (name) {
          const slug = SlugMap.get(name);
          if (slug) {
            capacityPreferences[slug] = {
              enabled: value.enabled,
              threshold: value.threshold
            };
          }
        }
      }

      // Send to backend
      const response = await fetch(`${EXPO_API_URL}:5001/api/v1/notifications/update-preferences`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          pushToken: expoPushToken,
          preferences: {
            capacity: capacityPreferences
          },
          is_active: true
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to sync preferences with backend');
      }
    } catch (error) {
      console.error("Error syncing with backend:", error);
    }
  };

  const toggleNotification = async () => {
    try {
      const newValue = !hasNotifications;
      setHasNotifications(newValue);
      
      const prefs: NotificationPreference = {
        enabled: newValue,
        threshold: 50
      };
      await AsyncStorage.setItem(`notification_${facilityId}`, JSON.stringify(prefs));
      await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);

      // Sync with backend
      await syncWithBackend(prefs);
    } catch (error) {
      console.error("Error updating notification status:", error);
    }
  };

  return (
    <TouchableOpacity onPress={toggleNotification} testID="notification-bell-button">
      <MaterialCommunityIcons
        name={hasNotifications ? "bell-check-outline" : "bell-off-outline"}
        size={32}
        color="black"
        testID="notification-bell-icon"
      />
    </TouchableOpacity>
  );
}