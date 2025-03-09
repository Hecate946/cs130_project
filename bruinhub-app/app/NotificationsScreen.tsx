import React from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import { Link, useRouter } from "expo-router";
import { Colors } from "@/constants/Colors";
import { Button, Switch } from "react-native-paper";
import * as Haptics from "expo-haptics";
import * as Notifications from 'expo-notifications';
import Constants from 'expo-constants';
import { Platform } from 'react-native';
import { Categories } from "@/constants/Categories";
import { SlugMap } from "@/constants/SlugMap";
import NotificationItem from "@/components/notifications/NotificationItem";
import Divider from "@/components/Divider";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { useState, useEffect } from "react";

const Restaurants = Categories.diningHalls;
const Takeout = Categories.takeout;
const Gyms = Categories.gym;
const Libraries = Categories.libraries;

interface NotificationsScreenProps {
  onFinish: () => void;
}

export default function NotificationsScreen({ onFinish }: NotificationsScreenProps) {
  const router = useRouter();
  const [expoPushToken, setExpoPushToken] = useState<string>('');
  const [allEnabled, setAllEnabled] = useState(false);

  // Load push token and sync with backend on mount
  useEffect(() => {
    const loadTokenAndSync = async () => {
      try {
        // Load push token
        const token = await AsyncStorage.getItem('expoPushToken');
        if (token) {
          setExpoPushToken(token);
        }

        // Load allEnabled state
        const allEnabledValue = await AsyncStorage.getItem('notifications_all_enabled');
        if (allEnabledValue !== null) {
          const parsedValue = JSON.parse(allEnabledValue);
          setAllEnabled(parsedValue);
          
          // Only sync with backend if we have a token, but don't update local state
          if (token) {
            await syncPreferencesWithBackend(token, parsedValue);
          }
        }
      } catch (error) {
        console.error('Error in loadTokenAndSync:', error);
      }
    };
    loadTokenAndSync();
  }, []);

  const registerForPushNotifications = async () => {
    try {
      let token;
      
      if (Platform.OS === 'android') {
        await Notifications.setNotificationChannelAsync('default', {
          name: 'default',
          importance: Notifications.AndroidImportance.MAX,
          vibrationPattern: [0, 250, 250, 250],
          lightColor: '#FF231F7C',
        });
      }
      
      const { status: existingStatus } = await Notifications.getPermissionsAsync();
      let finalStatus = existingStatus;
      
      if (existingStatus !== 'granted') {
        const { status } = await Notifications.requestPermissionsAsync();
        finalStatus = status;
      }
      
      if (finalStatus !== 'granted') {
        return;
      }
      
      token = await Notifications.getExpoPushTokenAsync({
        projectId: Constants.expoConfig?.extra?.eas?.projectId,
      });
      
      setExpoPushToken(token.data);
      await AsyncStorage.setItem('expoPushToken', token.data);
      
      // Register with backend
      await registerWithBackend(token.data);
      
    } catch (error) {
      console.error('Error getting push token:', error);
    }
  };

  const registerWithBackend = async (token: string) => {
    try {
      // Initialize all facilities with disabled preferences
      const facilities = [...Restaurants, ...Takeout, ...Gyms, ...Libraries];
      const capacityPreferences: { [key: string]: any } = {};
      
      for (const facility of facilities) {
        const slug = SlugMap.get(facility.name);
        if (slug) {
          capacityPreferences[slug] = {
            enabled: false,
            threshold: 50
          };
        }
      }

      const response = await fetch('http://192.168.216.35:5001/api/v1/notifications/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          pushToken: token,
          deviceType: Platform.OS,
          preferences: {
            capacity: capacityPreferences
          },
          is_active: true
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to register with backend');
      }
      
      const data = await response.json();
      setAllEnabled(data.is_active);

      // Also initialize AsyncStorage with disabled preferences
      for (const facility of facilities) {
        await AsyncStorage.setItem(`notification_${facility.key}`, JSON.stringify({
          enabled: false,
          threshold: 50
        }));
      }
      
    } catch (error) {
      console.error('Error registering with backend:', error);
    }
  };

  const syncPreferencesWithBackend = async (token: string, currentAllEnabled: boolean) => {
    try {
      // Get all notification preferences from AsyncStorage
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
        const name = [...Restaurants, ...Takeout, ...Gyms, ...Libraries]
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

      const requestPayload = {
        pushToken: token,
        preferences: {
          capacity: capacityPreferences
        },
        is_active: currentAllEnabled  // Use the current local state
      };

      // Send to backend
      const response = await fetch('http://192.168.216.35:5001/api/v1/notifications/update-preferences', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestPayload),
      });
      
      const responseData = await response.json();
      
      if (!response.ok) {
        throw new Error(`Failed to sync preferences with backend: ${responseData.error || 'Unknown error'}`);
      }
      
    } catch (error) {
      console.error('Error syncing preferences with backend:', error);
      if (error instanceof Error) {
        console.error('Error details:', error.message);
      }
      throw error;
    }
  };

  const handlePreferenceChange = async (slug: string, enabled: boolean, threshold: number) => {
    try {
      if (!expoPushToken) {
        await registerForPushNotifications();
        return;
      }

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
        const name = [...Restaurants, ...Takeout, ...Gyms, ...Libraries]
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
      const requestPayload = {
        pushToken: expoPushToken,
        preferences: {
          capacity: capacityPreferences
        },
        is_active: allEnabled
      };
      
      const response = await fetch('http://192.168.216.35:5001/api/v1/notifications/update-preferences', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestPayload),
      });
      
      if (!response.ok) {
        const responseData = await response.json();
        throw new Error(`Failed to sync preferences with backend: ${responseData.error || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error in handlePreferenceChange:', error);
    }
  };

  const handleToggleAll = async () => {
    const newValue = !allEnabled;
    setAllEnabled(newValue);
    
    // Store the new value in AsyncStorage
    await AsyncStorage.setItem('notifications_all_enabled', JSON.stringify(newValue));
    
    await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    
    if (!expoPushToken) {
      await registerForPushNotifications();
    } else {
      // Get current preferences from AsyncStorage
      const keys = await AsyncStorage.getAllKeys();
      const notificationKeys = keys.filter(key => key.startsWith('notification_'));
      const preferences: { [key: string]: any } = {};
      
      for (const key of notificationKeys) {
        const value = await AsyncStorage.getItem(key);
        if (value) {
          preferences[key] = JSON.parse(value);
        }
      }
      
      // Convert to backend format while preserving existing preferences
      const capacityPreferences: { [key: string]: any } = {};
      for (const [key, value] of Object.entries(preferences)) {
        const id = key.replace('notification_', '');
        const name = [...Restaurants, ...Takeout, ...Gyms, ...Libraries]
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
      const requestPayload = {
        pushToken: expoPushToken,
        preferences: {
          capacity: capacityPreferences
        },
        is_active: newValue  // Only update the global toggle
      };
      
      const response = await fetch('http://192.168.216.35:5001/api/v1/notifications/update-preferences', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestPayload),
      });
      
      if (!response.ok) {
        const responseData = await response.json();
        throw new Error(`Failed to sync preferences with backend: ${responseData.error || 'Unknown error'}`);
      }
    }
  };

  const handleFinish = async () => {
    await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy);
    router.back();
    onFinish();
  };

  return (
    <View style={styles.container}>
      <ScrollView
        style={styles.scrollContainer}
        contentContainerStyle={styles.contentContainer}
      >
        <View style={styles.notificationsContainer}>
          <Text style={styles.title}>Notifications</Text>
          <Text style={styles.text}>Select the facilities you'd like to receive
            notifications for, including capacity updates and closing times.</Text>
          <View style={styles.toggleAllContainer}>
            <Text style={styles.toggleAllText}>Enable All Notifications</Text>
            <Switch
              value={allEnabled}
              onValueChange={handleToggleAll}
              color={Colors.light.tint}
            />
          </View>
        </View>

        {allEnabled && (
          <>
            <Divider name="Restaurants" />
            <View>
              {Restaurants.map((item) => (
                <NotificationItem 
                  name={item.name} 
                  key={item.key} 
                  id={item.key}
                  onPreferenceChange={handlePreferenceChange}
                />
              ))}
            </View>

            <Divider name="Takeout" />
            <View>
              {Takeout.map((item) => (
                <NotificationItem 
                  name={item.name} 
                  key={item.key} 
                  id={item.key}
                  onPreferenceChange={handlePreferenceChange}
                />
              ))}
            </View>

            <Divider name="Gyms" />
            <View>
              {Gyms.map((item) => (
                <NotificationItem 
                  name={item.name} 
                  key={item.key} 
                  id={item.key}
                  onPreferenceChange={handlePreferenceChange}
                />
              ))}
            </View>

            <Divider name="Libraries" />
            <View>
              {Libraries.map((item) => (
                <NotificationItem 
                  name={item.name} 
                  key={item.key} 
                  id={item.key}
                  onPreferenceChange={handlePreferenceChange}
                />
              ))}
            </View>
          </>
        )}

      </ScrollView>
      <View style={{ position: "absolute", bottom: 50 }}>
          <Button
            style={styles.button}
            onPress={handleFinish}
            uppercase={true}
            mode="elevated"
            labelStyle={styles.buttonLabel}
            contentStyle={styles.buttonContent}
          >
            Done
          </Button>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "flex-start",
    alignItems: "center",
    backgroundColor: Colors.light.background,
    width: "100%",
    paddingTop: 80,
  },

  scrollContainer: {
    flex: 1,
  },

  contentContainer: {
    flexGrow: 1,
    paddingBottom: 155,
    marginStart: 20,
    marginEnd: 20,
  },

  notificationsContainer: {
    backgroundColor: Colors.light.background,
    width: "100%",
    gap: 5,
  },

  title: {
    fontSize: 24,
    fontWeight: "400",
    textTransform: "uppercase",
  },

  text: {
    fontSize: 16,
    fontWeight: "300",
  },

  toggleAllContainer: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginTop: 16,
    padding: 16,
    backgroundColor: "white",
    borderRadius: 10,
  },

  toggleAllText: {
    fontSize: 16,
    fontWeight: "500",
  },

  button: {
    backgroundColor: Colors.light.icon,
    borderRadius: 60,
  },

  buttonLabel: {
    fontSize: 18,
    color: Colors.light.text,
    alignItems: "center",
  },

  buttonContent: {
    height: 64,
    width: 180,
    justifyContent: "center",
    alignItems: "center",
  },
});
