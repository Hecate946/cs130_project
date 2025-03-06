import MaterialCommunityIcons from "react-native-vector-icons/MaterialCommunityIcons";
import React, { useState, useEffect, useCallback } from "react";
import { TouchableOpacity } from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { useFocusEffect } from "@react-navigation/native";
import * as Haptics from "expo-haptics";

interface NotificationBellProps {
  facilityId: number;
}

export default function NotificationBell({ facilityId }: NotificationBellProps) {
  const [hasNotifications, setHasNotifications] = useState(false);

  const checkNotifications = async () => {
    try {
      const storedValue = await AsyncStorage.getItem(`notification_${facilityId}`);
      setHasNotifications(storedValue === "on");
    } catch (error) {
      console.error("Error checking notifications:", error);
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

  const toggleNotification = async () => {
    try {
      const newValue = !hasNotifications ? "on" : "off";
      setHasNotifications(!hasNotifications);
      await AsyncStorage.setItem(`notification_${facilityId}`, newValue);

      await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    } catch (error) {
      console.error("Error updating notification status:", error);
    }
  };

  return (
    <TouchableOpacity onPress={toggleNotification}>
      <MaterialCommunityIcons
        name={hasNotifications ? "bell-check-outline" : "bell-off-outline"}
        size={32}
        color="black"
      />
    </TouchableOpacity>
  );
}